import os

from PySide6.QtWidgets import QMainWindow

from core.engine import AyoSortEngine
from core.translator import translator
from .main_window_actions import MainWindowActions
from .main_window_layout import build_ui


class MainWindow(MainWindowActions, QMainWindow):
    VERSION = "1.3.1"

    def __init__(self):
        super().__init__()
        self.engine = AyoSortEngine()
        self.current_pixmap = None
        self.current_theme_name = self.engine.current_theme

        self.setWindowTitle(f"{translator.get('window_title')} v{self.VERSION}")
        self.setMinimumSize(1000, 700)
        self.resize(1000, 700)
        self.setAcceptDrops(True)

        translator.load_language(self.engine.current_language)
        translator.language_changed.connect(self._update_ui_texts)

        build_ui(self)
        self.apply_theme(self.current_theme_name)
        self._check_initial_state()

    def load_logo(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "assets", "AyoSORT.png")
        if os.path.exists(logo_path):
            pixmap = self._load_logo_pixmap(logo_path)
            if pixmap is not None:
                self.mini_logo.setPixmap(pixmap)
                return
        self.mini_logo.setText(f"AyoSORT v{self.VERSION}")
        self.mini_logo.setStyleSheet("font-weight: bold;")

    @staticmethod
    def _load_logo_pixmap(path):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPixmap

        pixmap = QPixmap(path)
        if pixmap.isNull():
            return None
        return pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    def _update_ui_texts(self):
        self.setWindowTitle(f"{translator.get('window_title')} v{self.VERSION}")
        self.btn_create_catalog.setText(translator.get("btn_create_catalog"))
        self.btn_select_folder.setText(translator.get("btn_select_folder"))
        self.btn_good.setToolTip(translator.get("tooltip_good"))
        self.btn_mid.setToolTip(translator.get("tooltip_mid"))
        self.btn_bad.setToolTip(translator.get("tooltip_bad"))
        self.label_info_create.setText(translator.get("label_info_create"))
        self.label_info_select.setText(translator.get("label_info_select"))

        self.btn_narrow_logo.setToolTip(translator.get("info_title", "Info"))
        self.btn_narrow_lang.setToolTip(translator.get("label_language", "Language"))
        self.btn_narrow_settings.setToolTip(translator.get("label_theme", "Theme"))
        self.btn_narrow_close.setToolTip(translator.get("btn_close", "Close"))

        if self.current_pixmap is None:
            self.drop_area.setText(translator.get("drop_label_text"))

        if self.engine.has_images():
            self.file_count_label.setText(translator.get("label_file_count").format(count=len(self.engine.images)))

    @property
    def current_language(self):
        return self.engine.current_language

    def _check_initial_state(self):
        if self.engine.destination_folder and os.path.exists(self.engine.destination_folder):
            self.label_info_create.setVisible(False)
