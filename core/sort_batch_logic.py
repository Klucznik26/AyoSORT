import random
import re
from pathlib import Path

from core.sort_batch_files import BatchFiles
from core.sort_settings_logic import SettingsLogic


class BatchLogic:
    category_order = ['good', 'mid', 'bad']
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.wep', '.tif', '.tiff', '.ico'}

    def __init__(self):
        self.images = []
        self.current_index = 0
        self.source_folder = ''
        self.refresh_categories()

    def refresh_categories(self) -> None:
        self.categories = self._build_categories(SettingsLogic.get_language())

    def set_language(self, lang_code: str) -> None:
        SettingsLogic.set_language(lang_code)
        self.refresh_categories()

    def set_destination_folder(self, folder: str | None) -> None:
        SettingsLogic.set_destination_folder(folder)

    def get_destination_folder(self) -> str | None:
        return SettingsLogic.get_destination_folder()

    def initialize_sorting_structure(self, folder: str | None = None) -> None:
        target = folder or self.get_destination_folder()
        if not target:
            raise ValueError('Destination folder not set')
        self.set_destination_folder(target)
        subdirs = [self._folder_names()[key] for key in self.category_order]
        BatchFiles.create_directories(Path(target) / 'SORT', subdirs)

    def load_images_from_folder(self, folder: str) -> bool:
        self.source_folder = folder
        try:
            self.images = sorted(
                file_name for file_name in Path(folder).iterdir()
                if file_name.is_file() and file_name.suffix.lower() in self.image_extensions
            )
            self.current_index = 0
            return True
        except OSError:
            self.images = []
            return False

    def set_specific_images(self, folder: str, file_list: list[str]) -> None:
        self.source_folder = folder
        self.images = [Path(folder) / name for name in sorted(file_list)]
        self.current_index = 0

    def has_images(self) -> bool:
        return self.current_index < len(self.images)

    def is_finished(self) -> bool:
        return not self.has_images()

    def current_image_path(self) -> str | None:
        if self.has_images():
            return str(self.images[self.current_index])
        return None

    def current_filename(self) -> str | None:
        if self.has_images():
            return self.images[self.current_index].name
        return None

    def remaining_images(self) -> list[str]:
        return [path.name for path in self.images[self.current_index:]]

    def move_to_front(self, relative_index: int) -> None:
        idx = self.current_index + relative_index
        if self.current_index < idx < len(self.images):
            item = self.images.pop(idx)
            self.images.insert(self.current_index, item)

    def random_samples(self, count: int = 5) -> list[str]:
        remaining = self.images[self.current_index:]
        if not remaining:
            return []
        sample = random.sample(remaining, min(len(remaining), count))
        return [str(path) for path in sample]

    def prepare_source_folders(self) -> None:
        source = Path(self.source_folder)
        for folder_name in self.categories.values():
            (source / folder_name).mkdir(parents=True, exist_ok=True)

    def sort_current_image(self, category_key: str) -> bool:
        if self.is_finished():
            return False
        dest_subdir = self.categories.get(category_key)
        if not dest_subdir:
            return False
        current = self.images[self.current_index]
        target_root = Path(self.get_destination_folder() or self.source_folder)
        destination = target_root / dest_subdir / current.name
        BatchFiles.copy_image(current, destination)
        self.current_index += 1
        return True

    def _build_categories(self, lang_code: str) -> dict:
        names = self._folder_names(lang_code)
        return {key: str(Path('SORT') / names[key]) for key in self.category_order}

    def _folder_names(self, lang_code: str | None = None) -> dict:
        code = lang_code or SettingsLogic.get_language()
        names = {
            'good': 'Dobre' if code == 'pl' else 'Good',
            'mid': 'Średnie' if code == 'pl' else 'Average',
            'bad': 'Słabe' if code == 'pl' else 'Bad',
        }
        strings = SettingsLogic.get_translations(code)
        for key, field in [('good', 'folder_good'), ('mid', 'folder_mid'), ('bad', 'folder_bad')]:
            fallback = None if code == 'pl' else self._first_word(strings.get(f'tooltip_{key}'))
            names[key] = self._normalize_folder_name(strings.get(field) or fallback or names[key])
        return names

    @staticmethod
    def _first_word(text: str | None) -> str:
        if not text:
            return ''
        token = text.strip().split()[0]
        return re.sub(r"[^\w\-ąćęłńóśźżА-Яа-яЄєІіЇїҐґ]+$", '', token)

    @staticmethod
    def _normalize_folder_name(name: str) -> str:
        clean = str(name).replace('/', '_').replace('\\', '_').strip()
        return clean or 'Category'
