# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Marek Zubrzycki (Klucznik MZ)
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

import core.sort_settings_logic as settings_module
from core.sort_batch_files import BatchFiles
from core.sort_batch_logic import BatchLogic, DestinationUnavailableError
from core.sort_image_metadata import read_image_metadata
from core.sort_session_logic import SortSessionLogic
from core.sort_session_store import SortSessionStore
from core.sort_settings_logic import LANGUAGES, SettingsLogic


class IsolatedSettingsTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(prefix="ayosort_test_")
        self.root = Path(self.temporary_directory.name)
        self.config_path = self.root / "settings" / "config.json"
        self.patches = (
            patch.object(SettingsLogic, "config_path", return_value=self.config_path),
            patch.object(SettingsLogic, "repository_config_path", return_value=self.root / "missing-repository.json"),
            patch.object(SettingsLogic, "legacy_config_path", return_value=self.root / "missing-legacy.json"),
        )
        for active_patch in self.patches:
            active_patch.start()
        settings_module._SETTINGS_CACHE = None
        settings_module._SETTINGS_CACHE_PATH = None

    def tearDown(self):
        for active_patch in reversed(self.patches):
            active_patch.stop()
        settings_module._SETTINGS_CACHE = None
        settings_module._SETTINGS_CACHE_PATH = None
        self.temporary_directory.cleanup()

    def configure(self, **overrides):
        settings = {
            "destination_folder": None,
            "language": "pl",
            "theme": "dark",
            "category_names": {"good": "", "mid": "", "bad": ""},
        }
        settings.update(overrides)
        SettingsLogic.save(settings)


class BatchLogicTests(IsolatedSettingsTestCase):
    def test_default_categories_are_distinct(self):
        self.configure()
        logic = BatchLogic()
        self.assertEqual(logic.categories, {"good": "SORT/Dobre", "mid": "SORT/Średnie", "bad": "SORT/Słabe"})

    def test_existing_file_is_not_overwritten_and_undo_preserves_it(self):
        source = self.root / "source"
        destination = self.root / "destination"
        source.mkdir()
        (source / "photo.png").write_bytes(b"new image")
        existing = destination / "SORT" / "Dobre" / "photo.png"
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b"original image")
        self.configure(category_names={"good": "Dobre", "mid": "Średnie", "bad": "Słabe"})

        logic = BatchLogic()
        self.assertTrue(logic.load_images_from_folder(str(source)))
        logic.initialize_sorting_structure(str(destination))
        self.assertTrue(logic.sort_current_image("good"))

        copied = destination / "SORT" / "Dobre" / "photo_1.png"
        self.assertEqual(existing.read_bytes(), b"original image")
        self.assertEqual(copied.read_bytes(), b"new image")
        self.assertTrue(logic.undo_last_sort())
        self.assertTrue(existing.exists())
        self.assertFalse(copied.exists())

    def test_undo_refuses_to_delete_a_modified_copy(self):
        source = self.root / "source"
        source.mkdir()
        (source / "photo.png").write_bytes(b"new image")
        self.configure()
        logic = BatchLogic()
        logic.load_images_from_folder(str(source))
        logic.sort_current_image("good")
        copied = source / "SORT" / "Dobre" / "photo.png"
        copied.write_bytes(b"user edit")
        with self.assertRaises(OSError):
            logic.undo_last_sort()
        self.assertEqual(copied.read_bytes(), b"user edit")
        self.assertTrue(logic.can_undo())

    def test_natural_filename_order(self):
        source = self.root / "source"
        source.mkdir()
        for name in ("page10.png", "page2.png", "page1.png", "10.png", "alpha.png"):
            (source / name).touch()
        self.configure()
        logic = BatchLogic()
        logic.load_images_from_folder(str(source))
        self.assertEqual(
            [path.name for path in logic.images],
            ["10.png", "alpha.png", "page1.png", "page2.png", "page10.png"],
        )

    def test_loading_does_not_create_sort_folders(self):
        source = self.root / "source"
        source.mkdir()
        (source / "photo.png").touch()
        self.configure()
        session = SortSessionLogic()
        self.assertTrue(session.load_folder(str(source)))
        self.assertFalse((source / "SORT").exists())

    def test_destination_info_shows_effective_sort_folder(self):
        source = self.root / "source"
        source.mkdir()
        (source / "photo.png").touch()
        self.configure()
        logic = BatchLogic()
        logic.load_images_from_folder(str(source))
        destination, fixed, categories, available = logic.destination_info()
        self.assertEqual(destination, str(source / "SORT"))
        self.assertFalse(fixed)
        self.assertTrue(available)
        self.assertEqual(categories, ["Dobre", "Średnie", "Słabe"])

    def test_destination_info_marks_configured_destination(self):
        destination_root = self.root / "destination"
        destination_root.mkdir()
        self.configure(destination_folder=str(destination_root))
        logic = BatchLogic()
        destination, fixed, _categories, available = logic.destination_info()
        self.assertEqual(destination, str(destination_root / "SORT"))
        self.assertTrue(fixed)
        self.assertTrue(available)

    def test_missing_configured_destination_never_falls_back_to_source(self):
        source = self.root / "source"
        source.mkdir()
        (source / "photo.png").write_bytes(b"image")
        missing_destination = self.root / "unmounted-usb"
        self.configure(destination_folder=str(missing_destination))
        logic = BatchLogic()
        logic.load_images_from_folder(str(source))
        destination, fixed, _categories, available = logic.destination_info()
        self.assertEqual(destination, str(missing_destination / "SORT"))
        self.assertTrue(fixed)
        self.assertFalse(available)
        with self.assertRaises(DestinationUnavailableError):
            logic.sort_current_image("good")
        self.assertFalse((source / "SORT").exists())

    def test_category_folder_names_are_frozen_for_loaded_session(self):
        source = self.root / "source"
        source.mkdir()
        (source / "photo.png").touch()
        self.configure(language="pl")
        logic = BatchLogic()
        logic.load_images_from_folder(str(source))
        SettingsLogic.set_language("en")
        logic.refresh_categories()
        self.assertEqual(logic.categories, {"good": "SORT/Dobre", "mid": "SORT/Średnie", "bad": "SORT/Słabe"})
        logic.load_images_from_folder(str(source))
        self.assertEqual(logic.categories, {"good": "SORT/Good", "mid": "SORT/Average", "bad": "SORT/Bad"})

    def test_interrupted_copy_leaves_no_normal_or_part_file(self):
        source = self.root / "source.png"
        destination = self.root / "output" / "photo.png"
        source.write_bytes(b"a" * 1024)

        def interrupted(_source, output, **_kwargs):
            output.write(b"partial")
            raise OSError("interrupted")

        with patch("core.sort_batch_files.shutil.copyfileobj", side_effect=interrupted):
            with self.assertRaises(OSError):
                BatchFiles.copy_image(source, destination)
        self.assertFalse(destination.exists())
        self.assertEqual(list(destination.parent.glob("*.part")), [])
        self.assertEqual(list(destination.parent.glob(".*.part")), [])

    def test_existing_persisted_destination_is_used(self):
        source = self.root / "source"
        destination = self.root / "destination"
        source.mkdir()
        destination.mkdir()
        (source / "photo.png").write_bytes(b"image")
        self.configure(destination_folder=str(destination))
        logic = BatchLogic()
        logic.load_images_from_folder(str(source))
        logic.sort_current_image("good")
        self.assertTrue((destination / "SORT" / "Dobre" / "photo.png").exists())

    def test_unsafe_and_duplicate_names_stay_safe_and_distinct(self):
        self.configure(category_names={"good": "..", "mid": "Same", "bad": "Same"})
        logic = BatchLogic()
        category_paths = list(logic.categories.values())
        self.assertNotIn("SORT/..", category_paths)
        self.assertEqual(len({path.casefold() for path in category_paths}), 3)


