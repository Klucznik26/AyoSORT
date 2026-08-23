# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Klucznik MZ
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from core.sort_settings_logic import SettingsLogic


class CategoryNamesUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumSize(420, 340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_container = QWidget(self)
        self.main_container.setObjectName("categoryNamesRoot")
        layout.addWidget(self.main_container)

        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(16, 16, 16, 16)

        self.panel = QFrame(self.main_container)
        self.panel.setObjectName("categoryNamesPanel")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(16, 16, 16, 16)
        panel_layout.setSpacing(12)
        container_layout.addWidget(self.panel)

        self.title_label = QLabel(SettingsLogic.tr("category_names_title", "Kategorie sortowania"))
        title_font = self.title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        panel_layout.addWidget(self.title_label)

        self.description_label = QLabel(
            SettingsLogic.tr(
                "category_names_description",
                "Podaj własne nazwy trzech kategorii. Puste pole przywraca nazwę domyślną.",
            )
        )
        self.description_label.setWordWrap(True)
        panel_layout.addWidget(self.description_label)

        self.good_label = QLabel(SettingsLogic.tr("category_name_good", "Kategoria A"))
        self.good_input = QLineEdit()
        panel_layout.addWidget(self.good_label)
        panel_layout.addWidget(self.good_input)

        self.mid_label = QLabel(SettingsLogic.tr("category_name_mid", "Kategoria B"))
        self.mid_input = QLineEdit()
        panel_layout.addWidget(self.mid_label)
        panel_layout.addWidget(self.mid_input)

        self.bad_label = QLabel(SettingsLogic.tr("category_name_bad", "Kategoria C"))
        self.bad_input = QLineEdit()
        panel_layout.addWidget(self.bad_label)
        panel_layout.addWidget(self.bad_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        panel_layout.addWidget(self.button_box)

        self._load_values()
        self._apply_styles()
        self.retranslate_ui()

    def _load_values(self):
        values = SettingsLogic.get_category_names()
        self.good_input.setText(values.get("good", ""))
        self.mid_input.setText(values.get("mid", ""))
        self.bad_input.setText(values.get("bad", ""))

    def _apply_styles(self):
        self.main_container.setStyleSheet(
            "#categoryNamesRoot { background-color: rgba(10, 25, 20, 0.30); border-radius: 26px; }"
        )
        self.panel.setStyleSheet(
            "#categoryNamesPanel { background-color: rgba(19, 29, 37, 0.94); border-radius: 18px; border: 1px solid rgba(4, 227, 138, 0.20); }"
            "QLabel { color: #CFE8DC; background: transparent; border: none; }"
            "QLineEdit { background-color: #121917; color: #CFE8DC; border: 1px solid #25332D; border-radius: 8px; padding: 8px 10px; }"
            "QLineEdit:focus { border: 1px solid #04E38A; background-color: #161D1A; }"
            "QPushButton { background-color: #1C2622; color: #1AA178; border: 1px solid #25332D; border-radius: 8px; padding: 8px 12px; }"
            "QPushButton:hover { background-color: #1F3A30; border: 1px solid #04E38A; color: #E6FFF6; }"
            "QPushButton:pressed { background-color: #04E38A; color: #0F1412; }"
        )

    def retranslate_ui(self):
        self.title_label.setText(SettingsLogic.tr("category_names_title", "Kategorie sortowania"))
        self.description_label.setText(
            SettingsLogic.tr(
                "category_names_description",
                "Podaj własne nazwy trzech kategorii. Puste pole przywraca nazwę domyślną.",
            )
        )
        self.good_label.setText(SettingsLogic.tr("category_name_good", "Kategoria A"))
        self.mid_label.setText(SettingsLogic.tr("category_name_mid", "Kategoria B"))
        self.bad_label.setText(SettingsLogic.tr("category_name_bad", "Kategoria C"))
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText(SettingsLogic.tr("btn_ok", "OK"))
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(SettingsLogic.tr("btn_cancel", "Cancel"))

    def accept(self):
        try:
            SettingsLogic.set_category_names(
                {
                    "good": self.good_input.text(),
                    "mid": self.mid_input.text(),
                    "bad": self.bad_input.text(),
                }
            )
        except (OSError, ValueError) as exc:
            QMessageBox.warning(
                self,
                SettingsLogic.tr("error_title", "Error"),
                SettingsLogic.tr(
                    "msg_invalid_category_names",
                    "Category names must be different and cannot be “.” or “..”.",
                )
                + f"\n\n{exc}",
            )
            return
        super().accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
