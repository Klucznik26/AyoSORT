from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.sort_settings_logic import SettingsLogic


class SettingsLanguageOptionUI(QPushButton):
    hovered = Signal(str, str, str)
    left = Signal()

    def __init__(self, flag, native_name, code, parent=None):
        super().__init__('', parent)
        self.flag = '🇬🇧' if code == 'en' else flag
        self.native_name = native_name
        self.code = code
        self._hovered = False
        self.setFixedSize(72, 72)
        self.setFlat(True)
        self.setStyleSheet('background: transparent; border: none;')
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event):
        self._hovered = True; self.update(); self.hovered.emit(self.flag, self.native_name, self.code); super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False; self.update(); self.left.emit(); super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        tile_color = QColor(255, 255, 255, 80 if self._hovered else 62)
        border_color = QColor(255, 255, 255, 190 if self._hovered else 148)
        tile_rect = self.rect().adjusted(8, 8, -8, -8)
        painter.setBrush(tile_color); painter.setPen(QPen(border_color, 1)); painter.drawRoundedRect(tile_rect, 12, 12)
        font = self.font(); font.setPixelSize(60 if self._hovered else 46); painter.setFont(font)
        painter.setPen(self.palette().color(self.foregroundRole())); painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.flag)


class SettingsLanguageUI(QDialog):
    language_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(SettingsLogic.tr('select_language_title').rstrip(':'))
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        self.info_label = QLabel(' ')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet('font-size: 18px; padding: 10px 14px; background-color: rgba(255, 255, 255, 0.32); border: 1px solid rgba(255, 255, 255, 0.58); border-radius: 12px;')
        layout.addWidget(self.info_label)
        grid_widget = QWidget(); grid_layout = QGridLayout(grid_widget); grid_layout.setSpacing(8)
        for index, (native_name, code, flag) in enumerate(SettingsLogic.get_languages()):
            button = SettingsLanguageOptionUI(flag, native_name, code)
            button.clicked.connect(lambda _checked=False, value=code: (self.language_selected.emit(value), self.accept()))
            button.hovered.connect(self.on_hover); button.left.connect(self.on_leave)
            grid_layout.addWidget(button, index // 7, index % 7)
        layout.addWidget(grid_widget)

    def on_hover(self, _flag, native_name, code):
        localized_name = SettingsLogic.tr(f'lang_{code}', native_name)
        self.info_label.setText(native_name if localized_name == native_name else f'{native_name} - {localized_name}')

    def on_leave(self):
        self.info_label.setText(' ')