class SettingsLogicTests(IsolatedSettingsTestCase):
    def test_settings_are_validated_and_saved_atomically(self):
        SettingsLogic.save({"language": "invalid", "theme": "invalid", "category_names": "invalid"})
        loaded = SettingsLogic.load()
        self.assertEqual(loaded["language"], "pl")
        self.assertEqual(loaded["theme"], "dark")
        self.assertEqual(loaded["category_names"], {"good": "", "mid": "", "bad": ""})
        self.assertEqual(json.loads(self.config_path.read_text(encoding="utf-8")), loaded)
        self.assertEqual(list(self.config_path.parent.glob(".config-*.tmp")), [])

    def test_duplicate_category_names_are_rejected(self):
        self.configure()
        with self.assertRaises(ValueError):
            SettingsLogic.set_category_names({"good": "Same", "mid": "same", "bad": "Other"})

    def test_reading_existing_settings_does_not_rewrite_them(self):
        self.configure()
        settings_module._SETTINGS_CACHE = None
        settings_module._SETTINGS_CACHE_PATH = None
        with patch.object(SettingsLogic, "save", wraps=SettingsLogic.save) as save:
            self.assertEqual(SettingsLogic.get_language(), "pl")
            self.assertEqual(SettingsLogic.get_theme(), "dark")
        save.assert_not_called()

    def test_destination_panel_is_translated_in_every_language(self):
        keys = {
            "destination_title",
            "destination_open",
            "destination_fixed",
            "destination_source",
            "destination_pending",
            "destination_pending_hint",
        }
        english = SettingsLogic.get_translations("en")
        for _name, code, _flag in LANGUAGES:
            translated = SettingsLogic.get_translations(code)
            self.assertTrue(keys.issubset(translated), code)
            self.assertTrue(all(str(translated[key]).strip() for key in keys), code)
            if code != "en":
                for key in keys:
                    self.assertNotEqual(translated[key], english[key], f"{code}:{key}")

    def test_visible_viewer_controls_are_translated_in_every_language(self):
        keys = {
            "viewer_zoom_out_button",
            "viewer_zoom_in_button",
            "viewer_actual_size_button",
            "viewer_fit_button",
            "viewer_fullscreen_button",
            "viewer_compare_button",
        }
        english = SettingsLogic.get_translations("en")
        for _name, code, _flag in LANGUAGES:
            translated = SettingsLogic.get_translations(code)
            self.assertTrue(keys.issubset(translated), code)
            self.assertTrue(all(str(translated[key]).strip() for key in keys), code)
            if code != "en":
                for key in keys:
                    self.assertNotEqual(translated[key], english[key], f"{code}:{key}")


