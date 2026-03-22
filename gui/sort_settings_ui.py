from pathlib import Path

from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from core.sort_settings_logic import SettingsLogic
from gui.sort_settings_info_ui import SettingsInfoUI
from gui.sort_settings_language_ui import SettingsLanguageUI
from gui.sort_theme_selector_ui import ThemeSelectorUI


class SettingsUI(QFrame):
    language_changed = Signal(str)
    theme_changed = Signal(str)
    close_requested = Signal()

    def __init__(self, version: str, parent=None):
        super().__init__(parent)
        self.version = version
        self.setObjectName('narrowPanel')
        self.setFixedWidth(60)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(20)
        self.btn_info = self._create_button(); self._set_logo_icon(self.btn_info)
        self.btn_info.clicked.connect(self.show_info_dialog)
        self.btn_language = self._create_icon_button('languages.png')
        self.btn_language.clicked.connect(self.show_language_dialog)
        self.btn_theme = self._create_icon_button('settings.png')
        self.btn_theme.clicked.connect(self.show_theme_dialog)
        self.btn_close = self._create_icon_button('exit.png')
        self.btn_close.setProperty('danger', True)
        self.btn_close.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.btn_info, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        layout.addWidget(self.btn_language, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.btn_theme, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.btn_close, 0, Qt.AlignmentFlag.AlignHCenter)
        self.retranslate_ui()

    def _create_button(self, text: str = '') -> QPushButton:
        button = QPushButton(text)
        button.setObjectName('iconButton')
        button.setFixedSize(55, 55)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def _create_icon_button(self, filename: str) -> QPushButton:
        button = self._create_button()
        path = Path(__file__).resolve().parent.parent / 'assets' / 'icons' / filename
        if path.exists():
            pixmap = QPixmap(str(path))
            cropped = self._crop_alpha(pixmap)
            if not cropped.isNull():
                button.setIcon(QIcon(cropped))
                button.setIconSize(QSize(48, 48))
        return button

    def _crop_alpha(self, pixmap: QPixmap) -> QPixmap:
        if pixmap.isNull():
            return pixmap
        image = pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
        w, h = image.width(), image.height()
        points = [(x, y) for y in range(h) for x in range(w) if (image.pixel(x, y) >> 24) & 0xFF > 5]
        if not points:
            return pixmap
        xs, ys = zip(*points)
        return pixmap.copy(QRect(min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))

    def _set_logo_icon(self, button: QPushButton):
        path = Path(__file__).resolve().parent.parent / 'assets' / 'ASORT.png'
        if path.exists():
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                button.setIcon(QIcon(pixmap))
                button.setIconSize(QSize(48, 48))
                return
        button.setText('ⓘ')

    def retranslate_ui(self):
        self.btn_info.setToolTip(SettingsLogic.tr('info_title', 'Info'))
        self.btn_language.setToolTip(SettingsLogic.tr('label_language', 'Language'))
        self.btn_theme.setToolTip(SettingsLogic.tr('label_theme', 'Theme'))
        self.btn_close.setToolTip(SettingsLogic.tr('btn_close', 'Close'))

    def show_info_dialog(self):
        SettingsInfoUI(self.version, self.window().styleSheet(), self).exec()

    def show_language_dialog(self):
        dialog = SettingsLanguageUI(self)
        dialog.setStyleSheet(self.window().styleSheet())
        dialog.language_selected.connect(self._apply_language)
        dialog.exec()

    def show_theme_dialog(self):
        dialog = ThemeSelectorUI(self)
        dialog.setStyleSheet(self.window().styleSheet())
        dialog.theme_selected.connect(self._apply_theme)
        dialog.exec()

    def _apply_language(self, code: str):
        SettingsLogic.set_language(code)
        self.language_changed.emit(code)

    def _apply_theme(self, code: str):
        SettingsLogic.set_theme(code)
        self.theme_changed.emit(code)
