import re
from pathlib import Path
from typing import ClassVar

from core.sort_batch_files import BatchFiles
from core.sort_settings_logic import SettingsLogic


class DestinationUnavailableError(OSError):
    pass


class BatchLogic:
    category_order: ClassVar[tuple[str, ...]] = ("good", "mid", "bad")
    image_extensions: ClassVar[frozenset[str]] = frozenset(
        {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff", ".ico"}
    )

    def __init__(self):
        self.images = []
        self.current_index = 0
        self.source_folder = ""
        self.source_folders = []
        configured_destination = SettingsLogic.get_destination_folder()
        self.destination_initialized = bool(configured_destination)
        self._session_folder_names = None
        self._history = []
        self.refresh_categories()

    def refresh_categories(self) -> None:
        names = self._session_folder_names or self._folder_names(SettingsLogic.get_language())
        self.categories = self._build_categories(names)

    def set_language(self, lang_code: str) -> None:
        SettingsLogic.set_language(lang_code)
        self.refresh_categories()

    def set_destination_folder(self, folder: str | None) -> None:
        SettingsLogic.set_destination_folder(folder)
        self.destination_initialized = bool(folder)

    def get_destination_folder(self) -> str | None:
        return SettingsLogic.get_destination_folder()

    def destination_info(self) -> tuple[str | None, bool, list[str], bool]:
        """Describe the effective destination without creating any directories."""
        root = self.get_destination_folder() if self.destination_initialized else self.source_folder
        destination = str(Path(root) / "SORT") if root else None
        available = bool(root and Path(root).is_dir())
        names = self._session_folder_names or self._folder_names()
        return destination, self.destination_initialized, [names[key] for key in self.category_order], available

    def initialize_sorting_structure(self, folder: str | None = None) -> None:
        target = folder or self.get_destination_folder()
        if not target:
            raise ValueError("Destination folder not set")
        self.set_destination_folder(target)
        self.destination_initialized = True
        names = self._session_folder_names or self._folder_names()
        subdirs = [names[key] for key in self.category_order]
        BatchFiles.create_directories(Path(target) / "SORT", subdirs)

    def load_images_from_folder(self, folder: str) -> bool:
        source = Path(folder).resolve()
        self.source_folder = str(source)
        self.source_folders = [source]
        try:
            self.images = sorted(
                [
                    file_name
                    for file_name in source.iterdir()
                    if file_name.is_file() and file_name.suffix.lower() in self.image_extensions
                ],
                key=lambda path: self._natural_sort_key(path.name),
            )
            self.current_index = 0
            self._history.clear()
            self._session_folder_names = self._folder_names() if self.images else None
            self.refresh_categories()
            return True
        except OSError:
            self.images = []
            self._history.clear()
            self._session_folder_names = None
            self.refresh_categories()
            return False

    def set_specific_images(self, folder: str, file_list: list[str]) -> None:
        self.set_image_paths([Path(folder) / name for name in file_list])

    def set_image_paths(self, paths: list[str | Path]) -> None:
        resolved = [Path(path).resolve() for path in paths]
        self.images = sorted(resolved, key=lambda path: self._natural_sort_key(path.name))
        self.source_folders = list(dict.fromkeys(path.parent for path in self.images))
        self.source_folder = str(self.source_folders[0]) if self.source_folders else ""
        self.current_index = 0
        self._history.clear()
        self._session_folder_names = self._folder_names() if self.images else None
        self.refresh_categories()

    def session_snapshot(self) -> dict:
        return {
            "source_folder": self.source_folder,
            "source_folders": [str(path) for path in self.source_folders],
            "destination_folder": self.get_destination_folder(),
            "category_folder_names": dict(self._session_folder_names or self._folder_names()),
            "images": [str(path) for path in self.images],
            "current_index": self.current_index,
            "history": [
                {
                    "index": int(action["index"]),
                    "source": str(action["source"]),
                    "destination": str(action["destination"]),
                    "destination_signature": list(action["destination_signature"]),
                }
                for action in self._history
            ],
        }

    def restore_session(self, data: dict | None) -> bool:
        if not isinstance(data, dict):
            return False
        raw_source_folders = data.get("source_folders")
        if not isinstance(raw_source_folders, list):
            raw_source_folders = [data.get("source_folder", "")]
        source_folders = []
        for raw_source in raw_source_folders:
            if not isinstance(raw_source, str):
                continue
            source = Path(raw_source).expanduser()
            if source.is_dir():
                source_folders.append(source.resolve())
        raw_images = data.get("images")
        raw_index = data.get("current_index")
        if not source_folders or not isinstance(raw_images, list) or not isinstance(raw_index, int):
            return False

        indexed_images = []
        for old_index, raw_path in enumerate(raw_images):
            if not isinstance(raw_path, str):
                continue
            path = Path(raw_path).expanduser()
            try:
                resolved = path.resolve()
                is_inside_source = resolved.parent in source_folders
            except (OSError, RuntimeError):
                continue
            if is_inside_source and resolved.is_file() and resolved.suffix.lower() in self.image_extensions:
                indexed_images.append((old_index, resolved))
        if not indexed_images:
            return False

        old_to_new = {old: new for new, (old, _path) in enumerate(indexed_images)}
        restored_index = sum(1 for old, _path in indexed_images if old < raw_index)
        self.source_folders = source_folders
        self.source_folder = str(source_folders[0])
        self.images = [path for _old, path in indexed_images]
        self.current_index = min(restored_index, len(self.images))

        raw_names = data.get("category_folder_names")
        restored_names = {}
        if isinstance(raw_names, dict):
            for key in self.category_order:
                value = raw_names.get(key)
                if isinstance(value, str) and value.strip():
                    restored_names[key] = self._normalize_folder_name(value)
        if len(restored_names) != len(self.category_order) or len({v.casefold() for v in restored_names.values()}) != 3:
            restored_names = self._folder_names()
        self._session_folder_names = restored_names
        self.refresh_categories()

        destination_value = data.get("destination_folder")
        destination = Path(destination_value).expanduser() if isinstance(destination_value, str) else None
        destination = destination.resolve(strict=False) if destination else None
        SettingsLogic.set_destination_folder(str(destination) if destination else None)
        self.destination_initialized = destination is not None
        target_roots = [destination] if destination else source_folders
        sort_roots = [(root / "SORT").resolve(strict=False) for root in target_roots]

        restored_history = []
        raw_history = data.get("history", [])
        if isinstance(raw_history, list):
            for raw_action in raw_history:
                if not isinstance(raw_action, dict):
                    continue
                old_action_index = raw_action.get("index")
                signature = raw_action.get("destination_signature")
                if old_action_index not in old_to_new or not isinstance(signature, list) or len(signature) != 3:
                    continue
                try:
                    action_source = Path(str(raw_action["source"])).resolve()
                    action_destination = Path(str(raw_action["destination"])).resolve()
                    signature_tuple = tuple(int(value) for value in signature)
                    safe_destination = any(action_destination.is_relative_to(sort_root) for sort_root in sort_roots)
                except (KeyError, OSError, RuntimeError, TypeError, ValueError):
                    continue
                if action_source != self.images[old_to_new[old_action_index]] or not safe_destination:
                    continue
                restored_history.append(
                    {
                        "index": old_to_new[old_action_index],
                        "source": action_source,
                        "destination": action_destination,
                        "destination_signature": signature_tuple,
                    }
                )
        self._history = restored_history
        return True

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

    def image_path_at(self, relative_index: int) -> str | None:
        index = self.current_index + relative_index
        if self.current_index <= index < len(self.images):
            return str(self.images[index])
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
                destination_path = Path(destination)
                if not destination_path.is_dir():
                    raise DestinationUnavailableError(f"Destination is unavailable: {destination_path}")
                return destination_path
        if len(self.source_folders) > 1:
            raise DestinationUnavailableError("A shared destination is required for images from multiple folders")
        return Path(self.source_folder)

    def _build_categories(self, names: dict[str, str] | str) -> dict:
        if isinstance(names, str):
            names = self._session_folder_names or self._folder_names(names)
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