class PersistentSessionTests(IsolatedSettingsTestCase):
    def test_session_and_undo_history_survive_restart(self):
        source = self.root / "source"
        destination = self.root / "destination"
        source.mkdir()
        destination.mkdir()
        (source / "one.png").write_bytes(b"one")
        (source / "two.png").write_bytes(b"two")
        self.configure(destination_folder=str(destination))

        first_session = SortSessionLogic()
        self.assertTrue(first_session.load_folder(str(source)))
        self.assertTrue(first_session.sort_current("good"))
        copied = destination / "SORT" / "Dobre" / "one.png"
        self.assertTrue(copied.exists())

        restored_session = SortSessionLogic()
        self.assertTrue(restored_session.restored)
        self.assertEqual(Path(restored_session.state().current_image_path).name, "two.png")
        self.assertTrue(restored_session.state().can_undo)
        self.assertTrue(restored_session.undo_last_sort())
        self.assertFalse(copied.exists())
        self.assertEqual(Path(restored_session.state().current_image_path).name, "one.png")

    def test_corrupt_session_is_ignored(self):
        self.config_path.parent.mkdir(parents=True)
        SettingsLogic.session_path().write_text("not json", encoding="utf-8")
        session = SortSessionLogic()
        self.assertFalse(session.restored)
        self.assertFalse(session.state().has_images)

    def test_session_is_saved_atomically(self):
        SortSessionStore.save({"source_folder": "", "images": [], "current_index": 0, "history": []})
        data = json.loads(SettingsLogic.session_path().read_text(encoding="utf-8"))
        self.assertEqual(data["version"], 1)
        self.assertEqual(list(SettingsLogic.session_path().parent.glob(".session-*.tmp")), [])

    def test_empty_folder_clears_previous_session(self):
        source = self.root / "source"
        empty = self.root / "empty"
        source.mkdir()
        empty.mkdir()
        (source / "photo.png").touch()
        self.configure()
        session = SortSessionLogic()
        self.assertTrue(session.load_folder(str(source)))
        self.assertTrue(SettingsLogic.session_path().exists())
        self.assertFalse(session.load_folder(str(empty)))
        self.assertFalse(SettingsLogic.session_path().exists())

    def test_missing_restored_destination_is_preserved_and_blocked(self):
        source = self.root / "source"
        destination = self.root / "usb"
        source.mkdir()
        destination.mkdir()
        (source / "photo.png").write_bytes(b"image")
        self.configure(destination_folder=str(destination))
        first = SortSessionLogic()
        self.assertTrue(first.load_folder(str(source)))
        destination.rmdir()

        restored = SortSessionLogic()
        self.assertTrue(restored.restored)
        path, fixed, _categories, available = restored.destination_info()
        self.assertEqual(path, str(destination / "SORT"))
        self.assertTrue(fixed)
        self.assertFalse(available)
        with self.assertRaises(DestinationUnavailableError):
            restored.sort_current("good")

    def test_files_from_multiple_folders_require_shared_destination(self):
        first_dir = self.root / "first"
        second_dir = self.root / "second"
        first_dir.mkdir()
        second_dir.mkdir()
        first = first_dir / "one.png"
        second = second_dir / "two.png"
        first.touch()
        second.touch()
        self.configure()
        session = SortSessionLogic()
        self.assertFalse(session.load_dropped_paths([str(first), str(second)]))
        self.assertEqual(session.last_load_error, "mixed_sources_need_destination")

        destination = self.root / "destination"
        destination.mkdir()
        session.initialize_sorting_structure(str(destination))
        self.assertTrue(session.load_dropped_paths([str(first), str(second)]))
        self.assertEqual(len(session.batch_logic.images), 2)

    def test_persistence_failure_is_exposed_once(self):
        source = self.root / "source"
        source.mkdir()
        (source / "photo.png").touch()
        self.configure()
        session = SortSessionLogic()
        with patch.object(SortSessionStore, "save", side_effect=OSError("disk full")):
            self.assertTrue(session.load_folder(str(source)))
        self.assertEqual(session.take_persistence_error(), "disk full")
        self.assertIsNone(session.take_persistence_error())


class ImageMetadataTests(IsolatedSettingsTestCase):
    def test_basic_image_metadata(self):
        image_path = self.root / "photo.png"
        Image.new("RGB", (32, 18), "blue").save(image_path)
        metadata = read_image_metadata(image_path)
        self.assertEqual(metadata["name"], "photo.png")
        self.assertEqual(metadata["dimensions"], "32 × 18 px")
        self.assertNotEqual(metadata["size"], "—")


if __name__ == "__main__":
    unittest.main()
