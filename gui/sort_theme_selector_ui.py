from pathlib import Path

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent
from PySide6.QtWidgets import QDialog, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.sort_settings_logic import SettingsLogic
from core.sort_theme_selector_logic import ThemeSelectorLogic
from gui.sort_theme_selector_widgets import ThemeSelectorOptionUI


class ThemeSelectorUI(QDialog):
    theme_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.btn_confirm = None
        self.btn_confirm_shadow = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumSize(510, 486)
        self.current_theme = SettingsLogic.get_theme()
        self.preview_theme = self.current_theme

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        container = QWidget(self)
        layout.addWidget(container)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(5, 5, 5, 5)

        self.glass_panel = QFrame(container)
        container_layout.addWidget(self.glass_panel)
        glass_layout = QVBoxLayout(self.glass_panel)
        glass_layout.setContentsMargins(6, 6, 6, 6)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QWidget())
        self.title_label = QLabel(SettingsLogic.tr('select_theme_title').rstrip(':'))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_close = QPushButton('✕')
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.reject)
        top_bar.addStretch()
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_close)
        glass_layout.addLayout(top_bar)

        self.info_label = QLabel(' ')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setFixedHeight(32)
        glass_layout.addWidget(self.info_label)
        self._build_grid(glass_layout)

        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()
        self.btn_confirm = QPushButton(SettingsLogic.tr('btn_apply', 'Apply'))
        self.btn_confirm.clicked.connect(self.confirm_theme)
        self.btn_confirm_shadow = QGraphicsDropShadowEffect()
        self.btn_confirm.setGraphicsEffect(self.btn_confirm_shadow)
        self.btn_confirm.installEventFilter(self)
        bottom_bar.addWidget(self.btn_confirm)
        bottom_bar.addStretch()
        glass_layout.addLayout(bottom_bar)

        self.apply_preview_theme()
        self._update_selected_button()

    def _build_grid(self, layout):
        names = {code: SettingsLogic.tr(f'theme_{code}', code.title()) for code in ThemeSelectorLogic.get_theme_codes()}
        filenames = {'dark': 't-night.png', 'light': 't_light.png', 'creative': 't_creative.png', 'relax': 't-relaxing.png', 'arctic': 't_arctic.png', 'system': 't_system.png'}
        glows = {'dark': '#04E38A', 'light': '#FBBF24', 'creative': '#F43F5E', 'relax': '#34D399', 'arctic': '#22D3EE', 'system': '#94A3B8'}
        assets_dir = Path(__file__).resolve().parent.parent / 'assets' / 'themes_logo'
        fallback = Path(__file__).resolve().parent.parent / 'assets' / 'AyoSORT.png'
        grid_widget = QWidget()
        grid_layout = QVBoxLayout(grid_widget)
        codes = ThemeSelectorLogic.get_theme_codes()
        index = 0
        for row_index, count in enumerate([1, 2, 3]):
            row = QHBoxLayout()
            row.addStretch()
            for _ in range(count):
                if index >= len(codes):
                    break
                code = codes[index]
                icon_path = assets_dir / filenames[code]
                button = ThemeSelectorOptionUI(str(icon_path if icon_path.exists() else fallback), names[code], code, row_index == 0, glows[code])
                button.clicked.connect(lambda _checked=False, value=code: self.on_theme_clicked(value))
                button.hovered.connect(self.on_hover)
                button.left.connect(self.on_leave)
                row.addWidget(button)
                index += 1
            row.addStretch()
            grid_layout.addLayout(row)
        layout.addWidget(grid_widget)

    def eventFilter(self, obj, event):
        if obj is self.btn_confirm and self.btn_confirm_shadow and event.type() in {QEvent.Type.Enter, QEvent.Type.Leave}:
            alpha = 110 if event.type() == QEvent.Type.Enter else 60
            blur = 20 if event.type() == QEvent.Type.Enter else 15
            self.btn_confirm_shadow.setColor(QColor(4, 227, 138, alpha))
            self.btn_confirm_shadow.setBlurRadius(blur)
        return super().eventFilter(obj, event)

    def on_theme_clicked(self, code):
        self.preview_theme = code
        self.apply_preview_theme()
        self._update_selected_button()

    def _update_selected_button(self):
        for button in self.findChildren(ThemeSelectorOptionUI):
            button.set_selected(button.code == self.preview_theme)

    def confirm_theme(self):
        self.theme_selected.emit(self.preview_theme)
        self.accept()

    def apply_preview_theme(self):
        palette = ThemeSelectorLogic.get_preview_palette(self.preview_theme)
        self.info_label.setText(' ')
        bg_c = QColor(palette['bg'])
        self.glass_panel.setStyleSheet(f"QFrame {{ background: rgba({bg_c.red()}, {bg_c.green()}, {bg_c.blue()}, 210); border-radius: 20px; border: 1px solid rgba(255,255,255,0.08); }}")
        self.title_label.setStyleSheet(f"color: {palette['text']}; background: transparent; border: none;")
        self.btn_close.setStyleSheet(f"QPushButton {{ color: {palette['text']}; }}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 5)
        color = QColor(palette['glow'])
        color.setAlpha(60)
        shadow.setColor(color)
        self.glass_panel.setGraphicsEffect(shadow)
        if self.btn_confirm_shadow:
            self.btn_confirm_shadow.setColor(QColor(4, 227, 138, 60))
            self.btn_confirm_shadow.setBlurRadius(15)
            self.btn_confirm_shadow.setOffset(0, 0)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def on_hover(self, theme_name, _code):
        self.info_label.setText(theme_name)

    def on_leave(self):
        self.info_label.setText(' ')
