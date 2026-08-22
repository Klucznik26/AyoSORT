import re
from pathlib import Path
from typing import ClassVar

from core.sort_batch_files import BatchFiles
from core.sort_settings_logic import SettingsLogic


class BatchLogic:
    category_order: ClassVar[tuple[str, ...]] = ("good", "mid", "bad")
    image_extensions: ClassVar[frozenset[str]] = frozenset(
        {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff", ".ico"}
    )

    def __init__(self):
        self.images = []
        self.current_index = 0
        self.source_folder = ""
        configured_destination = SettingsLogic.get_destination_folder()
        self.destination_initialized = bool(configured_destination and Path(configured_destination).is_dir())
        self._history = []
        self.refresh_categories()

    def refresh_categories(self) -> None:
        self.categories = self._build_categories(SettingsLogic.get_language())

    def set_language(self, lang_code: str) -> None:
        SettingsLogic.set_language(lang_code)
        self.refresh_categories()

    def set_destination_folder(self, folder: str | None) -> None:
        SettingsLogic.set_destination_folder(folder)
        self.destination_initialized = bool(folder)

    def get_destination_folder(self) -> str | None:
        return SettingsLogic.get_destination_folder()

    def initialize_sorting_structure(self, folder: str | None = None) -> None:
        target = folder or self.get_destination_folder()
        if not target:
            raise ValueError("Destination folder not set")
        self.set_destination_folder(target)
        self.destination_initialized = True
        subdirs = [self._folder_names()[key] for key in self.category_order]
        BatchFiles.create_directories(Path(target) / "SORT", subdirs)

    def load_images_from_folder(self, folder: str) -> bool:
        self.source_folder = folder
        try:
            self.images = sorted(
                [
                    file_name
                    for file_name in Path(folder).iterdir()
                    if file_name.is_file() and file_name.suffix.lower() in self.image_extensions
                ],
                key=lambda path: self._natural_sort_key(path.name),
            )
            self.current_index = 0
            self._history.clear()
            return True
        except OSError:
            self.images = []
            self._history.clear()
            return False

    def set_specific_images(self, folder: str, file_list: list[str]) -> None:
        self.source_folder = folder
        self.images = [Path(folder) / name for name in sorted(file_list, key=self._natural_sort_key)]
        self.current_index = 0
        self._history.clear()

    def has_images(self) -> bool:
        return self.current_index < len(self.images)

    def is_finished(self) -> bool:
        return not self.has_images()

    def can_undo(self) -> bool:
        return bool(self._history)

    def current_image_path(self) -> str | None:
        if self.has_images():
            return str(self.images[self.current_index])
        return None

    def remaining_images(self) -> list[str]:
        return [path.name for path in self.images[self.current_index :]]

    def move_to_front(self, relative_index: int) -> None:
        idx = self.current_index + relative_index
        if self.current_index < idx < len(self.images):
            item = self.images.pop(idx)
            self.images.insert(self.current_index, item)

    def random_samples(self, count: int = 5) -> list[str]:
        remaining = self.images[self.current_index :]
        if not remaining:
            return []
        return [str(path) for path in remaining[:count]]

    def prepare_source_folders(self) -> None:
        source = self._target_root()
        for folder_name in self.categories.values():
            (source / folder_name).mkdir(parents=True, exist_ok=True)

    def sort_current_image(self, category_key: str) -> bool:
        if self.is_finished():
            return False
        dest_subdir = self.categories.get(category_key)
        if not dest_subdir:
            return False
        current = self.images[self.current_index]
        target_root = self._target_root()
        requested_destination = target_root / dest_subdir / current.name
        destination = BatchFiles.copy_image(current, requested_destination)
        destination_stat = destination.stat()
        self._history.append(
            {
                "index": self.current_index,
                "source": current,
                "destination": destination,
                "destination_signature": (
                    destination_stat.st_ino,
                    destination_stat.st_size,
                    destination_stat.st_mtime_ns,
                ),
            }
        )
        self.current_index += 1
        return True

    def undo_last_sort(self) -> bool:
        if not self._history:
            return False
        action = self._history.pop()
        destination = action["destination"]
        if destination.exists():
            destination_stat = destination.stat()
            current_signature = (
                destination_stat.st_ino,
                destination_stat.st_size,
                destination_stat.st_mtime_ns,
            )
            if current_signature != action["destination_signature"]:
                self._history.append(action)
                raise OSError(f"The sorted file has changed and cannot be safely removed: {destination}")
            destination.unlink()
        self.current_index = max(0, min(int(action["index"]), len(self.images) - 1 if self.images else 0))
        return True

    def _target_root(self) -> Path:
        if self.destination_initialized:
            destination = self.get_destination_folder()
            if destination:
                return Path(destination)
        return Path(self.source_folder)

    def _build_categories(self, lang_code: str) -> dict:
        names = self._folder_names(lang_code)
        return {key: str(Path("SORT") / names[key]) for key in self.category_order}

    def _folder_names(self, lang_code: str | None = None) -> dict:
        code = lang_code or SettingsLogic.get_language()
        custom_names = SettingsLogic.get_category_names()
        names = {
            "good": "Dobre" if code == "pl" else "Good",
            "mid": "Średnie" if code == "pl" else "Average",
            "bad": "Słabe" if code == "pl" else "Bad",
        }
        strings = SettingsLogic.get_translations(code)
        for key, field in [("good", "folder_good"), ("mid", "folder_mid"), ("bad", "folder_bad")]:
            raw_custom_name = custom_names.get(key, "").strip()
            if raw_custom_name:
                names[key] = self._normalize_folder_name(raw_custom_name)
                continue
            fallback = None if code == "pl" else self._first_word(strings.get(f"tooltip_{key}"))
            names[key] = self._normalize_folder_name(strings.get(field) or fallback or names[key])
        used_names = set()
        for key in self.category_order:
            candidate = names[key]
            unique_name = candidate
            suffix = 2
            while unique_name.casefold() in used_names:
                unique_name = f"{candidate} ({suffix})"
                suffix += 1
            names[key] = unique_name
            used_names.add(unique_name.casefold())
        return names

    @staticmethod
    def _first_word(text: str | None) -> str:
        if not text:
            return ""
        token = text.strip().split()[0]
        return re.sub(r"[^\w\-ąćęłńóśźżА-Яа-яЄєІіЇїҐґ]+$", "", token)

    @staticmethod
    def _normalize_folder_name(name: str) -> str:
        clean = re.sub(r'[\x00-\x1f<>:"/\\|?*]+', "_", str(name)).strip(" .")
        if not clean or clean in {".", ".."}:
            return "Category"
        reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
        if clean.split(".", 1)[0].upper() in reserved:
            clean = f"_{clean}"
        return clean[:120].rstrip(" .") or "Category"

    @staticmethod
    def _natural_sort_key(name: str) -> tuple:
        return tuple((1, int(part)) if part.isdigit() else (0, part.casefold()) for part in re.split(r"(\d+)", name))
