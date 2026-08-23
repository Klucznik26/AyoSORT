# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Marek Zubrzycki (Klucznik MZ)
import json
import logging
import os
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

LANGUAGES = [
    ("Polski", "pl", "🇵🇱"),
    ("English", "en", "🇺🇸"),
    ("Български", "bg", "🇧🇬"),
    ("Čeština", "cs", "🇨🇿"),
    ("Dansk", "da", "🇩🇰"),
    ("Deutsch", "de", "🇩🇪"),
    ("Español", "es", "🇪🇸"),
    ("Eesti", "et", "🇪🇪"),
    ("Suomi", "fi", "🇫🇮"),
    ("Français", "fr", "🇫🇷"),
    ("Magyar", "hu", "🇭🇺"),
    ("Íslenska", "is", "🇮🇸"),
    ("Italiano", "it", "🇮🇹"),
    ("Lietuvių", "lt", "🇱🇹"),
    ("Latviešu", "lv", "🇱🇻"),
    ("Nederlands", "nl", "🇳🇱"),
    ("Norsk", "no", "🇳🇴"),
    ("Português", "pt", "🇵🇹"),
    ("Română", "ro", "🇷🇴"),
    ("Slovenčina", "sk", "🇸🇰"),
    ("Svenska", "sv", "🇸🇪"),
    ("Українська", "uk", "🇺🇦"),
    ("Ελληνικά", "el", "🇬🇷"),
    ("ქართული", "ka", "🇬🇪"),
    ("Türkçe", "tr", "🇹🇷"),
    ("Српски", "sr", "🇷🇸"),
    ("Slovenščina", "sl", "🇸🇮"),
    ("Català", "ca", "🇪🇸"),
    ("Hrvatski", "hr", "🇭🇷"),
    ("Shqip", "sq", "🇦🇱"),
    ("Malti", "mt", "🇲🇹"),
    ("Македонски", "mk", "🇲🇰"),
    ("Bosanski", "bs", "🇧🇦"),
    ("Հայերեն", "hy", "🇦🇲"),
    ("Azərbaycan dili", "az", "🇦🇿"),
    ("Lëtzebuergesch", "lb", "🇱🇺"),
    ("Gaeilge", "ga", "🇮🇪"),
    ("Galego", "gl", "🇪🇸"),
    ("Euskara", "eu", "🇪🇸"),
    ("Corsu", "co", "🇫🇷"),
    ("Қазақша", "kk", "🇰🇿"),
    ("Kiswahili", "sw", "🇰🇪"),
    ("日本語", "ja", "🇯🇵"),
    ("Oʻzbekcha", "uz", "🇺🇿"),
    ("Тоҷикӣ", "tg", "🇹🇯"),
    ("Moldovenească", "mo", "🇲🇩"),
    ("Hindi", "hi", "🇮🇳"),
    ("Crnogorski", "cg", "🇲🇪"),
    ("Medžuslovjansky", "isv", "🌍"),
]

_THEME_CODES = ["dark", "light", "creative", "relax", "arctic", "system"]
_CONFIG_DEFAULTS = {
    "destination_folder": None,
    "language": "pl",
    "theme": "dark",
    "category_names": {"good": "", "mid": "", "bad": ""},
}
_TRANSLATION_CACHE = {}
_SETTINGS_CACHE: dict | None = None
_SETTINGS_CACHE_PATH: Path | None = None
LOGGER = logging.getLogger(__name__)


