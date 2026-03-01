import os
import json
import random
from core import file_manager

class AyoSortEngine:
    def __init__(self):
        # Konfiguracja kategorii i folderów
        self.categories = {
            "Dobre": os.path.join("SORT", "Dobre"),
            "Może być": os.path.join("SORT", "Średnie"),
            "Kiepskie": os.path.join("SORT", "Słabe")
        }
        
        # Obsługiwane rozszerzenia
        self.image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".wep", ".tif", ".tiff", ".ico"}
        
        self.images = []
        self.current_index = 0
        self.source_folder = ""
        self.destination_folder = None
        self.current_language = "pl"
        self.current_theme = "dark"
        
        # Ścieżka do pliku konfiguracyjnego
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.destination_folder = config.get("destination_folder")
                    self.current_language = config.get("language", "pl")
                    self.current_theme = config.get("theme", "dark")
            except Exception:
                pass

    def save_config(self):
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
        subdirs = ["Dobre", "Średnie", "Słabe"]
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