from themes.manager import ThemeManager


def get_style(theme_name: str) -> str:
    return ThemeManager.get_stylesheet(theme_name)


def get_drop_zone_style(theme_name: str) -> str:
    return ""
