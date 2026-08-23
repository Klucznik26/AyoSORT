# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Klucznik MZ
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFrame, QMessageBox, QPushButton, QVBoxLayout

from core.sort_icon_crop_logic import crop_alpha_pixmap
from core.sort_settings_logic import SettingsLogic


class SettingsUI(QFrame):
    language_changed = Signal(str)
    theme_changed = Signal(str)
    close_requested = Signal()

    def __init__(self, version: str, parent=None):
        super().__init__(parent)
        self.version = version
        self.setObjectName("narrowPanel")
        self.setFixedWidth(60)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(20)
        self.btn_info = self._create_button()
        self.btn_info.clicked.connect(self.show_info_dialog)
        self.btn_language = self._create_button()
        self.btn_language.clicked.connect(self.show_language_dialog)
        self.btn_theme = self._create_button()
        self.btn_theme.clicked.connect(self.show_theme_dialog)
        self.btn_close = self._create_button()
        self.btn_close.setProperty("danger", True)
        self.btn_close.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.btn_info, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        layout.addWidget(self.btn_language, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.btn_theme, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.btn_close, 0, Qt.AlignmentFlag.AlignHCenter)
        self.retranslate_ui()
        QTimer.singleShot(0, self._load_icons)

    def _create_button(self, text: str = "") -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("iconButton")
        button.setFixedSize(55, 55)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def _load_icons(self):
        self._set_logo_icon(self.btn_info)
        self._set_icon(self.btn_language, "languages.png")
        self._set_icon(self.btn_theme, "settings.png")
        self._set_icon(self.btn_close, "exit.png")

    def _set_icon(self, button: QPushButton, filename: str):
        path = Path(__file__).resolve().parent.parent / "assets" / "icons" / filename
        if not path.exists():
            return
        pixmap = QPixmap(str(path))
        cropped = crop_alpha_pixmap(pixmap)
        if not cropped.isNull():
            button.setIcon(QIcon(cropped))
            button.setIconSize(QSize(48, 48))

    def _set_logo_icon(self, button: QPushButton):
        path = Path(__file__).resolve().parent.parent / "assets" / "ASORT.png"
        if path.exists():
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                button.setIcon(QIcon(pixmap))
                button.setIconSize(QSize(48, 48))
                return
        button.setText("ⓘ")

    def retranslate_ui(self):
        self.btn_info.setToolTip(SettingsLogic.tr("info_title", "Info"))
        self.btn_language.setToolTip(SettingsLogic.tr("label_language", "Language"))
        self.btn_theme.setToolTip(SettingsLogic.tr("label_theme", "Theme"))
        self.btn_close.setToolTip(SettingsLogic.tr("btn_close", "Close"))

    def show_info_dialog(self):
        from gui.sort_settings_info_ui import SettingsInfoUI

        SettingsInfoUI(self.version, self.window().styleSheet(), self).exec()

    def show_language_dialog(self):
        from gui.sort_settings_language_ui import SettingsLanguageUI

        dialog = SettingsLanguageUI(self)
        dialog.setStyleSheet(self.window().styleSheet())
        dialog.language_selected.connect(self._apply_language)
        dialog.exec()

    def show_theme_dialog(self):
        from gui.sort_theme_selector_ui import ThemeSelectorUI

        dialog = ThemeSelectorUI(self)
        dialog.setStyleSheet(self.window().styleSheet())
        dialog.theme_selected.connect(self._apply_theme)
        dialog.exec()

    def _apply_language(self, code: str):
        try:
            SettingsLogic.set_language(code)
        except OSError as exc:
            QMessageBox.critical(self, SettingsLogic.tr("error_title", "Error"), str(exc))
            return
        self.language_changed.emit(code)

    def _apply_theme(self, code: str):
        try:
            SettingsLogic.set_theme(code)
        except OSError as exc:
            QMessageBox.critical(self, SettingsLogic.tr("error_title", "Error"), str(exc))
            return
        self.theme_changed.emit(code)
