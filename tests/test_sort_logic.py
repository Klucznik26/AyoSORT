import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core.sort_settings_logic as settings_module
from core.sort_batch_logic import BatchLogic
from core.sort_session_logic import SortSessionLogic
from core.sort_settings_logic import SettingsLogic


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


if __name__ == "__main__":
    unittest.main()
