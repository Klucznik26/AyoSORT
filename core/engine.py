import os
import json
import random
import re
from core import file_manager

class AyoSortEngine:
    def __init__(self):
        self.category_order = ["good", "mid", "bad"]
        
        # Obsługiwane rozszerzenia
        self.image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".wep", ".tif", ".tiff", ".ico"}
        
        self.images = []
        self.current_index = 0
        self.source_folder = ""
        self.destination_folder = None
        self.current_language = "pl"
        self.current_theme = "dark"
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = os.path.join(self.base_dir, "config")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.legacy_config_file = os.path.join(self.base_dir, "config.json")
        self.load_config()
        self.categories = self._build_categories()

    def load_config(self):
        source = self.config_file if os.path.exists(self.config_file) else self.legacy_config_file
        if os.path.exists(source):
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.destination_folder = config.get("destination_folder")
                    self.current_language = config.get("language", "pl")
                    self.current_theme = config.get("theme", "dark")
            except Exception:
                pass
        self.save_config()

    def save_config(self):
        os.makedirs(self.config_dir, exist_ok=True)
        config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                pass
        
        config["destination_folder"] = self.destination_folder
        config["language"] = self.current_language
        config["theme"] = self.current_theme
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception:
            pass

    def set_language(self, lang_code):
        self.current_language = lang_code
        self.categories = self._build_categories()
        self.save_config()

    def set_theme(self, theme_name):
        self.current_theme = theme_name
        self.save_config()

    def set_destination_folder(self, folder):
        self.destination_folder = folder
        self.save_config()
        
    def initialize_sorting_structure(self):
        """Tworzy strukturę katalogów w folderze docelowym."""
        if not self.destination_folder:
            raise ValueError("Destination folder not set")
            
        sort_path = os.path.join(self.destination_folder, "SORT")
        subdirs = [self._category_names_for_lang(self.current_language)[k] for k in self.category_order]
        file_manager.create_directories(sort_path, subdirs)

    def load_images_from_folder(self, folder):
        """Skanuje folder w poszukiwaniu obrazów."""
        self.source_folder = folder
        try:
            self.images = [f for f in os.listdir(self.source_folder) 
                           if os.path.splitext(f)[1].lower() in self.image_extensions]
            self.images.sort()
            self.current_index = 0
            return True
        except OSError:
            self.images = []
            return False

    def set_specific_images(self, folder, file_list):
        """Ustawia konkretną listę plików (np. z drag&drop)."""
        self.source_folder = folder
        self.images = sorted(file_list)
        self.current_index = 0

    def get_current_image_path(self):
        if 0 <= self.current_index < len(self.images):
            return os.path.join(self.source_folder, self.images[self.current_index])
        return None

    def get_current_filename(self):
        if 0 <= self.current_index < len(self.images):
            return self.images[self.current_index]
        return None

    def get_progress_string(self):
        return f"{self.current_index + 1}/{len(self.images)}"

    def is_finished(self):
        return self.current_index >= len(self.images)

    def has_images(self):
        return len(self.images) > 0

    def get_random_samples(self, count=5):
        if not self.images:
            return []
        sample_count = min(len(self.images), count)
        random_files = random.sample(self.images, sample_count)
        return [os.path.join(self.source_folder, f) for f in random_files]

    def sort_current_image(self, category_key):
        """Przenosi/kopiuje aktualny obraz do wybranej kategorii."""
        if self.is_finished():
            return False

        dest_subdir = self.categories.get(category_key)
        if not dest_subdir:
            return False

        filename = self.images[self.current_index]
        src_path = os.path.join(self.source_folder, filename)
        
        target_root = self.destination_folder if self.destination_folder else self.source_folder
        dest_path = os.path.join(target_root, dest_subdir, filename)
        
        # Wykonanie operacji na pliku
        file_manager.copy_image(src_path, dest_path)
        
        # Przejście do następnego
        self.current_index += 1
        return True

    def _build_categories(self):
        names = self._category_names_for_lang(self.current_language)
        return {key: os.path.join("SORT", names[key]) for key in self.category_order}

    def _category_names_for_lang(self, lang_code):
        # Stabilne domyślne nazwy (PL historyczne + EN fallback)
        names = {
            "good": "Dobre" if lang_code == "pl" else "Good",
            "mid": "Średnie" if lang_code == "pl" else "Average",
            "bad": "Słabe" if lang_code == "pl" else "Bad",
        }

        i18n_path = os.path.join(self.base_dir, "i18n", f"{lang_code}.json")
        try:
            with open(i18n_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return names

        # Jeśli są jawne klucze folderów, użyj ich.
        # Dla PL zachowujemy historyczne nazwy katalogów.
        # Dla pozostałych języków fallback to pierwszy wyraz z tooltipów.
        names["good"] = self._normalize_folder_name(
            data.get("folder_good")
            or (None if lang_code == "pl" else self._first_word(data.get("tooltip_good")))
            or names["good"]
        )
        names["mid"] = self._normalize_folder_name(
            data.get("folder_mid")
            or (None if lang_code == "pl" else self._first_word(data.get("tooltip_mid")))
            or names["mid"]
        )
        names["bad"] = self._normalize_folder_name(
            data.get("folder_bad")
            or (None if lang_code == "pl" else self._first_word(data.get("tooltip_bad")))
            or names["bad"]
        )
        return names

    @staticmethod
    def _first_word(text):
        if not text:
            return ""
        text = text.strip()
        if not text:
            return ""
        token = text.split()[0]
        token = re.sub(r"[^\w\-ąćęłńóśźżА-Яа-яЄєІіЇїҐґ]+$", "", token)
        return token

    @staticmethod
    def _normalize_folder_name(name):
        # Unikamy separatorów ścieżek i pustych nazw.
        clean = str(name).replace("/", "_").replace("\\", "_").strip()
        return clean or "Category"
