from pathlib import Path

from PySide6.QtCore import QAbstractAnimation, QEasingCurve, QEvent, QPropertyAnimation, QRect, QSequentialAnimationGroup, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QImage, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from core.sort_settings_logic import SettingsLogic


class BatchUI(QFrame):
    create_catalog_requested = Signal()
    select_folder_requested = Signal()
    sort_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('leftPanel')
        self.setFixedWidth(200)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(8)
        self.btn_create_catalog = QPushButton()
        self.btn_create_catalog.setObjectName('runButton')
        self.btn_create_catalog.setMinimumHeight(60)
        self.btn_create_catalog.clicked.connect(self.create_catalog_requested.emit)
        self.btn_select_folder = QPushButton()
        self.btn_select_folder.setObjectName('runButton')
        self.btn_select_folder.setMinimumHeight(60)
        self.btn_select_folder.clicked.connect(self.select_folder_requested.emit)
        layout.addWidget(self.btn_create_catalog)
        layout.addWidget(self.btn_select_folder)
        sort_layout = QHBoxLayout()
        self.btn_good = self._create_sort_button('excellent.png', 'good')
        self.btn_mid = self._create_sort_button('good.png', 'mid')
        self.btn_bad = self._create_sort_button('poor.png', 'bad')
        for button in (self.btn_good, self.btn_mid, self.btn_bad):
            sort_layout.addWidget(button)
        layout.addLayout(sort_layout)
        layout.addStretch()
        self.retranslate_ui()
        self.set_sort_enabled(False)

    def _create_sort_button(self, icon_filename: str, code: str) -> QPushButton:
        button = QPushButton()
        button.setObjectName('iconButton')
        button.setStyleSheet('QPushButton { background: transparent; border: none; } QPushButton:hover { background: transparent; border: none; }')
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(0)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 105, 62, 0))
        button.setGraphicsEffect(shadow)
        button.installEventFilter(self)
        icon_path = Path(__file__).resolve().parent.parent / 'assets' / 'icons' / icon_filename
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            cropped = self._crop_alpha(pixmap)
            if not cropped.isNull():
                button.setIcon(QIcon(cropped))
                button.setIconSize(QSize(52, 52))
        button.clicked.connect(lambda _checked=False, btn=button, key=code: self._on_sort_clicked(btn, key))
        return button

    def _on_sort_clicked(self, button: QPushButton, code: str):
        group = QSequentialAnimationGroup(button)
        
        anim_out = QPropertyAnimation(button, b"iconSize")
        anim_out.setDuration(120)
        anim_out.setStartValue(QSize(52, 52))
        anim_out.setEndValue(QSize(0, 52))
        anim_out.setEasingCurve(QEasingCurve.Type.InQuad)
        
        anim_in = QPropertyAnimation(button, b"iconSize")
        anim_in.setDuration(120)
        anim_in.setStartValue(QSize(0, 52))
        anim_in.setEndValue(QSize(52, 52))
        anim_in.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        group.addAnimation(anim_out)
        group.addAnimation(anim_in)
        group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        
        self.sort_requested.emit(code)

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

    def retranslate_ui(self):
        self.btn_create_catalog.setText(SettingsLogic.tr('btn_create_catalog'))
        self.btn_select_folder.setText(SettingsLogic.tr('btn_select_folder'))
        self.btn_good.setToolTip(SettingsLogic.tr('tooltip_good'))
        self.btn_mid.setToolTip(SettingsLogic.tr('tooltip_mid'))
        self.btn_bad.setToolTip(SettingsLogic.tr('tooltip_bad'))

    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton) and obj.graphicsEffect():
            if event.type() == QEvent.Type.Enter:
                effect = obj.graphicsEffect()
                effect.setBlurRadius(40)
                effect.setColor(QColor(0, 120, 70, 255))  # Mocniejszy szmaragdowy
            elif event.type() == QEvent.Type.Leave:
                effect = obj.graphicsEffect()
                effect.setBlurRadius(0)
                effect.setColor(QColor(0, 105, 62, 0))
        return super().eventFilter(obj, event)

    def set_destination_ready(self, ready: bool):
        pass

    def set_source_ready(self, ready: bool):
        self.set_sort_enabled(ready)

    def set_sort_enabled(self, enabled: bool):
        for button in (self.btn_good, self.btn_mid, self.btn_bad):
            button.setEnabled(enabled)
