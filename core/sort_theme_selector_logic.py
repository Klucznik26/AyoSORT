from core.sort_settings_logic import SettingsLogic
from core.sort_theme_selector_theme_arctic import THEME as ARCTIC_THEME
from core.sort_theme_selector_theme_creative import THEME as CREATIVE_THEME
from core.sort_theme_selector_theme_dark import THEME as DARK_THEME
from core.sort_theme_selector_theme_light import THEME as LIGHT_THEME
from core.sort_theme_selector_theme_relax import THEME as RELAX_THEME
from core.sort_theme_selector_theme_system import THEME as SYSTEM_THEME

_THEME_MAP = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
    "creative": CREATIVE_THEME,
    "relax": RELAX_THEME,
    "arctic": ARCTIC_THEME,
    "system": SYSTEM_THEME,
}


class ThemeSelectorLogic:
    @staticmethod
    def get_theme_codes() -> list[str]:
        return SettingsLogic.get_theme_codes()

    @staticmethod
    def get_theme(theme_name: str | None = None) -> dict:
        return _THEME_MAP.get(theme_name or SettingsLogic.get_theme(), DARK_THEME)

    @staticmethod
    def get_stylesheet(theme_name: str | None = None) -> str:
        t = ThemeSelectorLogic.get_theme(theme_name)
        panel_bg = t.get("panel_bg", t["bg_panel"])
        narrow_bg = t.get("narrow_bg", t["bg_panel"])
        narrow_border = t.get("narrow_border", t["border"])
        panel_border = t.get("panel_border", t["border"])
        drop_radius = t.get("drop_radius", "8px")
        drop_color = t.get("drop_color", t["text_muted"])
        button_text = t.get("button_text", t["text"])
        btn_hover_border = t.get("button_hover_border", f"1px solid {t['border']}")
        btn_hover_text = t.get("button_hover_text", t["text"])
        btn_pressed_text = t.get("button_pressed_text", t["text"])
        btn_disabled_border = t.get("button_disabled_border", "none")
        icon_color = t.get("icon_color", t["text"])
        list_text = t.get("list_text", t["text"])
        item_hover_bg = t.get("item_hover_bg", t["hover"])
        item_hover_text = t.get("item_hover_text", t["text"])
        run_bg = t.get("run_btn_bg", t["accent"])
        run_color = t.get("run_btn_color", t["selection_text"])
        run_border = t.get("run_btn_border", "none")
        run_hov_bg = t.get("run_btn_hover_bg", t["accent_hover"])
        run_hov_color = t.get("run_btn_hover_color", t["selection_text"])
        run_hov_border = t.get("run_btn_hover_border", "none")
        run_prs_bg = t.get("run_btn_pressed_bg", t["accent_pressed"])
        sb_handle = t.get("scrollbar_handle", t["accent"])
        sb_handle_hover = t.get("scrollbar_handle_hover", t["accent_hover"])
        dialog_bg = t.get("dialog_bg", t["bg_main"])

        return f"""
        QWidget {{ color: {t["text"]}; font-size: 11px; }}
        QWidget#main_widget, QMainWindow {{ background-color: {t["bg_main"]}; }}
        QFrame#leftPanel, QFrame#rightPanel {{ background: {panel_bg}; border: 1px solid {panel_border}; border-radius: 14px; }}
        QFrame#narrowPanel {{ background: {narrow_bg}; border: 1px solid {narrow_border}; border-radius: 14px; }}
        QLabel {{ color: {t["text"]}; }}
        QLabel[secondary='true'] {{ color: {t["text_muted"]}; }}
        QLabel#dropArea {{ background: transparent; color: {drop_color}; font-size: 18px; border: none; border-radius: {drop_radius}; padding: 15px; }}
        QLabel#cornerLogo {{ min-width: 150px; min-height: 150px; padding: 0; background-color: {t["corner_bg"]}; border: 1px solid {t["border"]}; border-radius: 12px; }}
        QLabel#fileCountLabel {{ background-color: {t["corner_bg"]}; color: {t["text"]}; border: 1px solid {t["border"]}; border-radius: 8px; padding: 4px 8px; }}
        QPushButton {{ background-color: {t["button_bg"]}; color: {button_text}; border: 1px solid {t["border"]}; border-radius: 8px; padding: 8px 12px; }}
        QPushButton:hover {{ background-color: {t["button_hover"]}; color: {btn_hover_text}; border: {btn_hover_border}; }}
        QPushButton:pressed {{ background-color: {t["button_pressed"]}; color: {btn_pressed_text}; }}
        QPushButton:disabled {{ background-color: {t["button_disabled_bg"]}; color: {t["button_disabled_text"]}; border: {btn_disabled_border}; }}
        QPushButton#runButton {{ background-color: {run_bg}; border: {run_border}; color: {run_color}; font-weight: bold; }}
        QPushButton#runButton:hover {{ background-color: {run_hov_bg}; border: {run_hov_border}; color: {run_hov_color}; }}
        QPushButton#runButton:pressed {{ background-color: {run_prs_bg}; }}
        QPushButton#iconButton {{ background-color: transparent; border: none; color: {icon_color}; font-size: 24px; border-radius: 10px; }}
        QPushButton#iconButton:hover {{ background-color: {t["hover"]}; color: {t["title"]}; }}
        QPushButton#iconButton[danger='true']:hover {{ background-color: {t["danger_hover"]}; color: {t["danger"]}; }}
        QDialog {{ background-color: {dialog_bg}; color: {t["text"]}; }}
        QComboBox, QLineEdit {{ background-color: {t["field_bg"]}; color: {t["text"]}; border: 1px solid {t["border"]}; border-radius: 4px; padding: 4px 6px; }}
        QComboBox::drop-down {{ border: none; }}
        QComboBox QAbstractItemView, QListWidget, QListView, QTreeView {{ background-color: {t["field_alt_bg"]}; color: {list_text}; border: 1px solid {t["border"]}; outline: none; selection-background-color: {t["selection_bg"]}; selection-color: {t["selection_text"]}; }}
        QListWidget::item:hover, QListView::item:hover, QTreeView::item:hover {{ background-color: {item_hover_bg}; color: {item_hover_text}; }}
        QScrollBar:vertical {{ background: {t["field_alt_bg"]}; width: 12px; margin: 2px; border: 1px solid {t["border"]}; border-radius: 6px; }}
        QScrollBar::handle:vertical {{ background: {sb_handle}; min-height: 24px; border-radius: 6px; }}
        QScrollBar::handle:vertical:hover {{ background: {sb_handle_hover}; }}
        QScrollBar:horizontal {{ background: {t["field_alt_bg"]}; height: 12px; margin: 2px; border: 1px solid {t["border"]}; border-radius: 6px; }}
        QScrollBar::handle:horizontal {{ background: {sb_handle}; min-width: 24px; border-radius: 6px; }}
        QScrollBar::handle:horizontal:hover {{ background: {sb_handle_hover}; }}
        QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; border: none; }}
        """
