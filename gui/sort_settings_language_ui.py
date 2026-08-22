from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QDialog, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.sort_settings_language_preview_logic import DEFAULT_ROOT_STYLE
from core.sort_settings_logic import SettingsLogic

tr = SettingsLogic.tr


ENGLISH_LANGUAGE_NAMES = {
    "pl": "Polish",
    "en": "English",
    "uk": "Ukrainian",
    "tr": "Turkish",
    "sw": "Swahili",
    "sv": "Swedish",
    "sr": "Serbian",
    "sq": "Albanian",
    "sl": "Slovenian",
    "sk": "Slovak",
    "ro": "Romanian",
    "pt": "Portuguese",
    "no": "Norwegian",
    "nl": "Dutch",
    "mt": "Maltese",
    "mk": "Macedonian",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "it": "Italian",
    "lb": "Luxembourgish",
    "kk": "Kazakh",
    "ka": "Georgian",
    "ja": "Japanese",
    "is": "Icelandic",
    "hy": "Armenian",
    "hu": "Hungarian",
    "hr": "Croatian",
    "gl": "Galician",
    "ga": "Irish",
    "fr": "French",
    "fi": "Finnish",
    "eu": "Basque",
    "et": "Estonian",
    "es": "Spanish",
    "el": "Greek",
    "de": "German",
    "da": "Danish",
    "cs": "Czech",
    "co": "Corsican",
    "ca": "Catalan",
    "bs": "Bosnian",
    "bg": "Bulgarian",
    "az": "Azerbaijani",
    "uz": "Uzbek",
    "tg": "Tajik",
    "mo": "Moldovan",
    "hi": "Hindi",
    "cg": "Montenegrin",
    "isv": "Interslavic",
}

POLISH_LANGUAGE_NAMES = {
    "pl": "polski",
    "en": "angielski",
    "uk": "ukraiński",
    "tr": "turecki",
    "sw": "suahili",
    "sv": "szwedzki",
    "sr": "serbski",
    "sq": "albański",
    "sl": "słoweński",
    "sk": "słowacki",
    "ro": "rumuński",
    "pt": "portugalski",
    "no": "norweski",
    "nl": "niderlandzki",
    "mt": "maltański",
    "mk": "macedoński",
    "lv": "łotewski",
    "lt": "litewski",
    "it": "włoski",
    "lb": "luksemburski",
    "kk": "kazachski",
    "ka": "gruziński",
    "ja": "japoński",
    "is": "islandzki",
    "hy": "ormiański",
    "hu": "węgierski",
    "hr": "chorwacki",
    "gl": "galisyjski",
    "ga": "irlandzki",
    "fr": "francuski",
    "fi": "fiński",
    "eu": "baskijski",
    "et": "estoński",
    "es": "hiszpański",
    "el": "grecki",
    "de": "niemiecki",
    "da": "duński",
    "cs": "czeski",
    "co": "korsykański",
    "ca": "kataloński",
    "bs": "bośniacki",
    "bg": "bułgarski",
    "az": "azerski",
    "uz": "uzbecki",
    "tg": "tadżycki",
    "mo": "mołdawski",
    "hi": "hindi",
    "cg": "czarnogórski",
    "isv": "międzysłowiański",
}

SAFE_NATIVE_LABELS = {
    "hi": "Hindi",
}


class SettingsLanguageOptionUI(QPushButton):
    hovered = Signal(str, str, str)
    left = Signal()

    def __init__(self, flag, native_name, code, parent=None):
        super().__init__("", parent)
        self.flag = "🇬🇧" if code == "en" else flag
        self.native_name = native_name
        self.code = code
        self._hovered = False
        self._tile_size = 56
        self._normal_font_px = 46
        self._hover_font_px = 60
        self.setFixedSize(72, 72)
        self.setFlat(True)
        self.setStyleSheet("background: transparent; border: none;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

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
            if self.code == "isv":
                tile_color = QColor(4, 227, 138, 80 if self._hovered else 40)
                border_color = QColor(4, 227, 138, 190 if self._hovered else 148)
            else:
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
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.flag)
        finally:
            painter.end()


class SettingsLanguageUI(QDialog):
    language_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumSize(670, 620)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.main_container = QWidget(self)
        self.main_container.setObjectName("languageSelectorRoot")
        self.main_container.setStyleSheet(DEFAULT_ROOT_STYLE)
        layout.addWidget(self.main_container)
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(20, 20, 20, 20)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.reject)
        self.btn_close.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; border-radius: 10px; font-size: 16px; }"
            "QPushButton:hover { background: rgba(4, 227, 138, 0.14); }"
        )
        top_bar.addWidget(self.btn_close)
        container_layout.addLayout(top_bar)

        self.info_label = QLabel(" ")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(
            "font-size: 18px; font-weight: normal; color: palette(text); "
            "padding: 10px 14px; "
            "background-color: rgba(255, 255, 255, 0.32); "
            "border: 1px solid rgba(255, 255, 255, 0.58); "
            "border-radius: 12px;"
        )
        container_layout.addWidget(self.info_label)

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(8)
        for index, (native_name, code, flag) in enumerate(SettingsLogic.get_languages()):
            button = SettingsLanguageOptionUI(flag, native_name, code)
            button.clicked.connect(
                lambda _checked=False, value=code: (self.language_selected.emit(value), self.accept())
            )
            button.hovered.connect(self.on_hover)
            button.left.connect(self.on_leave)
            grid_layout.addWidget(button, index // 7, index % 7)
        container_layout.addWidget(grid_widget)

    def on_hover(self, _flag, native_name, code):
        key = f"lang_{code}"
        localized_name = tr(key)
        safe_native_name = SAFE_NATIVE_LABELS.get(code, native_name)
        self.main_container.setStyleSheet(DEFAULT_ROOT_STYLE)
        if code in SAFE_NATIVE_LABELS:
            localized_name = safe_native_name
        if localized_name == key:
            current_lang = SettingsLogic.get_language()
            if current_lang == "pl":
                localized_name = POLISH_LANGUAGE_NAMES.get(code, safe_native_name)
            else:
                localized_name = ENGLISH_LANGUAGE_NAMES.get(code, safe_native_name)
        if localized_name == safe_native_name:
            self.info_label.setText(safe_native_name)
        else:
            self.info_label.setText(f"{safe_native_name} — {localized_name}")

    def on_leave(self):
        self.info_label.setText(" ")
        self.main_container.setStyleSheet(DEFAULT_ROOT_STYLE)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
