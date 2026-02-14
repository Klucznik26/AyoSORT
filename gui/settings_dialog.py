from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, 
                               QHBoxLayout, QPushButton)
from .gui_utils import create_emoji_icon
from core.translator import translator

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_lang="pl"):
        super().__init__(parent)
        self.setWindowTitle(translator.get("settings_title"))
        self.setFixedSize(260, 220)
        
        layout = QVBoxLayout(self)
        
        # Wybór języka
        layout.addWidget(QLabel(translator.get("label_language")))
        self.lang_combo = QComboBox()
        self.lang_combo.setFixedSize(235, 30)
        
        languages = [
            ("Polski", "🇵🇱", "pl"),
            ("English (angielski)", "🇬🇧", "en"),
            ("Українська (ukraiński)", "🇺🇦", "uk"),
            ("Latviešu (łotewski)", "🇱🇻", "lv"),
            ("Lietuvių (litewski)", "🇱🇹", "lt"),
            ("Eesti (estoński)", "🇪🇪", "et"),
            ("Português (portugalski)", "🇵🇹", "pt"),
            ("Čeština (czeski)", "🇨🇿", "cs"),
            ("Slovenščina (słoweński)", "🇸🇮", "sl"),
            ("ქართული (gruziński)", "🇬🇪", "ka"),
            ("Română (rumuński)", "🇷🇴", "ro"),
            ("Español (hiszpański)", "🇪🇸", "es")
        ]
        
        for lang_name, flag_emoji, lang_code in languages:
            self.lang_combo.addItem(create_emoji_icon(flag_emoji), lang_name, lang_code)
            if lang_code == current_lang:
                self.lang_combo.setCurrentIndex(self.lang_combo.count() - 1)
            
        layout.addWidget(self.lang_combo)
        
        layout.addSpacing(20)
        
        # Wybór motywu
        layout.addWidget(QLabel(translator.get("label_theme")))
        self.theme_combo = QComboBox()
        self.theme_combo.setFixedSize(235, 30)
        
        self.theme_combo.addItem(translator.get("theme_dark"), "dark")
        self.theme_combo.addItem(translator.get("theme_light"), "light")
        self.theme_combo.addItem(translator.get("theme_system"), "system")
        self.theme_combo.addItem(translator.get("theme_relax"), "relax")
        self.theme_combo.addItem(translator.get("theme_creative"), "creative")
        
        layout.addWidget(self.theme_combo)
        
        layout.addStretch()
        
        # Przyciski dolne
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton(translator.get("btn_cancel"))
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        btn_layout.addStretch()
        
        self.btn_ok = QPushButton(translator.get("btn_ok"))
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_ok)
        
        layout.addLayout(btn_layout)

    def apply_theme(self, t):
        if not t: return
        
        if isinstance(t, str):
            self.setStyleSheet(t)
            return
            
        self.setStyleSheet(f"""
            QDialog {{ background-color: {t['bg']}; color: {t['text']}; }}
            QLabel {{ color: {t['text']}; }}
            QComboBox {{
                background-color: {t['widget']};
                color: {t['text']};
                border: 1px solid {t['border']};
                padding: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {t['widget']};
                color: {t['text']};
                selection-background-color: {t['border']};
            }}
            QPushButton {{
                background-color: {t['widget']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {t['border']}; 
            }}
        """)