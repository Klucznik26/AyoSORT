# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Marek Zubrzycki (Klucznik MZ)
from math import pi, sin
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QRect, QSize, Qt, QUrl, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QDesktopServices, QPainter, QPixmap
from PySide6.QtWidgets import QAbstractButton, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from core.sort_icon_crop_logic import crop_alpha_pixmap
from core.sort_settings_logic import SettingsLogic


class SortIconButton(QAbstractButton):
    def __init__(self, pixmap: QPixmap, accent_color: str, parent=None):
        super().__init__(parent)
        self._icon_size = QSize(52, 52)
        self._pixmap = self._prepare_pixmap(pixmap)
        self._accent = QColor(accent_color)
        self._angle = 0.0
        self._scale = 1.0
        self._glow = 0.0
        self._spin = QVariantAnimation(self)
        self._spin.setStartValue(0.0)
        self._spin.setEndValue(1.0)
        self._spin.setDuration(340)
        self._spin.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._spin.valueChanged.connect(self._update_animation)
        self.clicked.connect(self._play_spin)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(56, 56)

    def _prepare_pixmap(self, pixmap: QPixmap) -> QPixmap:
        if pixmap.isNull():
            return QPixmap()
        cropped = crop_alpha_pixmap(pixmap)
        if cropped.isNull():
            return QPixmap()
        return cropped.scaled(
            self._icon_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _update_animation(self, value):
        progress = float(value)
        self._angle = 360.0 * progress
        self._scale = 1.0 + (0.16 * sin(pi * progress))
        self._glow = sin(pi * progress)
        self.update()

    def _play_spin(self):
        if not self.isEnabled() or self._pixmap.isNull():
            return
        self._spin.stop()
        self._spin.setStartValue(0.0)
        self._spin.setEndValue(1.0)
        self._spin.start()

    def sizeHint(self) -> QSize:
        return QSize(56, 56)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        hover_strength = 0.22 if self.underMouse() else 0.0
        glow_strength = max(hover_strength, self._glow)
        if glow_strength > 0:
            glow_color = QColor(self._accent)
            glow_color.setAlphaF(min(0.38, 0.10 + (0.22 * glow_strength)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow_color)
            painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 12, 12)

        if self._pixmap.isNull():
            return

        if not self.isEnabled():
            painter.setOpacity(0.35)
        elif self.isDown():
            painter.setOpacity(0.82)

        center = self.rect().center()
        painter.translate(center)
        painter.rotate(self._angle)
        painter.scale(self._scale, self._scale)
        target = QRect(0, 0, self._pixmap.width(), self._pixmap.height())
        target.moveCenter(QRect(self.rect()).translated(-center).center())
        painter.drawPixmap(target, self._pixmap)


class BatchUI(QFrame):
    create_catalog_requested = Signal()
    select_folder_requested = Signal()
    category_names_requested = Signal()
    sort_requested = Signal(str)
    undo_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("leftPanel")
        self.setFixedWidth(200)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(8)

        self.btn_create_catalog = QPushButton()
        self.btn_create_catalog.setObjectName("runButton")
        self.btn_create_catalog.setMinimumHeight(60)
        self.btn_create_catalog.clicked.connect(self.create_catalog_requested.emit)

        self.btn_select_folder = QPushButton()
        self.btn_select_folder.setObjectName("runButton")
        self.btn_select_folder.setMinimumHeight(60)
        self.btn_select_folder.clicked.connect(self.select_folder_requested.emit)

        self.btn_category_names = QPushButton()
        self.btn_category_names.setObjectName("runButton")
        self.btn_category_names.setMinimumHeight(60)
        self.btn_category_names.clicked.connect(self.category_names_requested.emit)

        self.btn_undo = QPushButton()
        self.btn_undo.setObjectName("runButton")
        self.btn_undo.setMinimumHeight(44)
        self.btn_undo.clicked.connect(self.undo_requested.emit)

        layout.addWidget(self.btn_create_catalog)
        layout.addWidget(self.btn_select_folder)
        layout.addWidget(self.btn_category_names)

        self.destination_panel = QFrame(self)
        self.destination_panel.setObjectName("destinationBanner")
        destination_layout = QVBoxLayout(self.destination_panel)
        destination_layout.setContentsMargins(9, 8, 9, 8)
        destination_layout.setSpacing(3)
        self.destination_title = QLabel()
        self.destination_title.setObjectName("destinationTitle")
        self.destination_title.setWordWrap(True)
        self.destination_path = QLabel()
        self.destination_path.setObjectName("destinationPath")
        self.destination_path.setWordWrap(True)
        self.destination_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.destination_mode = QLabel()
        self.destination_mode.setProperty("secondary", True)
        self.destination_mode.setWordWrap(True)
        self.btn_open_destination = QPushButton()
        self.btn_open_destination.clicked.connect(self._open_destination)
        destination_layout.addWidget(self.destination_title)
        destination_layout.addWidget(self.destination_path)
        destination_layout.addWidget(self.destination_mode)
        destination_layout.addWidget(self.btn_open_destination)
        layout.addWidget(self.destination_panel)

        sort_layout = QHBoxLayout()
        sort_layout.setSpacing(6)
        sort_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_good = self._create_sort_button("excellent.png", "good", "#4CAF50")
        self.btn_mid = self._create_sort_button("good.png", "mid", "#2196F3")
        self.btn_bad = self._create_sort_button("poor.png", "bad", "#F44336")
        for button in (self.btn_good, self.btn_mid, self.btn_bad):
            sort_layout.addWidget(button)
        layout.addLayout(sort_layout)
        layout.addWidget(self.btn_undo)
        layout.addStretch()
        self._destination = None
        self._destination_fixed = False
        self._destination_available = False
        self._categories = []
        self.retranslate_ui()
        self.set_destination_info(None, False, [], False)
        self.set_sort_enabled(False)

    def _create_sort_button(self, icon_filename: str, code: str, accent_color: str) -> SortIconButton:
        icon_path = Path(__file__).resolve().parent.parent / "assets" / "icons" / icon_filename
        pixmap = QPixmap(str(icon_path)) if icon_path.exists() else QPixmap()
        button = SortIconButton(pixmap, accent_color, self)
        button.clicked.connect(lambda _checked=False, key=code: self.sort_requested.emit(key))
        return button

    def retranslate_ui(self):
        category_names = SettingsLogic.get_category_display_names()
        self.btn_create_catalog.setText(SettingsLogic.tr("btn_create_catalog"))
        self.btn_select_folder.setText(SettingsLogic.tr("btn_select_folder"))
        self.btn_category_names.setText(SettingsLogic.tr("btn_category_names", "Kategorie\nsortowania"))
        self.btn_undo.setText(SettingsLogic.tr("btn_undo", "Undo"))
        self.btn_good.setToolTip(category_names["good"])
        self.btn_mid.setToolTip(category_names["mid"])
        self.btn_bad.setToolTip(category_names["bad"])
        self.retranslate_destination()

    def retranslate_destination(self):
        self.destination_title.setText(SettingsLogic.tr("destination_title", "Sorted images will be copied to:"))
        self.btn_open_destination.setText(SettingsLogic.tr("destination_open", "Open folder"))
        self._render_destination()

    def set_destination_info(self, path: str | None, fixed: bool, categories: list[str], available: bool):
        self._destination = path
        self._destination_fixed = fixed
        self._destination_available = available
        self._categories = categories
        self._render_destination()

    def _render_destination(self):
        if self._destination:
            self.destination_path.setText(self._destination)
            self.destination_path.setToolTip(self._destination)
            if self._destination_fixed and not self._destination_available:
                mode = SettingsLogic.tr("msg_error_access", "Access error: {e}").format(e=self._destination)
            else:
                mode_key = "destination_fixed" if self._destination_fixed else "destination_source"
                mode_default = "Selected destination" if self._destination_fixed else "SORT folder next to source"
                mode = SettingsLogic.tr(mode_key, mode_default)
            categories = " • ".join(self._categories)
            self.destination_mode.setText(f"{mode}\n{categories}" if categories else mode)
            self.btn_open_destination.setEnabled(self._destination_available and Path(self._destination).is_dir())
        else:
            self.destination_path.setText(SettingsLogic.tr("destination_pending", "Select source or destination"))
            self.destination_path.setToolTip("")
            self.destination_mode.setText(SettingsLogic.tr("destination_pending_hint", "The path will appear here."))
            self.btn_open_destination.setEnabled(False)

    def _open_destination(self):
        if self._destination and Path(self._destination).is_dir():
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._destination))

    def set_source_ready(self, ready: bool):
        self.set_sort_enabled(ready)

    def set_sort_enabled(self, enabled: bool):
        for button in (self.btn_good, self.btn_mid, self.btn_bad):
            button.setEnabled(enabled)

    def set_undo_enabled(self, enabled: bool):
        self.btn_undo.setEnabled(enabled)

    def set_busy(self, busy: bool):
        self.btn_create_catalog.setEnabled(not busy)
        self.btn_select_folder.setEnabled(not busy)
        self.btn_category_names.setEnabled(not busy)
        if busy:
            self.set_sort_enabled(False)
            self.set_undo_enabled(False)
