# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Marek Zubrzycki (Klucznik MZ)
from PySide6.QtCore import QPoint, QRect, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QToolButton, QVBoxLayout

from core.sort_image_metadata import read_image_metadata
from core.sort_settings_logic import SettingsLogic
from core.sort_theme_selector_logic import ThemeSelectorLogic
from gui.sort_file_drop_widgets import FileDropLabel
from gui.sort_image_viewer_ui import FullScreenImageDialog


class ViewerToolButton(QToolButton):
    def __init__(self, icon_kind: str, parent=None):
        super().__init__(parent)
        self.icon_kind = icon_kind
        self.setFixedHeight(30)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        super().paintEvent(event)
        theme = ThemeSelectorLogic.get_theme()
        color = theme.get("text", "#FFFFFF") if self.isEnabled() else theme.get("text_muted", "#A0A0A0")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(color), 1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        center_x = self.width() / 2
        center_y = self.height() / 2

        if self.icon_kind in {"zoom_out", "zoom_in"}:
            lens = QRectF(center_x - 9, center_y - 8, 13, 13)
            painter.drawEllipse(lens)
            painter.drawLine(QPoint(round(center_x + 2), round(center_y + 4)), QPoint(round(center_x + 9), round(center_y + 10)))
            painter.drawLine(QPoint(round(center_x - 6), round(center_y - 1.5)), QPoint(round(center_x + 1), round(center_y - 1.5)))
            if self.icon_kind == "zoom_in":
                painter.drawLine(QPoint(round(center_x - 2.5), round(center_y - 5)), QPoint(round(center_x - 2.5), round(center_y + 2)))
        elif self.icon_kind == "actual":
            font = painter.font()
            font.setBold(True)
            font.setPixelSize(12)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "1:1")
        elif self.icon_kind in {"fit", "fullscreen"}:
            left, right = center_x - 9, center_x + 9
            top, bottom = center_y - 8, center_y + 8
            length = 6
            if self.icon_kind == "fullscreen":
                segments = (
                    (left, top + length, left, top, left + length, top),
                    (right - length, top, right, top, right, top + length),
                    (left, bottom - length, left, bottom, left + length, bottom),
                    (right - length, bottom, right, bottom, right, bottom - length),
                )
            else:
                inset = 4
                segments = (
                    (left, top + inset, left + inset, top + inset, left + inset, top),
                    (right - inset, top, right - inset, top + inset, right, top + inset),
                    (left, bottom - inset, left + inset, bottom - inset, left + inset, bottom),
                    (right - inset, bottom, right - inset, bottom - inset, right, bottom - inset),
                )
            for x1, y1, x2, y2, x3, y3 in segments:
                painter.drawLine(QPoint(round(x1), round(y1)), QPoint(round(x2), round(y2)))
                painter.drawLine(QPoint(round(x2), round(y2)), QPoint(round(x3), round(y3)))
        elif self.icon_kind == "compare":
            painter.drawRoundedRect(QRectF(center_x - 11, center_y - 8, 9, 16), 2, 2)
            painter.drawRoundedRect(QRectF(center_x + 2, center_y - 8, 9, 16), 2, 2)
            painter.drawLine(QPoint(round(center_x - 1), round(center_y)), QPoint(round(center_x + 1), round(center_y)))


