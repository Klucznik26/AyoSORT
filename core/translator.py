import json
import os
from PySide6.QtCore import QObject, Signal

class Translator(QObject):
    _instance = None
    language_changed = Signal()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        super().__init__()
        self.translations = {}
        self.lang_code = "pl"
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._initialized = True

    def load_language(self, lang_code):
        self.lang_code = lang_code
        path = os.path.join(self.base_path, "i18n", f"{lang_code}.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except Exception as e:
                print(f"Error loading translation {lang_code}: {e}")
        else:
            print(f"Translation file not found: {path}")
            # Fallback to 'pl' if requested language is missing
            if lang_code != "pl":
                self.load_language("pl")
                return

        self.language_changed.emit()

    def get(self, key, default=None):
        return self.translations.get(key, default if default is not None else key)

translator = Translator()