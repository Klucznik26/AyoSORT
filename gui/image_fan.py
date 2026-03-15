from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget


class ImageFan(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(122, 63)
        self.pixmaps = []
        self.setVisible(False)

    def set_images(self, image_paths):
        self.pixmaps = []
        for path in image_paths:
            pm = QPixmap(path)
            if not pm.isNull():
                self.pixmaps.append(pm.scaledToHeight(35, Qt.TransformationMode.SmoothTransformation))

        self.setVisible(bool(self.pixmaps))
        if self.pixmaps:
            self.update()

    def paintEvent(self, event):
        if not self.pixmaps:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        count = len(self.pixmaps)
        center_x = self.width() / 2
        pivot_y = self.height() * 1.5
        radius = pivot_y - 21

        max_angle = 25
        if count > 1:
            step = (2 * max_angle) / (count - 1)
            angles = [-max_angle + i * step for i in range(count)]
        else:
            angles = [0]

        for i, pixmap in enumerate(self.pixmaps):
            painter.save()
            painter.translate(center_x, pivot_y)
            painter.rotate(angles[i])
            painter.translate(0, -radius)

            w, h = pixmap.width(), pixmap.height()
            x = -w / 2
            y = -h / 2

            painter.setBrush(QColor("white"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRect(int(x) - 3, int(y) - 3, w + 6, h + 6))
            painter.drawPixmap(int(x), int(y), pixmap)
            painter.restore()
