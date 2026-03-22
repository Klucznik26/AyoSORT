import random

from PySide6.QtCore import QEasingCurve, QPoint, QRect, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget


class PreviewFanWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.paths = []
        self.hub_compact = False
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()

    def set_images(self, image_paths):
        self.paths = random.sample(image_paths, 5) if len(image_paths) > 5 else list(image_paths)
        self.setVisible(len(self.paths) > 1)
        self.update()

    def paintEvent(self, event):
        if len(self.paths) <= 1:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        count = min(len(self.paths), 5)
        if self.hub_compact:
            dx, dy, margin = 10, 6, 3
        else:
            dx, dy, margin = 15, 10, 12
        image_width = self.width() - (count - 1) * dx - (margin * 2)
        image_height = self.height() - (count - 1) * dy - (margin * 2)
        if image_width <= 0 or image_height <= 0:
            return
        total_width = image_width + (count - 1) * dx
        total_height = image_height + (count - 1) * dy
        start_x = (self.width() - total_width) / 2
        start_y = (self.height() - total_height) / 2 + (count - 1) * dy
        for index, path in enumerate(self.paths[:count]):
            pixmap = QPixmap(path)
            if pixmap.isNull():
                continue
            scaled = pixmap.scaled(int(image_width), int(image_height), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            slot_x = start_x + index * dx
            slot_y = start_y - index * dy
            img_x = slot_x + (image_width - scaled.width()) / 2
            img_y = slot_y + (image_height - scaled.height()) / 2
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255))
            painter.drawRoundedRect(int(img_x) - 4, int(img_y) - 4, scaled.width() + 8, scaled.height() + 8, 3, 3)
            painter.drawPixmap(int(img_x), int(img_y), scaled)


class PreviewOverlayWidget(QWidget):
    def __init__(self, parent, pixmap, geometry, color, angle_target, offset_target=QPoint(0, 0)):
        super().__init__(parent)
        self.pixmap = pixmap
        self.color = QColor(color)
        self.angle_target = angle_target
        self.offset_target = offset_target
        self.current_angle = 0.0
        self.current_offset = QPoint(0, 0)
        self.current_opacity = 1.0
        self.setGeometry(geometry)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.show()
        self.animation = QVariantAnimation(startValue=0.0, endValue=1.0, duration=400)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.animation.valueChanged.connect(self._update_state)
        self.animation.finished.connect(self.close)
        self.animation.start()

    def _update_state(self, value):
        self.current_angle = value * self.angle_target
        self.current_offset = QPoint(int(self.offset_target.x() * value), int(self.offset_target.y() * value))
        self.current_opacity = 1.0 - value
        self.update()

    def paintEvent(self, event):
        if not self.pixmap:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setOpacity(self.current_opacity)
        cx = self.width() / 2
        cy = self.height() / 2
        painter.translate(self.current_offset)
        painter.translate(cx, cy)
        painter.rotate(self.current_angle)
        painter.translate(-cx, -cy)
        px = (self.width() - self.pixmap.width()) / 2
        py = (self.height() - self.pixmap.height()) / 2
        target_rect = QRect(int(px), int(py), self.pixmap.width(), self.pixmap.height())
        painter.drawPixmap(int(px), int(py), self.pixmap)
        pen = QPen(self.color); pen.setWidth(6); pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.drawRect(target_rect)
