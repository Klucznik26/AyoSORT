from PySide6.QtWidgets import QLabel, QWidget, QSizePolicy
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPainter, QColor, QPixmap, QPen
from PySide6.QtCore import Qt, QRect, QPoint, QVariantAnimation, QEasingCurve
from core.translator import translator

class ImageDropLabel(QLabel):
    def __init__(self, parent=None, on_drop_callback=None):
        super().__init__(parent)
        self.on_drop_callback = on_drop_callback
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setFixedSize(435, 450)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(translator.get("drop_label_text"))
        self.setStyleSheet("QLabel { background-color: #2b2b2b; color: #aaaaaa; font-size: 18px; border: 2px dashed #444; border-radius: 10px; }")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls() and self.on_drop_callback:
            urls = event.mimeData().urls()
            paths = [url.toLocalFile() for url in urls]
            self.on_drop_callback(paths)
            event.acceptProposedAction()

class ThumbnailFanWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(122, 63)
        self.pixmaps = []
        self.setVisible(False)

    def update_images(self, image_paths):
        self.pixmaps = []
        for path in image_paths:
            pm = QPixmap(path)
            if not pm.isNull():
                # Skalowanie do miniatury (np. 100px wysokości)
                pm = pm.scaledToHeight(35, Qt.TransformationMode.SmoothTransformation)
                self.pixmaps.append(pm)
        
        if self.pixmaps:
            self.setVisible(True)
            self.update()
        else:
            self.setVisible(False)

    def paintEvent(self, event):
        if not self.pixmaps:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        count = len(self.pixmaps)
        center_x = self.width() / 2
        # Punkt obrotu poniżej widgetu, aby uzyskać efekt łuku
        pivot_y = self.height() * 1.5 
        radius = pivot_y - 21 # Promień łuku
        
        # Kąty rozłożenia kart
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
            
            # Rysowanie karty wycentrowanej względem punktu na łuku
            w, h = pixmap.width(), pixmap.height()
            x = -w / 2
            y = -h / 2
            
            # Biała ramka (tło karty)
            painter.setBrush(QColor("white"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRect(int(x)-3, int(y)-3, w+6, h+6))
            
            painter.drawPixmap(int(x), int(y), pixmap)
            
            painter.restore()

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
        if not self.pixmap: return
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