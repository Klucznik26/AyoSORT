import os

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QMainWindow, QMessageBox, QWidget

from core.sort_batch_logic import BatchLogic
from core.sort_settings_logic import SettingsLogic
from core.sort_theme_selector_logic import ThemeSelectorLogic
from gui.sort_batch_ui import BatchUI
from gui.sort_file_drop_ui import FileDropUI
from gui.sort_preview_ui import PreviewUI
from gui.sort_preview_widgets import PreviewOverlayWidget
from gui.sort_settings_ui import SettingsUI


class MainUI(QMainWindow):
    VERSION = '1.7.0'

    def __init__(self):
        super().__init__()
        self.logic = BatchLogic()
        self.current_theme_name = SettingsLogic.get_theme()
        self.setAcceptDrops(True)
        self.setMinimumSize(1050, 700)
        self.resize(1050, 700)
        central = QWidget(); central.setObjectName('main_widget'); self.setCentralWidget(central)
        layout = QHBoxLayout(central); layout.setContentsMargins(10, 10, 10, 10); layout.setSpacing(10)
        self.settings_ui = SettingsUI(self.VERSION, self)
        self.batch_ui = BatchUI(self)
        self.file_drop_ui = FileDropUI(self.handle_drop, self)
        self.preview_ui = PreviewUI(self)
        layout.addWidget(self.settings_ui); layout.addWidget(self.batch_ui); layout.addWidget(self.file_drop_ui); layout.addWidget(self.preview_ui)
        self.settings_ui.close_requested.connect(self.close)
        self.settings_ui.language_changed.connect(self._apply_language)
        self.settings_ui.theme_changed.connect(self.apply_theme)
        self.batch_ui.create_catalog_requested.connect(self.create_sorting_catalog)
        self.batch_ui.select_folder_requested.connect(self.select_folder_to_sort)
        self.batch_ui.sort_requested.connect(self.sort_current)
        self.preview_ui.file_list.itemClicked.connect(self._on_list_item_clicked)
        self.key_map = {Qt.Key.Key_1: 'good', Qt.Key.Key_2: 'mid', Qt.Key.Key_3: 'bad'}
        self.apply_theme(self.current_theme_name)
        self.retranslate_ui()
        self.batch_ui.set_destination_ready(bool(SettingsLogic.get_destination_folder() and os.path.exists(SettingsLogic.get_destination_folder())))

    def retranslate_ui(self):
        self.setWindowTitle(f'AyoSORT {self.VERSION}')
        self.settings_ui.retranslate_ui(); self.batch_ui.retranslate_ui(); self.file_drop_ui.retranslate_ui(); self.preview_ui.retranslate_ui()
        self._refresh_state(show_empty=True)

    def apply_theme(self, theme_name: str | None = None):
        self.current_theme_name = theme_name or SettingsLogic.get_theme()
        self.setStyleSheet(ThemeSelectorLogic.get_stylesheet(self.current_theme_name))

    def _apply_language(self, code: str):
        self.logic.set_language(code)
        self.retranslate_ui()

    def handle_drop(self, paths):
        if not paths:
            return
        if len(paths) == 1 and os.path.isdir(paths[0]):
            self._load_images(folder_path=paths[0])
            return
        folder = os.path.dirname(paths[0])
        selected = [os.path.basename(path) for path in paths if os.path.isfile(path) and os.path.dirname(path) == folder and os.path.splitext(path)[1].lower() in self.logic.image_extensions]
        if selected:
            self.logic.set_specific_images(folder, selected)
            self.logic.prepare_source_folders()
            self.batch_ui.set_source_ready(True)
            self._refresh_state()
        else:
            QMessageBox.information(self, SettingsLogic.tr('info_title'), SettingsLogic.tr('msg_no_images'))

    def create_sorting_catalog(self):
        dialog = self._directory_dialog('dialog_create_title', 'dialog_create_accept')
        if dialog.exec() and dialog.selectedFiles():
            path = dialog.selectedFiles()[0]
            try:
                self.logic.initialize_sorting_structure(path)
                self.batch_ui.set_destination_ready(True)
            except OSError as exc:
                QMessageBox.critical(self, SettingsLogic.tr('error_title'), SettingsLogic.tr('msg_error_create').format(e=exc))

    def select_folder_to_sort(self):
        dialog = self._directory_dialog('dialog_select_title', 'dialog_select_accept')
        if dialog.exec() and dialog.selectedFiles():
            self._load_images(folder_path=dialog.selectedFiles()[0])

    def _directory_dialog(self, title_key: str, accept_key: str):
        dialog = QFileDialog(self, SettingsLogic.tr(title_key))
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setLabelText(QFileDialog.DialogLabel.Accept, SettingsLogic.tr(accept_key))
        dialog.setLabelText(QFileDialog.DialogLabel.Reject, SettingsLogic.tr('btn_cancel'))
        dialog.setLabelText(QFileDialog.DialogLabel.LookIn, SettingsLogic.tr('dialog_look_in'))
        dialog.setLabelText(QFileDialog.DialogLabel.FileName, SettingsLogic.tr('dialog_file_name'))
        dialog.setLabelText(QFileDialog.DialogLabel.FileType, SettingsLogic.tr('dialog_file_type'))
        dialog.setStyleSheet(self.styleSheet())
        return dialog

    def _load_images(self, folder_path: str):
        try:
            if not self.logic.load_images_from_folder(folder_path) or not self.logic.has_images():
                QMessageBox.information(self, SettingsLogic.tr('info_title'), SettingsLogic.tr('msg_info_no_images_folder'))
                self.preview_ui.clear_files(); self.batch_ui.set_source_ready(False); self.file_drop_ui.reset_preview()
                return
            self.logic.prepare_source_folders()
            self.batch_ui.set_source_ready(True)
            self._refresh_state()
        except OSError as exc:
            QMessageBox.critical(self, SettingsLogic.tr('error_title'), SettingsLogic.tr('msg_error_access').format(e=exc))

    def _refresh_state(self, show_empty: bool = False):
        path = self.logic.current_image_path()
        if path:
            self.file_drop_ui.show_preview(path)
            self.preview_ui.update_files(self.logic.remaining_images(), self.logic.random_samples())
        elif show_empty:
            self.file_drop_ui.reset_preview()
            self.preview_ui.clear_files()
        else:
            self.file_drop_ui.show_finished()
            self.preview_ui.clear_files(completed=True)
        self.batch_ui.set_sort_enabled(self.logic.has_images())

    def sort_current(self, category_key: str):
        if self.logic.is_finished():
            return
        pixmap = self.file_drop_ui.current_pixmap()
        try:
            if not self.logic.sort_current_image(category_key):
                return
        except Exception as exc:
            QMessageBox.critical(self, SettingsLogic.tr('error_title'), SettingsLogic.tr('msg_error_copy').format(e=exc))
            return
        if pixmap and not pixmap.isNull():
            pos = self.file_drop_ui.drop_label.mapTo(self, QPoint(0, 0))
            geom = QRect(pos, self.file_drop_ui.drop_label.size())
            animation = {'good': ('#4CAF50', -15, QPoint(0, 0)), 'mid': ('#2196F3', 15, QPoint(0, 0)), 'bad': ('#F44336', 0, QPoint(0, 450))}[category_key]
            PreviewOverlayWidget(self, pixmap.copy(), geom, animation[0], animation[1], animation[2])
        self._refresh_state()

    def _on_list_item_clicked(self, item):
        row = self.preview_ui.file_list.row(item)
        if row > 0:
            self.logic.move_to_front(row)
            self._refresh_state()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in self.key_map:
            self.sort_current(self.key_map[event.key()])
        else:
            super().keyPressEvent(event)
