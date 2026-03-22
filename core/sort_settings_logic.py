import json
from pathlib import Path


LANGUAGES = [
    ("Polski", "pl", "🇵🇱"), ("English", "en", "🇺🇸"), ("Български", "bg", "🇧🇬"),
    ("Čeština", "cs", "🇨🇿"), ("Dansk", "da", "🇩🇰"), ("Deutsch", "de", "🇩🇪"),
    ("Español", "es", "🇪🇸"), ("Eesti", "et", "🇪🇪"), ("Suomi", "fi", "🇫🇮"),
    ("Français", "fr", "🇫🇷"), ("Magyar", "hu", "🇭🇺"), ("Íslenska", "is", "🇮🇸"),
    ("Italiano", "it", "🇮🇹"), ("Lietuvių", "lt", "🇱🇹"), ("Latviešu", "lv", "🇱🇻"),
    ("Nederlands", "nl", "🇳🇱"), ("Norsk", "no", "🇳🇴"), ("Português", "pt", "🇵🇹"),
    ("Română", "ro", "🇷🇴"), ("Slovenčina", "sk", "🇸🇰"), ("Svenska", "sv", "🇸🇪"),
    ("Українська", "uk", "🇺🇦"), ("Ελληνικά", "el", "🇬🇷"), ("ქართული", "ka", "🇬🇪"),
    ("Türkçe", "tr", "🇹🇷"), ("Српски", "sr", "🇷🇸"), ("Slovenščina", "sl", "🇸🇮"),
    ("Català", "ca", "🇪🇸"), ("Hrvatski", "hr", "🇭🇷"), ("Shqip", "sq", "🇦🇱"),
    ("Malti", "mt", "🇲🇹"), ("Македонски", "mk", "🇲🇰"), ("Bosanski", "bs", "🇧🇦"),
    ("Հայերեն", "hy", "🇦🇲"), ("Azərbaycan dili", "az", "🇦🇿"), ("Lëtzebuergesch", "lb", "🇱🇺"),
    ("Gaeilge", "ga", "🇮🇪"), ("Galego", "gl", "🇪🇸"), ("Euskara", "eu", "🇪🇸"),
    ("Corsu", "co", "🇫🇷"), ("Қазақша", "kk", "🇰🇿"), ("Kiswahili", "sw", "🇰🇪"),
    ("日本語", "ja", "🇯🇵")
]

_THEME_CODES = ['dark', 'light', 'creative', 'relax', 'arctic', 'system']
_CONFIG_DEFAULTS = {'destination_folder': None, 'language': 'pl', 'theme': 'dark'}
_TRANSLATION_CACHE = {}


class SettingsLogic:
    @staticmethod
    def base_dir() -> Path:
        return Path(__file__).resolve().parent.parent

    @staticmethod
    def config_path() -> Path:
        return SettingsLogic.base_dir() / 'config' / 'config.json'

    @staticmethod
    def legacy_config_path() -> Path:
        return SettingsLogic.base_dir() / 'config.json'

    @staticmethod
    def load() -> dict:
        path = SettingsLogic.config_path()
        source = path if path.exists() else SettingsLogic.legacy_config_path()
        data = dict(_CONFIG_DEFAULTS)
        if source.exists():
            try:
                data.update(json.loads(source.read_text(encoding='utf-8')))
            except Exception:
                pass
        SettingsLogic.save(data)
        return data

    @staticmethod
    def save(settings: dict) -> None:
        path = SettingsLogic.config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        data = dict(_CONFIG_DEFAULTS)
        data.update(settings)
        try:
            path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding='utf-8')
        except Exception:
            pass

    @staticmethod
    def get_languages() -> list[tuple[str, str, str]]:
        return LANGUAGES

    @staticmethod
    def get_theme_codes() -> list[str]:
        return list(_THEME_CODES)

    @staticmethod
    def get_language() -> str:
        return SettingsLogic.load().get('language', 'pl')

    @staticmethod
    def set_language(code: str) -> None:
        settings = SettingsLogic.load()
        settings['language'] = code
        SettingsLogic.save(settings)

    @staticmethod
    def get_theme() -> str:
        return SettingsLogic.load().get('theme', 'dark')

    @staticmethod
    def set_theme(code: str) -> None:
        settings = SettingsLogic.load()
        settings['theme'] = code
        SettingsLogic.save(settings)

    @staticmethod
    def get_destination_folder() -> str | None:
        return SettingsLogic.load().get('destination_folder')

    @staticmethod
    def set_destination_folder(path: str | None) -> None:
        settings = SettingsLogic.load()
        settings['destination_folder'] = path
        SettingsLogic.save(settings)

    @staticmethod
    def get_translations(lang_code: str | None = None) -> dict:
        code = lang_code or SettingsLogic.get_language()
        if code in _TRANSLATION_CACHE:
            return _TRANSLATION_CACHE[code]
        json_file = SettingsLogic.base_dir() / 'i18n' / f'{code}.json'
        
        if not json_file.exists() and ('_' in code or '-' in code):
            short_code = code.replace('-', '_').split('_')[0]
            json_file = SettingsLogic.base_dir() / 'i18n' / f'{short_code}.json'
            
        if not json_file.exists():
            json_file = SettingsLogic.base_dir() / 'i18n' / 'pl.json'
        try:
            _TRANSLATION_CACHE[code] = json.loads(json_file.read_text(encoding='utf-8'))
        except Exception:
            _TRANSLATION_CACHE[code] = {}
        return _TRANSLATION_CACHE[code]

    @staticmethod
    def tr(key: str, default: str | None = None, lang_code: str | None = None) -> str:
        return SettingsLogic.get_translations(lang_code).get(key, default if default is not None else key)
