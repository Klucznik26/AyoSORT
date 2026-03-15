import importlib


class ThemeManager:
    @staticmethod
    def get_theme(theme_name="dark"):
        try:
            module_name = f"{__package__}.{theme_name}" if __package__ else theme_name
            module = importlib.import_module(module_name)
            return module.THEME
        except (ModuleNotFoundError, AttributeError):
            if __package__:
                return importlib.import_module(f"{__package__}.dark").THEME
            from themes.dark import THEME as fallback_theme
            return fallback_theme

    @staticmethod
    def get_stylesheet(theme_name="dark"):
        return ThemeManager._build_css(ThemeManager.get_theme(theme_name))

    @staticmethod
    def _build_css(t):
        narrow_bg = t.get("narrow_bg", t["bg_panel"])
        narrow_border = t.get("narrow_border", t["border"])
        return f"""
            QWidget {{
                color: {t['text']};
                font-size: 11px;
                font-family: 'Segoe UI', 'Noto Sans', 'Ubuntu', 'DejaVu Sans', sans-serif;
            }}
            QWidget#main_widget {{
                background-color: {t['bg_main']};
            }}
            QMainWindow {{
                background-color: {t['bg_main']};
            }}
            QFrame#leftPanel, QFrame#rightPanel {{
                background-color: {t['bg_panel']};
                border: 1px solid {t['border']};
                border-radius: 10px;
            }}
            QFrame#narrowPanel {{
                background: {narrow_bg};
                border: 1px solid {narrow_border};
                border-radius: 10px;
            }}
            QLabel {{
                color: {t['text']};
            }}
            QLabel[secondary="true"] {{
                color: {t['text_muted']};
            }}
            QLabel#cornerLogo {{
                min-width: 150px;
                min-height: 150px;
                padding: 0;
                background-color: {t['corner_bg']};
                border: 1px solid {t['border']};
                border-radius: 10px;
            }}
            QLabel#dropArea {{
                background-color: {t['bg_panel_alt']};
                color: {t['text_muted']};
                font-size: 18px;
                border: 2px dashed {t['border']};
                border-radius: 10px;
            }}
            QLabel#fileCountLabel {{
                background-color: {t['corner_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 8px;
                padding: 4px 8px;
            }}
            QPushButton#iconButton {{
                background-color: transparent;
                border: none;
                color: {t['text']};
                font-size: 20px;
                border-radius: 6px;
            }}
            QPushButton#iconButton:hover {{
                background-color: {t['hover']};
                color: {t['title']};
            }}
            QPushButton#iconButton[danger="true"]:hover {{
                background-color: {t['danger_hover']};
                color: {t['danger']};
            }}
            QDialog {{
                background-color: {t['bg_main']};
                color: {t['text']};
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton {{
                background-color: {t['button_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {t['button_hover']};
                color: {t['text']};
                border: 1px solid {t['border']};
            }}
            QPushButton:pressed {{
                background-color: {t['button_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {t['button_disabled_bg']};
                color: {t['button_disabled_text']};
                border-color: {t['border']};
            }}
            QPushButton#runButton {{
                background-color: {t['accent']};
                border: none;
                color: {t['selection_text']};
                font-weight: bold;
            }}
            QPushButton#runButton:hover {{
                background-color: {t['accent_hover']};
            }}
            QPushButton#runButton:pressed {{
                background-color: {t['accent_pressed']};
            }}
            QComboBox, QLineEdit {{
                background-color: {t['field_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 4px;
                padding: 4px 6px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView, QListView, QTreeView {{
                background-color: {t['field_alt_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                outline: none;
                selection-background-color: {t['selection_bg']};
                selection-color: {t['selection_text']};
            }}
            QScrollBar:vertical {{
                background: {t['field_alt_bg']};
                width: 12px;
                margin: 2px;
                border: 1px solid {t['border']};
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {t['accent']};
                min-height: 24px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['accent_hover']};
            }}
            QScrollBar:horizontal {{
                background: {t['field_alt_bg']};
                height: 12px;
                margin: 2px;
                border: 1px solid {t['border']};
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background: {t['accent']};
                min-width: 24px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {t['accent_hover']};
            }}
            QScrollBar::add-line, QScrollBar::sub-line,
            QScrollBar::add-page, QScrollBar::sub-page {{
                background: transparent;
                border: none;
            }}
        """
