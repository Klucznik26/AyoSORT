import os

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QKeyEvent, QPixmap
from PySide6.QtWidgets import QFileDialog, QMessageBox

from core.translator import translator
from .animated_overlay import AnimatedOverlay
from .gui_utils import apply_dialog_theme
from .info_window import InfoWindow
from .language_window import LanguageWindow
from .settings_window import SettingsWindow
from .styles import get_style
from .theme_window import ThemeWindow


class MainWindowActions:
    def tr(self, key, default=None):
        return translator.get(key, default)

    def show_info_window(self):
        dialog = InfoWindow(self.VERSION, self.styleSheet(), self)
        dialog.exec()

    def show_language_window(self):
        dialog = LanguageWindow(translator, self)
        dialog.setStyleSheet(self.styleSheet())
        dialog.language_selected.connect(self._apply_language_code)
        dialog.exec()

    def show_theme_window(self):
        dialog = ThemeWindow(translator, self)
        dialog.setStyleSheet(self.styleSheet())
        dialog.theme_selected.connect(self._apply_theme_code)
        dialog.exec()

    def open_settings(self):
        dialog = SettingsWindow(self, current_lang=self.current_language)
        index = dialog.theme_combo.findData(self.current_theme_name)
        if index >= 0:
            dialog.theme_combo.setCurrentIndex(index)

        dialog.apply_theme(get_style(self.current_theme_name))
        dialog.theme_combo.currentTextChanged.connect(
            lambda _text: dialog.apply_theme(get_style(dialog.theme_combo.currentData()))
        )

        if dialog.exec():
            self._apply_theme_code(dialog.theme_combo.currentData())
            selected_lang_data = dialog.lang_combo.currentData()
            if selected_lang_data:
                self._apply_language_code(selected_lang_data)

    def _apply_language_code(self, lang_code):
        self.engine.set_language(lang_code)
        translator.load_language(lang_code)

    def _apply_theme_code(self, theme_code):
        self.apply_theme(theme_code)
        self.engine.set_theme(theme_code)

    def handle_drop(self, paths):
        if not paths:
            return

        if len(paths) == 1 and os.path.isdir(paths[0]):
            self.engine.source_folder = paths[0]
            self._load_images()
            self._prepare_folders()
            self._show_current_image()
            self.label_info_select.setVisible(False)
            return

        first_path = paths[0]
        if os.path.isfile(first_path):
            folder = os.path.dirname(first_path)
            self.engine.source_folder = folder

            selected_images = []
            for p in paths:
                if os.path.isfile(p) and os.path.dirname(p) == folder:
                    ext = os.path.splitext(p)[1].lower()
                    if ext in self.engine.image_extensions:
                        selected_images.append(os.path.basename(p))

            if selected_images:
                self._load_images(specific_files=selected_images)
                self._prepare_folders()
                self._show_current_image()
                self.label_info_select.setVisible(False)
            else:
                QMessageBox.information(self, self.tr("info_title"), self.tr("msg_no_images"))

    def create_sorting_catalog(self):
        dialog = QFileDialog(self, self.tr("dialog_create_title"))
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setLabelText(QFileDialog.DialogLabel.Accept, self.tr("dialog_create_accept"))
        dialog.setLabelText(QFileDialog.DialogLabel.Reject, self.tr("btn_cancel"))
        dialog.setLabelText(QFileDialog.DialogLabel.LookIn, self.tr("dialog_look_in"))
        dialog.setLabelText(QFileDialog.DialogLabel.FileName, self.tr("dialog_file_name"))
        dialog.setLabelText(QFileDialog.DialogLabel.FileType, self.tr("dialog_file_type"))
        apply_dialog_theme(dialog, get_style(self.current_theme_name))

        if dialog.exec():
            selected_files = dialog.selectedFiles()
            if selected_files:
                self.engine.set_destination_folder(selected_files[0])
                try:
                    self.engine.initialize_sorting_structure()
                    self.label_info_create.setVisible(False)
                except OSError as e:
                    QMessageBox.critical(self, self.tr("error_title"), self.tr("msg_error_create").format(e=e))

    def select_folder_to_sort(self):
        dialog = QFileDialog(self, self.tr("dialog_select_title"))
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setLabelText(QFileDialog.DialogLabel.Accept, self.tr("dialog_select_accept"))
        dialog.setLabelText(QFileDialog.DialogLabel.Reject, self.tr("btn_cancel"))
        dialog.setLabelText(QFileDialog.DialogLabel.LookIn, self.tr("dialog_look_in"))
        dialog.setLabelText(QFileDialog.DialogLabel.FileName, self.tr("dialog_file_name"))
        dialog.setLabelText(QFileDialog.DialogLabel.FileType, self.tr("dialog_file_type"))
        apply_dialog_theme(dialog, get_style(self.current_theme_name))

        if dialog.exec():
            selected_files = dialog.selectedFiles()
            if selected_files:
                self._load_images(folder_path=selected_files[0])
                self._prepare_folders()
                self._show_current_image()
                self.label_info_select.setVisible(False)

    def apply_theme(self, theme_name):
        self.current_theme_name = theme_name if theme_name else "dark"
        self.setStyleSheet(get_style(self.current_theme_name))

    def _load_images(self, specific_files=None, folder_path=None):
        try:
            if specific_files:
                self.engine.set_specific_images(self.engine.source_folder, specific_files)
            elif folder_path:
                self.engine.load_images_from_folder(folder_path)
            else:
                self.engine.load_images_from_folder(self.engine.source_folder)

            if not self.engine.has_images():
                QMessageBox.information(self, self.tr("info_title"), self.tr("msg_info_no_images_folder"))
                self.file_count_label.setVisible(False)
            else:
                random_paths = self.engine.get_random_samples()
                self.image_fan.set_images(random_paths)
                self.file_count_label.setText(self.tr("label_file_count").format(count=len(self.engine.images)))
                self.file_count_label.setVisible(len(self.engine.images) > 1)
        except OSError as e:
            QMessageBox.critical(self, self.tr("error_title"), self.tr("msg_error_access").format(e=e))

    def _prepare_folders(self):
        for folder_name in self.engine.categories.values():
            os.makedirs(os.path.join(self.engine.source_folder, folder_name), exist_ok=True)

    def _show_current_image(self):
        path = self.engine.get_current_image_path()
        if path:
            self.current_pixmap = QPixmap(path)
            if not self.current_pixmap.isNull():
                self._update_image_display()
                filename = self.engine.get_current_filename()
                self.setWindowTitle(f"AyoSORT v{self.VERSION} - {filename} ({self.engine.get_progress_string()})")
            else:
                self.drop_area.setText(self.tr("msg_error_load").format(filename=path))
        else:
            self.current_pixmap = None
            self.drop_area.setText(self.tr("label_end_sorting"))
            self.setWindowTitle(f"{self.tr('window_title_end')} v{self.VERSION}")

    def _update_image_display(self):
        if self.current_pixmap and not self.current_pixmap.isNull():
            scaled = self.current_pixmap.scaled(
                self.drop_area.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.drop_area.setPixmap(scaled)

    def sort_current(self, category_key):
        if self.engine.is_finished():
            return

        try:
            success = self.engine.sort_current_image(category_key)
            if not success:
                return
        except Exception as e:
            QMessageBox.critical(self, self.tr("error_title"), self.tr("msg_error_copy").format(e=e))
            return

        current_pixmap = self.drop_area.pixmap()
        if current_pixmap and not current_pixmap.isNull():
            pm_copy = current_pixmap.copy()
            pos = self.drop_area.mapTo(self, QPoint(0, 0))
            geom = QRect(pos, self.drop_area.size())
            if category_key == "good":
                AnimatedOverlay(self, pm_copy, geom, "#4CAF50", -15)
            elif category_key == "mid":
                AnimatedOverlay(self, pm_copy, geom, "#2196F3", 15)
            elif category_key == "bad":
                AnimatedOverlay(self, pm_copy, geom, "#F44336", 0, QPoint(0, 450))

        self._show_current_image()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in self.key_map:
            self.sort_current(self.key_map[event.key()])
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        self._update_image_display()
        super().resizeEvent(event)
