from PySide6.QtCore import QEasingCurve, QPoint, QRect, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class AnimatedOverlay(QWidget):
    def __init__(self, parent, pixmap, geometry, color, angle_target, offset_target=QPoint(0, 0)):
        super().__init__(parent)
        self.pixmap = pixmap
        self.setGeometry(geometry)
        self.color = QColor(color)
        self.angle_target = angle_target
        self.offset_target = offset_target
        self.current_angle = 0.0
        self.current_offset = QPoint(0, 0)
        self.current_opacity = 1.0

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.show()

        self.anim = QVariantAnimation()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.valueChanged.connect(self.update_state)
        self.anim.finished.connect(self.close)
        self.anim.start()

    def update_state(self, value):
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

        pen = QPen(self.color)
        pen.setWidth(6)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.drawRect(target_rect)