class FileDropUI(QFrame):
    compare_requested = Signal()

    def __init__(self, on_drop_callback=None, parent=None):
        super().__init__(parent)
        self.setObjectName("rightPanel")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(5)
        self.btn_zoom_out = self._tool_button("zoom_out", lambda: self.drop_label.zoom_by(1 / 1.2))
        self.btn_zoom_in = self._tool_button("zoom_in", lambda: self.drop_label.zoom_by(1.2))
        self.btn_actual = self._tool_button("actual", self._actual_size)
        self.btn_fit = self._tool_button("fit", self._fit)
        self.btn_fullscreen = self._tool_button("fullscreen", self._show_fullscreen)
        self.btn_compare = self._tool_button("compare", self.compare_requested.emit)
        for button in (
            self.btn_zoom_out,
            self.btn_zoom_in,
            self.btn_actual,
            self.btn_fit,
            self.btn_fullscreen,
            self.btn_compare,
        ):
            toolbar.addWidget(button, 1)
        layout.addLayout(toolbar)
        self.drop_label = FileDropLabel(on_drop_callback, self)
        self.drop_label.setObjectName("dropArea")
        layout.addWidget(self.drop_label, 1)
        self.metadata_label = QLabel()
        self.metadata_label.setObjectName("imageMetadata")
        self.metadata_label.setWordWrap(True)
        self.metadata_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.metadata_label)
        self._metadata = None
        self._fullscreen_dialog = None
        self._set_view_actions_enabled(False)

    def _tool_button(self, icon_kind, callback):
        button = ViewerToolButton(icon_kind, self)
        button.clicked.connect(callback)
        return button

    def _actual_size(self):
        self.drop_label.actual_size()

    def _fit(self):
        self.drop_label.fit_to_window()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # The panel width is part of AyoSORT's original four-column composition.
        # Keep it based on the full panel height; viewer controls must not alter
        # the proportions designed for the vertical panels.
        original_drop_height = event.size().height() - 30
        available_view_height = event.size().height() - 175
        if original_drop_height <= 0 or available_view_height <= 0:
            return
        drop_width = int(original_drop_height * (2 / 3))
        panel_width = drop_width + 30
        if self.width() != panel_width:
            self.setFixedWidth(panel_width)
        self.drop_label.setFixedSize(drop_width, available_view_height)

    def retranslate_ui(self):
        self.drop_label.retranslate_ui()
        tips = (
            (self.btn_zoom_out, "viewer_zoom_out_button", "Zoom out"),
            (self.btn_zoom_in, "viewer_zoom_in_button", "Zoom in"),
            (self.btn_actual, "viewer_actual_size_button", "Actual size"),
            (self.btn_fit, "viewer_fit_button", "Fit to window"),
            (self.btn_fullscreen, "viewer_fullscreen_button", "Full screen"),
            (self.btn_compare, "viewer_compare_button", "Compare"),
        )
        for button, key, fallback in tips:
            translated = SettingsLogic.tr(key, fallback)
            button.setToolTip(translated)
            button.setAccessibleName(translated)
        self._render_metadata()

    def show_preview(self, path: str):
        self.drop_label.set_image_path(path)
        self._metadata = read_image_metadata(path)
        self._render_metadata()
        self._set_view_actions_enabled(self.drop_label.source_pixmap is not None)

    def show_finished(self):
        self.drop_label.clear_preview(SettingsLogic.tr("label_end_sorting"))
        self._metadata = None
        self._render_metadata()
        self._set_view_actions_enabled(False)

    def reset_preview(self):
        self.drop_label.clear_preview()
        self._metadata = None
        self._render_metadata()
        self._set_view_actions_enabled(False)

    def current_pixmap(self):
        return self.drop_label.displayed_pixmap()

    def _set_view_actions_enabled(self, enabled: bool):
        for button in (self.btn_zoom_out, self.btn_zoom_in, self.btn_actual, self.btn_fit, self.btn_fullscreen):
            button.setEnabled(enabled)
        self.btn_compare.setEnabled(enabled)

    def set_compare_enabled(self, enabled: bool):
        self.btn_compare.setEnabled(enabled and self.drop_label.source_pixmap is not None)

    def _show_fullscreen(self):
        if not self.drop_label.image_path:
            return
        self._fullscreen_dialog = FullScreenImageDialog(self.drop_label.image_path, self)
        self._fullscreen_dialog.show()

    def _render_metadata(self):
        if not self._metadata:
            self.metadata_label.clear()
            return
        data = self._metadata
        self.metadata_label.setText(
            "<b>{name}</b><br>{dimensions} · {size}<br>{camera}<br>{captured} · {exposure}".format(**data)
        )

    def preview_geometry(self, parent) -> QRect | None:
        if parent is None:
            return None
        pos = self.drop_label.mapTo(parent, QPoint(0, 0))
        return QRect(pos, self.drop_label.size())
