# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Marek Zubrzycki (Klucznik MZ)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QPushButton

from core.sort_icon_crop_logic import crop_alpha_pixmap


class ThemeSelectorOptionUI(QPushButton):
    hovered = Signal(str, str)
    left = Signal()

    def __init__(self, icon_path, theme_name, code, is_top=False, glow_color="#FFFFFF", parent=None):
        super().__init__("", parent)
        self.theme_name = theme_name
        self.code = code
        self._hovered = False
        self._selected = False
        original = QPixmap(icon_path)
        normal_target = 195 if is_top else 171
        hover_target = 205 if is_top else 180
        self.pix_normal = crop_alpha_pixmap(
            original.scaled(
                normal_target,
                normal_target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.pix_hover = crop_alpha_pixmap(
            original.scaled(
                hover_target,
                hover_target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.setFixedSize(self.pix_hover.width(), self.pix_hover.height())
        self.setFlat(True)
        self.setStyleSheet("background: transparent; border: none;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(12)
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)
        self._apply_shadow(glow_color, 50, 12)

    def _apply_shadow(self, glow_color, alpha, blur):
        color = QColor(glow_color)
        color.setAlpha(alpha)
        self.shadow.setColor(color)
        self.shadow.setBlurRadius(blur)

    def set_selected(self, selected):
        self._selected = selected
        self._apply_shadow("#FFFFFF", 160 if selected else 50, 25 if selected else 12)
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self.raise_()
        self.update()
        self.hovered.emit(self.theme_name, self.code)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        self.left.emit()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = self.pix_hover if self._hovered else self.pix_normal
        painter.drawPixmap((self.width() - pixmap.width()) // 2, (self.height() - pixmap.height()) // 2, pixmap)
