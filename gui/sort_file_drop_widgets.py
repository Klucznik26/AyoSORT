import re

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QImageReader,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPixmap,
    QRadialGradient,
    QWheelEvent,
)
from PySide6.QtWidgets import QLabel, QSizePolicy

from core.sort_settings_logic import SettingsLogic
from core.sort_theme_selector_logic import ThemeSelectorLogic

THEME_DROP_RECIPES = {
    "dark": {
        "base_key": "bg_panel_alt",
        "primary_key": "accent",
        "secondary_key": "button_hover",
        "border_key": "border",
    },
    "light": {
        "base_key": "bg_panel_alt",
        "primary_key": "accent",
        "secondary_key": "button_hover",
        "border_key": "border",
    },
    "creative": {
        "base_key": "bg_panel_alt",
        "primary_key": "accent",
        "secondary_key": "button_pressed",
        "border_key": "border",
    },
    "relax": {
        "base_key": "bg_panel_alt",
        "primary_key": "accent",
        "secondary_key": "button_hover",
        "border_key": "border",
    },
    "arctic": {
        "base_key": "bg_panel_alt",
        "primary_key": "accent_hover",
        "secondary_key": "accent",
        "border_key": "border",
    },
    "system": {
        "base_key": "field_bg",
        "primary_key": "accent",
        "secondary_key": "hover",
        "border_key": "border",
    },
}


