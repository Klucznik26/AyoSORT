import os
from dataclasses import dataclass

from core.sort_batch_logic import BatchLogic


@dataclass(slots=True)
class SortSessionState:
    current_image_path: str | None
    remaining_images: list[str]
    random_samples: list[str]
    has_images: bool
    can_undo: bool
    is_finished: bool


class SortSessionLogic:
    def __init__(self):
        self.batch_logic = BatchLogic()

    @property
    def image_extensions(self) -> set[str]:
        return set(self.batch_logic.image_extensions)

    def state(self) -> SortSessionState:
        has_images = self.batch_logic.has_images()
        return SortSessionState(
            current_image_path=self.batch_logic.current_image_path(),
            remaining_images=self.batch_logic.remaining_images() if has_images else [],
            random_samples=self.batch_logic.random_samples() if has_images else [],
            has_images=has_images,
            can_undo=self.batch_logic.can_undo(),
            is_finished=self.batch_logic.is_finished(),
        )

    def set_language(self, code: str) -> None:
        self.batch_logic.set_language(code)

    def refresh_categories(self) -> None:
        self.batch_logic.refresh_categories()

    def get_destination_folder(self) -> str | None:
        return self.batch_logic.get_destination_folder()

    def initialize_sorting_structure(self, folder: str | None = None) -> None:
        self.batch_logic.initialize_sorting_structure(folder)

    def prepare_source_folders(self) -> None:
        self.batch_logic.prepare_source_folders()

    def load_folder(self, folder_path: str) -> bool:
        if not self.batch_logic.load_images_from_folder(folder_path):
            return False
        if not self.batch_logic.has_images():
            return False
        return True

    def load_dropped_paths(self, paths: list[str]) -> bool:
        if not paths:
            return False
        if len(paths) == 1 and os.path.isdir(paths[0]):
            return self.load_folder(paths[0])
        folder = os.path.dirname(paths[0])
        selected = [
            os.path.basename(path)
            for path in paths
            if os.path.isfile(path)
            and os.path.dirname(path) == folder
            and os.path.splitext(path)[1].lower() in self.image_extensions
        ]
        if not selected:
            return False
        self.batch_logic.set_specific_images(folder, selected)
        return True

    def sort_current(self, category_key: str) -> bool:
        return self.batch_logic.sort_current_image(category_key)

    def undo_last_sort(self) -> bool:
        return self.batch_logic.undo_last_sort()

    def move_to_front(self, relative_index: int) -> None:
        self.batch_logic.move_to_front(relative_index)