class SettingsLogic:
    @staticmethod
    def base_dir() -> Path:
        bundled_dir = getattr(sys, "_MEIPASS", None)
        if bundled_dir:
            return Path(bundled_dir)
        return Path(__file__).resolve().parent.parent

    @staticmethod
    def config_path() -> Path:
        if sys.platform == "win32":
            root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif sys.platform == "darwin":
            root = Path.home() / "Library" / "Application Support"
        else:
            root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        return root / "AyoSORT" / "config.json"

    @staticmethod
    def session_path() -> Path:
        """Return the per-user path used for the recoverable sorting session."""
        return SettingsLogic.config_path().with_name("session.json")

    @staticmethod
    def legacy_config_path() -> Path:
        return SettingsLogic.base_dir() / "config.json"

    @staticmethod
    def repository_config_path() -> Path:
        return SettingsLogic.base_dir() / "config" / "config.json"

    @staticmethod
    def _validated(settings: dict | None) -> dict:
        source = settings if isinstance(settings, dict) else {}
        data = deepcopy(_CONFIG_DEFAULTS)
        destination = source.get("destination_folder")
        data["destination_folder"] = (
            destination.strip() if isinstance(destination, str) and destination.strip() else None
        )

        language_codes = {code for _name, code, _flag in LANGUAGES}
        language = source.get("language")
        data["language"] = language if language in language_codes else _CONFIG_DEFAULTS["language"]

        theme = source.get("theme")
        data["theme"] = theme if theme in _THEME_CODES else _CONFIG_DEFAULTS["theme"]

        category_names = source.get("category_names")
        if isinstance(category_names, dict):
            for key in data["category_names"]:
                value = category_names.get(key, "")
                data["category_names"][key] = str(value).strip() if value is not None else ""
        return data

    @staticmethod
    def load() -> dict:
        global _SETTINGS_CACHE, _SETTINGS_CACHE_PATH
        path = SettingsLogic.config_path()
        if _SETTINGS_CACHE is not None and _SETTINGS_CACHE_PATH == path:
            return deepcopy(_SETTINGS_CACHE)

        legacy_paths = (SettingsLogic.repository_config_path(), SettingsLogic.legacy_config_path())
        source = path if path.exists() else next((item for item in legacy_paths if item.exists()), None)
        loaded = None
        if source is not None:
            try:
                loaded = json.loads(source.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, UnicodeError) as exc:
                LOGGER.warning("Cannot read AyoSORT settings from %s: %s", source, exc)
        data = SettingsLogic._validated(loaded)
        _SETTINGS_CACHE = deepcopy(data)
        _SETTINGS_CACHE_PATH = path
        if source is not None and source != path:
            SettingsLogic.save(data)
        return deepcopy(data)

    @staticmethod
    def save(settings: dict) -> None:
        global _SETTINGS_CACHE, _SETTINGS_CACHE_PATH
        path = SettingsLogic.config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        data = SettingsLogic._validated(settings)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent, prefix=".config-", suffix=".tmp", delete=False
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(data, temporary_file, indent=4, ensure_ascii=False)
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, path)
        except (OSError, TypeError, ValueError):
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise
        _SETTINGS_CACHE = deepcopy(data)
        _SETTINGS_CACHE_PATH = path

    @staticmethod
    def get_languages() -> list[tuple[str, str, str]]:
        return LANGUAGES

    @staticmethod
    def get_theme_codes() -> list[str]:
        return list(_THEME_CODES)

    @staticmethod
    def get_language() -> str:
        return SettingsLogic.load().get("language", "pl")

    @staticmethod
    def set_language(code: str) -> None:
        if code not in {language_code for _name, language_code, _flag in LANGUAGES}:
            raise ValueError(f"Unsupported language code: {code}")
        settings = SettingsLogic.load()
        settings["language"] = code
        SettingsLogic.save(settings)

    @staticmethod
    def get_theme() -> str:
        return SettingsLogic.load().get("theme", "dark")

    @staticmethod
    def set_theme(code: str) -> None:
        if code not in _THEME_CODES:
            raise ValueError(f"Unsupported theme code: {code}")
        settings = SettingsLogic.load()
        settings["theme"] = code
        SettingsLogic.save(settings)

    @staticmethod
    def get_destination_folder() -> str | None:
        return SettingsLogic.load().get("destination_folder")

    @staticmethod
    def set_destination_folder(path: str | None) -> None:
        settings = SettingsLogic.load()
        settings["destination_folder"] = path
        SettingsLogic.save(settings)

    @staticmethod
    def get_category_names() -> dict[str, str]:
        stored = SettingsLogic.load().get("category_names", {})
        result = {"good": "", "mid": "", "bad": ""}
        if isinstance(stored, dict):
            for key in result:
                value = stored.get(key, "")
                result[key] = str(value).strip() if value is not None else ""
        return result

    @staticmethod
    def set_category_names(category_names: dict[str, str]) -> None:
        settings = SettingsLogic.load()
        sanitized = {"good": "", "mid": "", "bad": ""}
        for key in sanitized:
            value = category_names.get(key, "")
            sanitized[key] = str(value).strip() if value is not None else ""
        non_empty = [name.casefold() for name in sanitized.values() if name]
        if len(non_empty) != len(set(non_empty)):
            raise ValueError("Category names must be unique")
        if any(name in {".", ".."} for name in sanitized.values()):
            raise ValueError("Category names cannot be . or ..")
        settings["category_names"] = sanitized
        SettingsLogic.save(settings)

    @staticmethod
    def get_category_display_names() -> dict[str, str]:
        custom_names = SettingsLogic.get_category_names()
        defaults = {"good": "A", "mid": "B", "bad": "C"}
        result = {}
        for key, default in defaults.items():
            result[key] = custom_names.get(key) or default
        return result

    @staticmethod
    def get_translations(lang_code: str | None = None) -> dict:
        code = lang_code or SettingsLogic.get_language()
        if code in _TRANSLATION_CACHE:
            return _TRANSLATION_CACHE[code]
        json_file = SettingsLogic.base_dir() / "i18n" / f"sort_{code}.json"

        if not json_file.exists() and ("_" in code or "-" in code):
            short_code = code.replace("-", "_").split("_")[0]
            json_file = SettingsLogic.base_dir() / "i18n" / f"sort_{short_code}.json"

        if not json_file.exists():
            json_file = SettingsLogic.base_dir() / "i18n" / "sort_pl.json"
        try:
            translations = json.loads(json_file.read_text(encoding="utf-8"))
            _TRANSLATION_CACHE[code] = translations if isinstance(translations, dict) else {}
        except (OSError, json.JSONDecodeError, UnicodeError) as exc:
            LOGGER.warning("Cannot read AyoSORT translations from %s: %s", json_file, exc)
            _TRANSLATION_CACHE[code] = {}
        return _TRANSLATION_CACHE[code]

    @staticmethod
    def tr(key: str, default: str | None = None, lang_code: str | None = None) -> str:
        return SettingsLogic.get_translations(lang_code).get(key, default if default is not None else key)
