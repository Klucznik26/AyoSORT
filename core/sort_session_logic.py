import logging
from dataclasses import dataclass
from pathlib import Path

from core.sort_batch_logic import BatchLogic
from core.sort_session_store import SortSessionStore

LOGGER = logging.getLogger(__name__)


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
        self.last_load_error = None
        self.last_persistence_error = None
        self.restored = self.batch_logic.restore_session(SortSessionStore.load())
        if self.restored:
            self._persist()

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

    def destination_info(self) -> tuple[str | None, bool, list[str], bool]:
        return self.batch_logic.destination_info()

    def initialize_sorting_structure(self, folder: str | None = None) -> None:
        self.batch_logic.initialize_sorting_structure(folder)
        self._persist()

    def prepare_source_folders(self) -> None:
        self.batch_logic.prepare_source_folders()

    def load_folder(self, folder_path: str) -> bool:
        if not self.batch_logic.load_images_from_folder(folder_path):
            return False
        if not self.batch_logic.has_images():
            self.restored = False
            self._clear_persisted_session()
            return False
        self.restored = False
        self._persist()
        return True

    def load_dropped_paths(self, paths: list[str]) -> bool:
        self.last_load_error = None
        if not paths:
            return False
        if len(paths) == 1 and Path(paths[0]).is_dir():
            return self.load_folder(paths[0])
        selected = [
            str(Path(path).resolve())
            for path in paths
            if Path(path).is_file() and Path(path).suffix.lower() in self.image_extensions
        ]
        if not selected:
            return False
        source_folders = {str(Path(path).parent) for path in selected}
        if len(source_folders) > 1 and not self.get_destination_folder():
            self.last_load_error = "mixed_sources_need_destination"
            return False
        self.batch_logic.set_image_paths(selected)
        self.restored = False
        self._persist()
        return True

    def sort_current(self, category_key: str) -> bool:
        success = self.batch_logic.sort_current_image(category_key)
        if success:
            self._persist()
        return success

    def undo_last_sort(self) -> bool:
        success = self.batch_logic.undo_last_sort()
        if success:
            self._persist()
        return success

    def move_to_front(self, relative_index: int) -> None:
        self.batch_logic.move_to_front(relative_index)
        self._persist()

    def image_path_at(self, relative_index: int) -> str | None:
        return self.batch_logic.image_path_at(relative_index)

    def take_persistence_error(self) -> str | None:
        error = self.last_persistence_error
        self.last_persistence_error = None
        return error

    def _persist(self) -> bool:
        try:
            SortSessionStore.save(self.batch_logic.session_snapshot())
        except (OSError, TypeError, ValueError) as exc:
            self.last_persistence_error = str(exc)
            LOGGER.warning("Cannot persist AyoSORT session: %s", exc)
            return False
        self.last_persistence_error = None
        return True

    def _clear_persisted_session(self) -> bool:
        try:
            SortSessionStore.clear()
        except OSError as exc:
            self.last_persistence_error = str(exc)
            LOGGER.warning("Cannot clear AyoSORT session: %s", exc)
            return False
        self.last_persistence_error = None
        return True
