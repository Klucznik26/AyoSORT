# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Klucznik MZ
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPainterPath, QPen, QPolygonF
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

FLAG_SPECS = {
    "pl": ("h", "#FFFFFF", "#DC143C"),
    "en": ("uk",),
    "bg": ("h", "#FFFFFF", "#00966E", "#D62612"),
    "cs": ("cz",),
    "da": ("cross", "#C60C30", "#FFFFFF"),
    "de": ("h", "#000000", "#DD0000", "#FFCE00"),
    "es": ("h", "#AA151B", "#F1BF00", "#F1BF00", "#AA151B"),
    "et": ("h", "#4891D9", "#000000", "#FFFFFF"),
    "fi": ("cross", "#FFFFFF", "#003580"),
    "fr": ("v", "#0055A4", "#FFFFFF", "#EF4135"),
    "hu": ("h", "#CE2939", "#FFFFFF", "#477050"),
    "is": ("cross2", "#02529C", "#FFFFFF", "#DC1E35"),
    "it": ("v", "#009246", "#FFFFFF", "#CE2B37"),
    "lt": ("h", "#FDB913", "#006A44", "#C1272D"),
    "lv": ("h", "#9E3039", "#9E3039", "#FFFFFF", "#9E3039", "#9E3039"),
    "nl": ("h", "#AE1C28", "#FFFFFF", "#21468B"),
    "no": ("cross2", "#BA0C2F", "#FFFFFF", "#00205B"),
    "pt": ("v", "#046A38", "#DA291C", "#DA291C"),
    "ro": ("v", "#002B7F", "#FCD116", "#CE1126"),
    "sk": ("h", "#FFFFFF", "#0B4EA2", "#EE1C25"),
    "sv": ("cross", "#006AA7", "#FECC02"),
    "uk": ("h", "#0057B7", "#FFD700"),
    "el": ("h", "#0D5EAF", "#FFFFFF", "#0D5EAF", "#FFFFFF", "#0D5EAF"),
    "ka": ("cross", "#FFFFFF", "#FF0000"),
    "tr": ("crescent", "#E30A17", "#FFFFFF"),
    "sr": ("h", "#C6363C", "#0C4076", "#FFFFFF"),
    "sl": ("h", "#FFFFFF", "#005DA4", "#ED1C24"),
    "ca": ("h", "#FCDD09", "#DA121A", "#FCDD09", "#DA121A", "#FCDD09", "#DA121A", "#FCDD09"),
    "hr": ("h", "#FF0000", "#FFFFFF", "#171796"),
    "sq": ("label", "#E41E20", "AL"),
    "mt": ("v", "#FFFFFF", "#CF142B"),
    "mk": ("sun", "#D20000", "#F8E92E"),
    "bs": ("diag", "#002395", "#FECB00"),
    "hy": ("h", "#D90012", "#0033A0", "#F2A800"),
    "az": ("h", "#00B5E2", "#EF3340", "#509E2F"),
    "lb": ("h", "#EF3340", "#FFFFFF", "#00A3E0"),
    "ga": ("v", "#169B62", "#FFFFFF", "#FF883E"),
    "gl": ("diag", "#FFFFFF", "#6AA9E9"),
    "eu": ("cross2", "#D52B1E", "#009B48", "#FFFFFF"),
    "co": ("label", "#FFFFFF", "CO"),
    "kk": ("circle", "#00AFCA", "#FEC50C"),
    "sw": ("diag", "#1EB53A", "#00A3DD"),
    "ja": ("circle", "#FFFFFF", "#BC002D"),
    "uz": ("h", "#1EB53A", "#FFFFFF", "#0099B5"),
    "tg": ("h", "#CC0000", "#FFFFFF", "#006600"),
    "mo": ("v", "#003F87", "#FFD200", "#CE1126"),
    "hi": ("h", "#FF9933", "#FFFFFF", "#138808"),
    "cg": ("label", "#C40308", "ME"),
    "isv": ("circle", "#0B5EA8", "#04E38A"),
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
            flag_width = 54 if self._hovered else 46
            flag_height = 36 if self._hovered else 30
            flag_rect = QRectF(
                (self.width() - flag_width) / 2,
                (self.height() - flag_height) / 2,
                flag_width,
                flag_height,
            )
            self._paint_flag(painter, flag_rect)
        finally:
            painter.end()

    def _paint_flag(self, painter: QPainter, rect: QRectF):
        spec = FLAG_SPECS.get(self.code, ("label", "#455A64", self.code.upper()))
        kind, colors = spec[0], spec[1:]
        path = QPainterPath()
        path.addRoundedRect(rect, 3, 3)
        painter.save()
        painter.setClipPath(path)
        if kind in {"h", "v"}:
            count = len(colors)
            for index, color in enumerate(colors):
                if kind == "h":
                    stripe = QRectF(rect.left(), rect.top() + rect.height() * index / count, rect.width(), rect.height() / count + 0.5)
                else:
                    stripe = QRectF(rect.left() + rect.width() * index / count, rect.top(), rect.width() / count + 0.5, rect.height())
                painter.fillRect(stripe, QColor(color))
        elif kind in {"cross", "cross2"}:
            painter.fillRect(rect, QColor(colors[0]))
            outer = QColor(colors[1])
            painter.fillRect(QRectF(rect.left(), rect.center().y() - rect.height() * 0.12, rect.width(), rect.height() * 0.24), outer)
            painter.fillRect(QRectF(rect.left() + rect.width() * 0.31, rect.top(), rect.width() * 0.18, rect.height()), outer)
            if kind == "cross2":
                inner = QColor(colors[2])
                painter.fillRect(QRectF(rect.left(), rect.center().y() - rect.height() * 0.06, rect.width(), rect.height() * 0.12), inner)
                painter.fillRect(QRectF(rect.left() + rect.width() * 0.35, rect.top(), rect.width() * 0.10, rect.height()), inner)
        elif kind == "uk":
            painter.fillRect(rect, QColor("#012169"))
            painter.setPen(QPen(QColor("#FFFFFF"), 7))
            painter.drawLine(rect.topLeft(), rect.bottomRight())
            painter.drawLine(rect.topRight(), rect.bottomLeft())
            painter.setPen(QPen(QColor("#C8102E"), 3))
            painter.drawLine(rect.topLeft(), rect.bottomRight())
            painter.drawLine(rect.topRight(), rect.bottomLeft())
            painter.fillRect(QRectF(rect.left(), rect.center().y() - 4, rect.width(), 8), QColor("#FFFFFF"))
            painter.fillRect(QRectF(rect.center().x() - 4, rect.top(), 8, rect.height()), QColor("#FFFFFF"))
            painter.fillRect(QRectF(rect.left(), rect.center().y() - 2, rect.width(), 4), QColor("#C8102E"))
            painter.fillRect(QRectF(rect.center().x() - 2, rect.top(), 4, rect.height()), QColor("#C8102E"))
        elif kind == "cz":
            painter.fillRect(QRectF(rect.left(), rect.top(), rect.width(), rect.height() / 2), QColor("#FFFFFF"))
            painter.fillRect(QRectF(rect.left(), rect.center().y(), rect.width(), rect.height() / 2), QColor("#D7141A"))
            painter.setBrush(QColor("#11457E"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(QPolygonF([rect.topLeft(), rect.bottomLeft(), QPointF(rect.left() + rect.width() * 0.45, rect.center().y())]))
        elif kind == "circle":
            painter.fillRect(rect, QColor(colors[0]))
            diameter = rect.height() * 0.55
            painter.setBrush(QColor(colors[1]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(rect.center().x() - diameter / 2, rect.center().y() - diameter / 2, diameter, diameter))
        elif kind == "crescent":
            painter.fillRect(rect, QColor(colors[0]))
            diameter = rect.height() * 0.55
            moon = QRectF(rect.center().x() - diameter * 0.55, rect.center().y() - diameter / 2, diameter, diameter)
            painter.setBrush(QColor(colors[1]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(moon)
            moon.translate(diameter * 0.22, 0)
            painter.setBrush(QColor(colors[0]))
            painter.drawEllipse(moon)
        elif kind == "diag":
            painter.fillRect(rect, QColor(colors[0]))
            painter.setPen(QPen(QColor(colors[1]), rect.height() * 0.28))
            painter.drawLine(rect.bottomLeft(), rect.topRight())
        elif kind == "sun":
            painter.fillRect(rect, QColor(colors[0]))
            painter.setPen(QPen(QColor(colors[1]), 2))
            for offset in (-0.4, -0.2, 0, 0.2, 0.4):
                painter.drawLine(QPointF(rect.left(), rect.center().y()), QPointF(rect.right(), rect.center().y() + rect.height() * offset))
            painter.setBrush(QColor(colors[1]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(rect.center().x() - 5, rect.center().y() - 5, 10, 10))
        else:
            painter.fillRect(rect, QColor(colors[0]))
            font = painter.font()
            font.setBold(True)
            font.setPixelSize(12)
            painter.setFont(font)
            foreground = QColor("#111111") if QColor(colors[0]).lightness() > 150 else QColor("#FFFFFF")
            painter.setPen(foreground)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(colors[1]))
        painter.restore()
        painter.setPen(QPen(QColor(255, 255, 255, 170), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, 3, 3)


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