class FileDropLabel(QLabel):
    def __init__(self, on_drop_callback=None, parent=None):
        super().__init__(parent)
        self.on_drop_callback = on_drop_callback
        self.source_pixmap = None
        self.image_path = None
        self._fit_mode = True
        self._scale = 1.0
        self._offset = QPointF()
        self._drag_origin = None
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.retranslate_ui()

    def retranslate_ui(self):
        if self.source_pixmap is None:
            self.setText(SettingsLogic.tr("drop_label_text"))

    def set_image_path(self, path: str):
        reader = QImageReader(path)
        reader.setAutoTransform(True)
        pixmap = QPixmap.fromImage(reader.read())
        if pixmap.isNull():
            self.source_pixmap = None
            self.image_path = None
            self.setText(SettingsLogic.tr("msg_error_load").format(filename=path))
            return
        self.source_pixmap = pixmap
        self.image_path = path
        self.fit_to_window()

    def clear_preview(self, text: str | None = None):
        self.source_pixmap = None
        self.image_path = None
        self._fit_mode = True
        self._scale = 1.0
        self._offset = QPointF()
        self.setPixmap(QPixmap())
        self.setText(text or SettingsLogic.tr("drop_label_text"))

    def fit_to_window(self):
        self._fit_mode = True
        self._offset = QPointF()
        self.update()

    def actual_size(self):
        if self.source_pixmap is None:
            return
        self._fit_mode = False
        self._scale = 1.0
        self._offset = QPointF()
        self.update()

    def zoom_by(self, factor: float):
        if self.source_pixmap is None:
            return
        current = self._effective_scale()
        self._fit_mode = False
        self._scale = max(0.05, min(16.0, current * factor))
        self.update()

    def displayed_pixmap(self) -> QPixmap:
        if self.source_pixmap is None:
            return QPixmap()
        return self.source_pixmap.scaled(
            self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

    def _fit_scale(self) -> float:
        if self.source_pixmap is None or self.source_pixmap.isNull():
            return 1.0
        return min(self.width() / self.source_pixmap.width(), self.height() / self.source_pixmap.height())

    def _effective_scale(self) -> float:
        return self._fit_scale() if self._fit_mode else self._scale

    def _update_scaled_pixmap(self):
        self.update()

    @staticmethod
    def _parse_color(value: str | None, fallback: QColor) -> QColor:
        if not value:
            return QColor(fallback)
        color = QColor(value)
        if color.isValid():
            return color
        match = re.fullmatch(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([0-9.]+))?\)", value.strip())
        if not match:
            return QColor(fallback)
        red, green, blue = (int(match.group(i)) for i in range(1, 4))
        alpha_group = match.group(4)
        alpha = 255
        if alpha_group is not None:
            alpha = round(float(alpha_group) * 255) if "." in alpha_group else int(alpha_group)
        return QColor(red, green, blue, max(0, min(255, alpha)))

    @staticmethod
    def _parse_radius(value: str | None, fallback: float = 12.0) -> float:
        if not value:
            return fallback
        match = re.search(r"(\d+(?:\.\d+)?)", value)
        return float(match.group(1)) if match else fallback

    def _paint_drop_background(self):
        theme = ThemeSelectorLogic.get_theme()
        recipe = THEME_DROP_RECIPES.get(theme.get("name", "dark"), THEME_DROP_RECIPES["dark"])
        base_color = self._parse_color(
            theme.get(recipe.get("base_key")) or theme.get("bg_panel_alt") or theme.get("field_bg"),
            self.palette().color(self.backgroundRole()),
        )
        accent_color = self._parse_color(
            theme.get(recipe.get("primary_key")) or theme.get("accent"), self.palette().color(self.foregroundRole())
        )
        secondary_color = self._parse_color(
            theme.get(recipe.get("secondary_key")) or theme.get("button_hover") or theme.get("accent_hover"),
            accent_color,
        )
        border_color = self._parse_color(
            theme.get(recipe.get("border_key")) or theme.get("border"), self.palette().color(self.foregroundRole())
        )
        radius = self._parse_radius(theme.get("drop_radius"), 12.0)

        accent_glow = QColor(accent_color)
        accent_glow.setAlpha(78)
        accent_mid = QColor(accent_color)
        accent_mid.setAlpha(24)
        secondary_glow = QColor(secondary_color)
        secondary_glow.setAlpha(62)
        secondary_mid = QColor(secondary_color)
        secondary_mid.setAlpha(18)
        transparent_base = QColor(base_color)
        transparent_base.setAlpha(0)
        frame_color = QColor(border_color)
        frame_color.setAlpha(115)

        rect = self.rect().adjusted(1, 1, -1, -1)
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.setClipPath(path)
        painter.fillPath(path, base_color)

        glow_radius = max(rect.width(), rect.height()) * 0.95
        top_left = QRadialGradient(rect.topLeft(), glow_radius)
        top_left.setColorAt(0.0, accent_glow)
        top_left.setColorAt(0.38, accent_mid)
        top_left.setColorAt(1.0, transparent_base)
        painter.fillPath(path, top_left)

        bottom_right = QRadialGradient(rect.bottomRight(), glow_radius)
        bottom_right.setColorAt(0.0, secondary_glow)
        bottom_right.setColorAt(0.38, secondary_mid)
        bottom_right.setColorAt(1.0, transparent_base)
        painter.fillPath(path, bottom_right)

        painter.setClipping(False)
        painter.setPen(frame_color)
        painter.drawRoundedRect(rect, radius, radius)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled_pixmap()

    def paintEvent(self, event):
        self._paint_drop_background()
        if self.source_pixmap is None:
            super().paintEvent(event)
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        scale = self._effective_scale()
        width = self.source_pixmap.width() * scale
        height = self.source_pixmap.height() * scale
        origin = QPointF((self.width() - width) / 2, (self.height() - height) / 2) + self._offset
        painter.drawPixmap(
            origin,
            self.source_pixmap.scaled(
                max(1, round(width)),
                max(1, round(height)),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ),
        )

    def wheelEvent(self, event: QWheelEvent):
        if self.source_pixmap is None:
            super().wheelEvent(event)
            return
        self.zoom_by(1.2 if event.angleDelta().y() > 0 else 1 / 1.2)
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.source_pixmap is not None:
            if self._fit_mode:
                self.actual_size()
            else:
                self.fit_to_window()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.source_pixmap is not None:
            self._drag_origin = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.position() - self._drag_origin
            self._drag_origin = event.position()
            self._offset += delta
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self._drag_origin is not None:
            self._drag_origin = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls() and self.on_drop_callback:
            self.on_drop_callback([url.toLocalFile() for url in event.mimeData().urls()])
            event.acceptProposedAction()
