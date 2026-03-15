from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.app_config import LANGUAGES_DATA


class HoverButton(QPushButton):
    hovered = Signal(str, str, str)
    left = Signal()

    def __init__(self, flag, native_name, code, parent=None):
        super().__init__("", parent)
        self.flag = flag
        self.native_name = native_name
        self.code = code
        self._hovered = False
        self._tile_size = 56
        self._normal_font_px = 46
        self._hover_font_px = 60
        self.setFixedSize(72, 72)
        self.setFlat(True)
        self.setStyleSheet("background: transparent; border: none;")
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        self._hovered = True
        self.raise_()
        self.update()
        self.hovered.emit(self.flag, self.native_name, self.code)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        self.left.emit()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing, True)
            tile_color = QColor(255, 255, 255, 80 if self._hovered else 62)
            border_color = QColor(255, 255, 255, 190 if self._hovered else 148)

            x = (self.width() - self._tile_size) // 2
            y = (self.height() - self._tile_size) // 2
            tile_rect = self.rect().adjusted(
                x,
                y,
                -(self.width() - self._tile_size - x),
                -(self.height() - self._tile_size - y),
            )

            painter.setBrush(tile_color)
            painter.setPen(QPen(border_color, 1))
            painter.drawRoundedRect(tile_rect, 12, 12)

            font = self.font()
            font.setPixelSize(self._hover_font_px if self._hovered else self._normal_font_px)
            painter.setFont(font)
            painter.setPen(self.palette().color(self.foregroundRole()))
            painter.drawText(self.rect(), Qt.AlignCenter, self.flag)
        finally:
            painter.end()


class LanguageWindow(QDialog):
    language_selected = Signal(str)

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.tr = translator

        title = self.tr.get("select_language_title", self.tr.get("label_language")).rstrip(":")
        self.setWindowTitle(title)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.info_label = QLabel(" ")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(
            "font-size: 18px; font-weight: normal; color: palette(text); "
            "padding: 10px 14px; "
            "background-color: rgba(255, 255, 255, 0.32); "
            "border: 1px solid rgba(255, 255, 255, 0.58); "
            "border-radius: 12px;"
        )
        layout.addWidget(self.info_label)

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(8)

        columns = 6
        for i, (native_name, code, flag) in enumerate(LANGUAGES_DATA):
            row = i // columns
            col = i % columns
            display_flag = "🇬🇧" if code == "en" else flag
            btn = HoverButton(display_flag, native_name, code)
            btn.clicked.connect(lambda _checked=False, c=code: (self.language_selected.emit(c), self.accept()))
            btn.hovered.connect(self.on_hover)
            btn.left.connect(self.on_leave)
            grid_layout.addWidget(btn, row, col)

        layout.addWidget(grid_widget)

    def on_hover(self, _flag, native_name, code):
        localized_name = self.tr.get(f"lang_{code}", native_name)
        if localized_name == native_name:
            self.info_label.setText(native_name)
        else:
            self.info_label.setText(f"{native_name} — {localized_name}")

    def on_leave(self):
        self.info_label.setText(" ")
