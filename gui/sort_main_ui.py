from PySide6.QtCore import QObject, QPoint, QRunnable, Qt, QThreadPool, QTimer, Signal, Slot
from PySide6.QtGui import QKeyEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from core.sort_session_logic import SortSessionLogic
from core.sort_settings_logic import SettingsLogic
from core.sort_theme_selector_logic import ThemeSelectorLogic
from gui.sort_preview_widgets import PreviewOverlayWidget
from gui.sort_workspace_ui import SortWorkspaceUI


class SortTaskSignals(QObject):
    finished = Signal(bool, str)


class SortTask(QRunnable):
    def __init__(self, session_logic: SortSessionLogic, category_key: str):
        super().__init__()
        self.session_logic = session_logic
        self.category_key = category_key
        self.signals = SortTaskSignals()

    @Slot()
    def run(self):
        try:
            success = self.session_logic.sort_current(self.category_key)
        except Exception as exc:  # noqa: BLE001 - worker boundary must report every failure to the GUI
            self.signals.finished.emit(False, str(exc))
            return
        self.signals.finished.emit(success, "")


class MainUI(QMainWindow):
    VERSION = "1.7.1"

    def __init__(self):
        super().__init__()
        self.session_logic = SortSessionLogic()
        self.current_theme_name = SettingsLogic.get_theme()
        self.workspace_ui = None
        self._startup_widget = None
        self.setAcceptDrops(True)
        self.setMinimumSize(1050, 700)
        self.resize(1050, 700)
        self._central = QWidget()
        self._central.setObjectName("main_widget")
        self.setCentralWidget(self._central)
        self._layout = QHBoxLayout(self._central)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)
        self.key_map = {
            Qt.Key.Key_1: "good",
            Qt.Key.Key_2: "mid",
            Qt.Key.Key_3: "bad",
        }
        self._sort_shortcuts = []
        self._undo_shortcuts = []
        self._sort_in_progress = False
        self._sort_task = None
        self._pending_animation = None
        self.apply_theme(self.current_theme_name)
        self._build_startup_ui()
        self.retranslate_ui()
        QTimer.singleShot(0, self._build_ui)

    def _build_ui(self):
        if self.workspace_ui is not None:
            return
        if self._startup_widget is not None:
            self._layout.removeWidget(self._startup_widget)
            self._startup_widget.deleteLater()
            self._startup_widget = None
        self.workspace_ui = SortWorkspaceUI(self.VERSION, self.handle_drop, self)
        self._layout.addWidget(self.workspace_ui)
        self.workspace_ui.settings_ui.close_requested.connect(self.close)
        self.workspace_ui.settings_ui.language_changed.connect(self._apply_language)
        self.workspace_ui.settings_ui.theme_changed.connect(self.apply_theme)
        self.workspace_ui.batch_ui.create_catalog_requested.connect(self.create_sorting_catalog)
        self.workspace_ui.batch_ui.select_folder_requested.connect(self.select_folder_to_sort)
        self.workspace_ui.batch_ui.category_names_requested.connect(self.open_category_names_window)
        self.workspace_ui.batch_ui.sort_requested.connect(self.sort_current)
        self.workspace_ui.batch_ui.undo_requested.connect(self.undo_last_sort)
        self.workspace_ui.preview_ui.file_list.itemClicked.connect(self._on_list_item_clicked)
        self._setup_sort_shortcuts()
        self._setup_undo_shortcuts()
        self.retranslate_ui()

    def _build_startup_ui(self):
        self._startup_widget = QFrame(self)
        self._startup_widget.setObjectName("startupPanel")
        self._startup_widget.setStyleSheet(
            "QFrame#startupPanel {"
            "background-color: rgba(10, 25, 20, 0.78);"
            "border-radius: 18px;"
            "border: 1px solid rgba(4, 227, 138, 0.22);"
            "}"
            "QLabel#startupTitle {"
            "color: white;"
            "font-size: 34px;"
            "font-weight: 700;"
            "letter-spacing: 1px;"
            "}"
            "QLabel#startupStatus {"
            "color: rgba(207, 232, 220, 0.92);"
            "font-size: 15px;"
            "}"
        )
        layout = QVBoxLayout(self._startup_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)
        layout.addStretch()
        title = QLabel("AyoSORT")
        title.setObjectName("startupTitle")
        title.setAlignment(Qt.AlignCenter)
        status = QLabel("...")
        status.setObjectName("startupStatus")
        status.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(status)
        layout.addStretch()
        self._layout.addWidget(self._startup_widget)

    def retranslate_ui(self):
        self.setWindowTitle(f"AyoSORT {self.VERSION}")
        if self.workspace_ui is not None:
            self.workspace_ui.retranslate_ui()
            self._refresh_state(show_empty=True)

    def apply_theme(self, theme_name: str | None = None):
        self.current_theme_name = theme_name or SettingsLogic.get_theme()
        self.setStyleSheet(ThemeSelectorLogic.get_stylesheet(self.current_theme_name))

    def _apply_language(self, code: str):
        self.session_logic.refresh_categories()
        self.retranslate_ui()

    def open_category_names_window(self):
        if self._sort_in_progress:
            return
        from gui.sort_category_names_ui import CategoryNamesUI

        dialog = CategoryNamesUI(self)
        dialog.setStyleSheet(self.styleSheet())
        if dialog.exec():
            self.session_logic.refresh_categories()
            self.workspace_ui.batch_ui.retranslate_ui()
            state = self.session_logic.state()
            if state.current_image_path or self.session_logic.get_destination_folder():
                try:
                    self.session_logic.prepare_source_folders()
                except OSError as exc:
                    QMessageBox.warning(self, SettingsLogic.tr("error_title"), str(exc))
            self._refresh_state()

    def handle_drop(self, paths):
        if self.workspace_ui is None or self._sort_in_progress:
            return
        if self.session_logic.load_dropped_paths(paths):
            self.workspace_ui.batch_ui.set_source_ready(True)
            self._refresh_state()
            return
        if paths:
            QMessageBox.information(self, SettingsLogic.tr("info_title"), SettingsLogic.tr("msg_no_images"))

    def create_sorting_catalog(self):
        if self._sort_in_progress:
            return
        dialog = self._directory_dialog("dialog_create_title", "dialog_create_accept")
        if dialog.exec() and dialog.selectedFiles():
            path = dialog.selectedFiles()[0]
            try:
                self.session_logic.initialize_sorting_structure(path)
            except OSError as exc:
                QMessageBox.critical(
                    self, SettingsLogic.tr("error_title"), SettingsLogic.tr("msg_error_create").format(e=exc)
                )

    def select_folder_to_sort(self):
        if self._sort_in_progress:
            return
        dialog = self._directory_dialog("dialog_select_title", "dialog_select_accept")
        if dialog.exec() and dialog.selectedFiles():
            self._load_images(folder_path=dialog.selectedFiles()[0])

    def _directory_dialog(self, title_key: str, accept_key: str):
        dialog = QFileDialog(self, SettingsLogic.tr(title_key))
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setLabelText(QFileDialog.DialogLabel.Accept, SettingsLogic.tr(accept_key))
        dialog.setLabelText(QFileDialog.DialogLabel.Reject, SettingsLogic.tr("btn_cancel"))
        dialog.setLabelText(QFileDialog.DialogLabel.LookIn, SettingsLogic.tr("dialog_look_in"))
        dialog.setLabelText(QFileDialog.DialogLabel.FileName, SettingsLogic.tr("dialog_file_name"))
        dialog.setLabelText(QFileDialog.DialogLabel.FileType, SettingsLogic.tr("dialog_file_type"))
        dialog.setStyleSheet(self.styleSheet())
        return dialog

    def _load_images(self, folder_path: str):
        try:
            if not self.session_logic.load_folder(folder_path):
                QMessageBox.information(
                    self, SettingsLogic.tr("info_title"), SettingsLogic.tr("msg_info_no_images_folder")
                )
                self.workspace_ui.preview_ui.clear_files()
                self.workspace_ui.batch_ui.set_source_ready(False)
                self.workspace_ui.file_drop_ui.reset_preview()
                return
            self.workspace_ui.batch_ui.set_source_ready(True)
            self._refresh_state()
        except OSError as exc:
            QMessageBox.critical(
                self, SettingsLogic.tr("error_title"), SettingsLogic.tr("msg_error_access").format(e=exc)
            )

    def _refresh_state(self, show_empty: bool = False):
        if self.workspace_ui is None:
            return
        state = self.session_logic.state()
        if state.current_image_path:
            self.workspace_ui.file_drop_ui.show_preview(state.current_image_path)
            self.workspace_ui.preview_ui.update_files(state.remaining_images, state.random_samples)
        elif show_empty:
            self.workspace_ui.file_drop_ui.reset_preview()
            self.workspace_ui.preview_ui.clear_files()
        else:
            self.workspace_ui.file_drop_ui.show_finished()
            self.workspace_ui.preview_ui.clear_files(completed=True)
        self.workspace_ui.batch_ui.set_sort_enabled(state.has_images)
        self.workspace_ui.batch_ui.set_undo_enabled(state.can_undo)
        self._set_sort_shortcuts_enabled(state.has_images)
        self._set_undo_shortcuts_enabled(state.can_undo)

    def _setup_sort_shortcuts(self):
        if self._sort_shortcuts:
            return
        shortcut_map = {
            "good": Qt.Key.Key_Left,
            "mid": Qt.Key.Key_Right,
            "bad": Qt.Key.Key_Down,
        }
        for category_key, key in shortcut_map.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
            shortcut.setEnabled(False)
            shortcut.activated.connect(lambda key=category_key: self.sort_current(key))
            self._sort_shortcuts.append(shortcut)

    def _set_sort_shortcuts_enabled(self, enabled: bool):
        for shortcut in self._sort_shortcuts:
            shortcut.setEnabled(enabled)

    def _setup_undo_shortcuts(self):
        if self._undo_shortcuts:
            return
        for sequence in (QKeySequence.StandardKey.Undo, QKeySequence(Qt.Key.Key_Backspace)):
            shortcut = QShortcut(sequence, self)
            shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
            shortcut.setEnabled(False)
            shortcut.activated.connect(self.undo_last_sort)
            self._undo_shortcuts.append(shortcut)

    def _set_undo_shortcuts_enabled(self, enabled: bool):
        for shortcut in self._undo_shortcuts:
            shortcut.setEnabled(enabled)

    def sort_current(self, category_key: str):
        if self._sort_in_progress:
            return
        state = self.session_logic.state()
        if state.is_finished:
            return
        pixmap = self.workspace_ui.file_drop_ui.current_pixmap()
        geom = self.workspace_ui.file_drop_ui.preview_geometry(self)
        animation = {
            "good": ("#4CAF50", -15, QPoint(0, 0)),
            "mid": ("#2196F3", 15, QPoint(0, 0)),
            "bad": ("#F44336", 0, QPoint(0, 450)),
        }[category_key]
        self._pending_animation = (pixmap.copy(), geom, animation) if pixmap and not pixmap.isNull() else None
        self._set_sort_busy(True)
        task = SortTask(self.session_logic, category_key)
        task.signals.finished.connect(self._on_sort_finished)
        self._sort_task = task
        QThreadPool.globalInstance().start(task)

    @Slot(bool, str)
    def _on_sort_finished(self, success: bool, error: str):
        pending_animation = self._pending_animation
        self._pending_animation = None
        self._sort_task = None
        self._set_sort_busy(False)
        if not success:
            if error:
                QMessageBox.critical(
                    self,
                    SettingsLogic.tr("error_title"),
                    SettingsLogic.tr("msg_error_copy").format(e=error),
                )
            self._refresh_state()
            return
        if pending_animation is not None:
            pixmap, geom, animation = pending_animation
            if geom is not None:
                PreviewOverlayWidget(self, pixmap, geom, animation[0], animation[1], animation[2])
        self._refresh_state()

    def _set_sort_busy(self, busy: bool):
        self._sort_in_progress = busy
        if self.workspace_ui is not None:
            self.workspace_ui.batch_ui.set_busy(busy)
            self.workspace_ui.settings_ui.setEnabled(not busy)
            self.workspace_ui.preview_ui.file_list.setEnabled(not busy)
        self._set_sort_shortcuts_enabled(False if busy else self.session_logic.state().has_images)
        self._set_undo_shortcuts_enabled(False if busy else self.session_logic.state().can_undo)

    def undo_last_sort(self):
        if self._sort_in_progress:
            return
        if not self.session_logic.state().can_undo:
            return
        try:
            if not self.session_logic.undo_last_sort():
                return
        except OSError as exc:
            QMessageBox.critical(
                self,
                SettingsLogic.tr("error_title"),
                SettingsLogic.tr("msg_error_undo", "Failed to undo the last sorting action: {e}").format(e=exc),
            )
            return
        self._refresh_state()

    def _on_list_item_clicked(self, item):
        if self._sort_in_progress:
            return
        row = self.workspace_ui.preview_ui.file_list.row(item)
        if row > 0:
            self.session_logic.move_to_front(row)
            self._refresh_state()

    def keyPressEvent(self, event: QKeyEvent):
        if not self._sort_in_progress and event.key() in self.key_map:
            self.sort_current(self.key_map[event.key()])
        else:
            super().keyPressEvent(event)
