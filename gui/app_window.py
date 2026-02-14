import os
import json
import random
from PySide6.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, 
                               QHBoxLayout, QWidget, QFileDialog, QMessageBox)
from PySide6.QtGui import QPixmap, QKeyEvent
from PySide6.QtCore import Qt, QRect, QPoint

from .settings_dialog import SettingsDialog
from .widgets import ImageDropLabel, ThumbnailFanWidget, AnimatedOverlay
from themes import dark, light, relax, system, creative
from .gui_utils import create_emoji_icon
from core import file_manager
from core.translator import translator

class AyoSortApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(795, 480)

        # Definicje motywów
        self.themes = {
            "dark": dark.theme,
            "light": light.theme,
            "relax": relax.theme,
            "system": system.theme,
            "creative": creative.theme
        }

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
        self.current_pixmap = None
        self.current_language = "pl"
        
        # Ścieżka do pliku konfiguracyjnego
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        self._load_config()
        translator.load_language(self.current_language)
        translator.language_changed.connect(self._update_ui_texts)

        self._setup_ui()
        self.setWindowTitle(translator.get("window_title"))
        self.apply_theme("dark")
        self._check_initial_state()

    def _setup_ui(self):
        # Główny widget i layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QHBoxLayout(central_widget)
        self.layout.setSpacing(10) # Gwarancja odstępu między panelami (brak nakładania)

        # --- LEWY PANEL (Przyciski) ---
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(0)
        left_layout.addSpacing(15)
        
        self.btn_create_catalog = QPushButton(translator.get("btn_create_catalog"))
        self.btn_create_catalog.setFixedSize(190, 50)
        self.btn_create_catalog.clicked.connect(self.create_sorting_catalog)
        left_layout.addWidget(self.btn_create_catalog)
        left_layout.addSpacing(5)
        
        self.btn_select_folder = QPushButton(translator.get("btn_select_folder"))
        self.btn_select_folder.setFixedSize(190, 50)
        self.btn_select_folder.clicked.connect(self.select_folder_to_sort)
        left_layout.addWidget(self.btn_select_folder)
        
        left_layout.addSpacing(5)
        
        sort_btns_layout = QHBoxLayout()
        sort_btns_layout.setSpacing(5)
        sort_btns_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_good = QPushButton()
        self.btn_good.setIcon(create_emoji_icon("👍"))
        self.btn_good.setFixedSize(57, 40)
        self.btn_good.setToolTip(translator.get("tooltip_good"))
        self.btn_good.clicked.connect(lambda: self.sort_current("Dobre"))
        sort_btns_layout.addWidget(self.btn_good)
        
        self.btn_mid = QPushButton()
        self.btn_mid.setIcon(create_emoji_icon("✋"))
        self.btn_mid.setFixedSize(57, 40)
        self.btn_mid.setToolTip(translator.get("tooltip_mid"))
        self.btn_mid.clicked.connect(lambda: self.sort_current("Może być"))
        sort_btns_layout.addWidget(self.btn_mid)
        
        self.btn_bad = QPushButton()
        self.btn_bad.setIcon(create_emoji_icon("👎"))
        self.btn_bad.setFixedSize(57, 40)
        self.btn_bad.setToolTip(translator.get("tooltip_bad"))
        self.btn_bad.clicked.connect(lambda: self.sort_current("Kiepskie"))
        sort_btns_layout.addWidget(self.btn_bad)
        
        left_layout.addLayout(sort_btns_layout)
        
        left_layout.addSpacing(10)
        
        self.label_info_create = QLabel(translator.get("label_info_create"))
        self.label_info_create.setFixedSize(190, 50)
        self.label_info_create.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.label_info_create)
        
        self.label_info_select = QLabel(translator.get("label_info_select"))
        self.label_info_select.setFixedSize(190, 50)
        self.label_info_select.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.label_info_select)
        
        left_layout.addStretch() # Pychamy przyciski na dół
        
        btns_layout = QHBoxLayout()
        btns_layout.setContentsMargins(0, 0, 0, 0)
        btns_layout.setSpacing(5)
        
        self.btn_settings = QPushButton(translator.get("btn_settings"))
        self.btn_settings.setFixedSize(92, 40)
        self.btn_settings.clicked.connect(self.open_settings)
        btns_layout.addWidget(self.btn_settings)
        
        self.btn_close = QPushButton(translator.get("btn_close"))
        self.btn_close.setFixedSize(92, 40)
        self.btn_close.clicked.connect(self.close)
        btns_layout.addWidget(self.btn_close)
        
        left_layout.addLayout(btns_layout)
        self.layout.addLayout(left_layout)

        # --- ŚRODKOWY PANEL (Obraz) ---
        self.image_label = ImageDropLabel(on_drop_callback=self.handle_drop)
        self.layout.addWidget(self.image_label, stretch=1, alignment=Qt.AlignmentFlag.AlignBottom)

        # --- PRAWY PANEL (Logo) ---
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Widget wachlarza (domyślnie ukryty) - teraz na górze
        right_layout.addSpacing(20)
        self.fan_widget = ThumbnailFanWidget()
        right_layout.addWidget(self.fan_widget)
        
        self.file_count_label = QLabel("")
        self.file_count_label.setFixedSize(122, 30)
        self.file_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_count_label.setVisible(False)
        right_layout.addWidget(self.file_count_label)
        
        right_layout.addStretch() # Odstęp wypychający logo na dół
        
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(122, 115)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        logo_path = os.path.join("assets", "AyoSORT.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Skalowanie logo jeśli jest za duże
            if pixmap.height() > 115:
                pixmap = pixmap.scaledToHeight(115, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("AyoSORT")
            self.logo_label.setStyleSheet("color: #666; font-weight: bold;")
        
        right_layout.addWidget(self.logo_label)
        self.layout.addLayout(right_layout)

        # Mapowanie klawiszy (zachowujemy logikę sortowania 1, 2, 3)
        self.key_map = {}
        hotkeys = [Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3]
        for i, (cat_name, folder_name) in enumerate(self.categories.items()):
            if i < len(hotkeys):
                self.key_map[hotkeys[i]] = cat_name

    def handle_drop(self, paths):
        """Obsługa upuszczenia pliku lub folderu"""
        if not paths:
            return

        # Jeśli upuszczono jeden element i jest to folder
        if len(paths) == 1 and os.path.isdir(paths[0]):
            self.source_folder = paths[0]
            self._load_images()
            self._prepare_folders()
            self._show_current_image()
            self.label_info_select.setVisible(False)
            return

        # Jeśli upuszczono pliki (jeden lub więcej)
        first_path = paths[0]
        if os.path.isfile(first_path):
            folder = os.path.dirname(first_path)
            self.source_folder = folder
            
            # Wybieramy tylko te pliki, które są obrazami i są w tym samym folderze
            selected_images = []
            for p in paths:
                if os.path.isfile(p) and os.path.dirname(p) == folder:
                    if os.path.splitext(p)[1].lower() in self.image_extensions:
                        selected_images.append(os.path.basename(p))
            
            if selected_images:
                self._load_images(specific_files=selected_images)
                self._prepare_folders()
                self._show_current_image()
                self.label_info_select.setVisible(False)
            else:
                QMessageBox.information(self, translator.get("info_title"), translator.get("msg_no_images"))

    def create_sorting_catalog(self):
        dialog = QFileDialog(self, translator.get("dialog_create_title"))
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setLabelText(QFileDialog.DialogLabel.Accept, translator.get("dialog_create_accept"))
        dialog.setLabelText(QFileDialog.DialogLabel.Reject, translator.get("btn_cancel"))
        dialog.setLabelText(QFileDialog.DialogLabel.LookIn, translator.get("dialog_look_in"))
        dialog.setLabelText(QFileDialog.DialogLabel.FileName, translator.get("dialog_file_name"))
        dialog.setLabelText(QFileDialog.DialogLabel.FileType, translator.get("dialog_file_type"))
        
        if hasattr(self, 'current_theme_name') and self.current_theme_name in self.themes:
            t = self.themes[self.current_theme_name]
            if isinstance(t, str):
                dialog.setStyleSheet(t)
            else:
                dialog.setStyleSheet(f"""
                    QFileDialog {{ background-color: {t['bg']}; color: {t['text']}; }}
                    QWidget {{ color: {t['text']}; }}
                    QTreeView, QListView {{ 
                        background-color: {t['widget']}; 
                        color: {t['text']}; 
                        border: 1px solid {t['border']};
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
                    QComboBox {{
                        background-color: {t['widget']};
                        color: {t['text']};
                        border: 1px solid {t['border']};
                    }}
                    QLineEdit {{
                        background-color: {t['widget']};
                        color: {t['text']};
                        border: 1px solid {t['border']};
                    }}
                """)
        
        if dialog.exec():
            selected_files = dialog.selectedFiles()
            if selected_files:
                folder = selected_files[0]
                self.destination_folder = folder
                self._save_config()
                
                # Tworzenie struktury katalogów
                sort_path = os.path.join(folder, "SORT")
                subdirs = ["Dobre", "Średnie", "Słabe"]
                
                # Sprawdzenie czy struktura już istnieje
                already_exists = os.path.exists(sort_path) and all(
                    os.path.exists(os.path.join(sort_path, sd)) for sd in subdirs
                )

                try:
                    file_manager.create_directories(sort_path, subdirs)
                    self.label_info_create.setVisible(False)
                except OSError as e:
                    QMessageBox.critical(self, translator.get("error_title"), translator.get("msg_error_create").format(e=e))

    def select_folder_to_sort(self):
        dialog = QFileDialog(self, translator.get("dialog_select_title"))
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setLabelText(QFileDialog.DialogLabel.Accept, translator.get("dialog_select_accept"))
        dialog.setLabelText(QFileDialog.DialogLabel.Reject, translator.get("btn_cancel"))
        dialog.setLabelText(QFileDialog.DialogLabel.LookIn, translator.get("dialog_look_in"))
        dialog.setLabelText(QFileDialog.DialogLabel.FileName, translator.get("dialog_file_name"))
        dialog.setLabelText(QFileDialog.DialogLabel.FileType, translator.get("dialog_file_type"))
        
        if hasattr(self, 'current_theme_name') and self.current_theme_name in self.themes:
            t = self.themes[self.current_theme_name]
            if isinstance(t, str):
                dialog.setStyleSheet(t)
            else:
                dialog.setStyleSheet(f"""
                    QFileDialog {{ background-color: {t['bg']}; color: {t['text']}; }}
                    QWidget {{ color: {t['text']}; }}
                    QTreeView, QListView {{ 
                        background-color: {t['widget']}; 
                        color: {t['text']}; 
                        border: 1px solid {t['border']};
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
                    QComboBox {{
                        background-color: {t['widget']};
                        color: {t['text']};
                        border: 1px solid {t['border']};
                    }}
                    QLineEdit {{
                        background-color: {t['widget']};
                        color: {t['text']};
                        border: 1px solid {t['border']};
                    }}
                """)

        if dialog.exec():
            selected_files = dialog.selectedFiles()
            if selected_files:
                folder = selected_files[0]
                self.source_folder = folder
                self._load_images()
                self._prepare_folders()
                self._show_current_image()
                self.label_info_select.setVisible(False)

    def open_settings(self):
        dialog = SettingsDialog(self, current_lang=self.current_language)
        
        # Ustawienie aktualnego wyboru i wyglądu okna ustawień
        if hasattr(self, 'current_theme_name'):
            index = dialog.theme_combo.findText(self.current_theme_name)
            if index >= 0:
                dialog.theme_combo.setCurrentIndex(index)
            
            dialog.apply_theme(self.themes.get(self.current_theme_name))
            
            # Podgląd motywu w oknie ustawień przy zmianie wyboru
            dialog.theme_combo.currentTextChanged.connect(
                lambda text: dialog.apply_theme(self.themes.get(text)))

        if dialog.exec():
            selected_theme = dialog.theme_combo.currentData()
            self.apply_theme(selected_theme)
            
            # Zapisanie i zastosowanie języka
            selected_lang_data = dialog.lang_combo.currentData()
            if selected_lang_data:
                self.current_language = selected_lang_data
                translator.load_language(self.current_language)
                self._save_config()

    def apply_theme(self, theme_name):
        if theme_name not in self.themes:
            return
        self.current_theme_name = theme_name

        theme_data = self.themes[theme_name]

        if isinstance(theme_data, str):
            # Obsługa motywu jako string (QSS)
            self.setStyleSheet(theme_data)
            self.image_label.setStyleSheet("") # Reset stylu, aby zadziałał ten z QSS
            if self.logo_label.text() == "AyoSORT":
                self.logo_label.setStyleSheet("font-weight: bold;")
            return

        t = theme_data
        
        # Styl dla głównego okna i przycisków
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {t['bg']}; }}
            QWidget {{ color: {t['text']}; }}
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
            QComboBox {{
                background-color: {t['widget']};
                color: {t['text']};
                border: 1px solid {t['border']};
            }}
        """)
        
        # Styl dla pola przeciągania (ImageDropLabel)
        self.image_label.setStyleSheet(f"""
            QLabel {{ 
                background-color: {t['drag']}; 
                color: {t['text']}; 
                font-size: 18px; 
                border: 2px dashed {t['border']}; 
                border-radius: 10px; 
            }}
        """)
        
        # Aktualizacja koloru tekstu logo (jeśli nie jest obrazkiem)
        if self.logo_label.text() == "AyoSORT":
             self.logo_label.setStyleSheet(f"color: {t['text']}; font-weight: bold;")

    def _load_images(self, specific_files=None):
        try:
            if specific_files:
                self.images = specific_files
            else:
                self.images = [f for f in os.listdir(self.source_folder) if os.path.splitext(f)[1].lower() in self.image_extensions]
            
            self.images.sort()
            self.current_index = 0
            if not self.images:
                QMessageBox.information(self, translator.get("info_title"), translator.get("msg_info_no_images_folder"))
                self.file_count_label.setVisible(False)
            else:
                sample_count = min(len(self.images), 5)
                random_files = random.sample(self.images, sample_count)
                random_paths = [os.path.join(self.source_folder, f) for f in random_files]
                self.fan_widget.update_images(random_paths)
                self.file_count_label.setText(translator.get("label_file_count").format(count=len(self.images)))
                self.file_count_label.setVisible(True)
        except OSError as e:
             QMessageBox.critical(self, translator.get("error_title"), translator.get("msg_error_access").format(e=e))

    def _prepare_folders(self):
        for folder_name in self.categories.values():
            path = os.path.join(self.source_folder, folder_name)
            os.makedirs(path, exist_ok=True)

    def _show_current_image(self):
        if self.current_index < len(self.images):
            filename = self.images[self.current_index]
            path = os.path.join(self.source_folder, filename)
            self.current_pixmap = QPixmap(path)
            if not self.current_pixmap.isNull():
                self._update_image_display()
                self.setWindowTitle(f"AyoSORT - {filename} ({self.current_index + 1}/{len(self.images)})")
            else:
                self.image_label.setText(translator.get("msg_error_load").format(filename=filename))
        else:
            self.image_label.setText(translator.get("label_end_sorting"))
            self.setWindowTitle(translator.get("window_title_end"))

    def _update_image_display(self):
        if self.current_pixmap and not self.current_pixmap.isNull():
            scaled_pixmap = self.current_pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

    def sort_current(self, category_key):
        if self.current_index >= len(self.images): return
        dest_folder = self.categories[category_key]
        filename = self.images[self.current_index]
        src_path = os.path.join(self.source_folder, filename)
        
        target_root = self.destination_folder if self.destination_folder else self.source_folder
        dest_path = os.path.join(target_root, dest_folder, filename)
        
        try:
            file_manager.copy_image(src_path, dest_path)
        except Exception as e:
            QMessageBox.critical(self, translator.get("error_title"), translator.get("msg_error_copy").format(e=e))
            return
            
        # Animacje
        current_pixmap = self.image_label.pixmap()
        if current_pixmap and not current_pixmap.isNull():
            pm_copy = current_pixmap.copy()
            pos = self.image_label.mapTo(self, QPoint(0, 0))
            geom = QRect(pos, self.image_label.size())
            
            if category_key == "Dobre":
                AnimatedOverlay(self, pm_copy, geom, "#4CAF50", -15)
            elif category_key == "Może być":
                AnimatedOverlay(self, pm_copy, geom, "#2196F3", 15)
            elif category_key == "Kiepskie":
                AnimatedOverlay(self, pm_copy, geom, "#F44336", 0, QPoint(0, 450))

        self.current_index += 1
        self._show_current_image()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in self.key_map:
            self.sort_current(self.key_map[event.key()])
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        self._update_image_display()
        super().resizeEvent(event)

    def _update_ui_texts(self):
        self.setWindowTitle(translator.get("window_title"))
        self.btn_create_catalog.setText(translator.get("btn_create_catalog"))
        self.btn_select_folder.setText(translator.get("btn_select_folder"))
        self.btn_good.setToolTip(translator.get("tooltip_good"))
        self.btn_mid.setToolTip(translator.get("tooltip_mid"))
        self.btn_bad.setToolTip(translator.get("tooltip_bad"))
        self.label_info_create.setText(translator.get("label_info_create"))
        self.label_info_select.setText(translator.get("label_info_select"))
        self.btn_settings.setText(translator.get("btn_settings"))
        self.btn_close.setText(translator.get("btn_close"))
        
        # Aktualizuj tekst w polu drop tylko jeśli nie ma załadowanego obrazka (czyli wyświetla tekst zachęty)
        if self.current_pixmap is None:
            self.image_label.setText(translator.get("drop_label_text"))

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.destination_folder = config.get("destination_folder")
                    self.current_language = config.get("language", "pl")
            except Exception:
                pass

    def _save_config(self):
        config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                pass
        
        config["destination_folder"] = self.destination_folder
        config["language"] = self.current_language
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception:
            pass

    def _check_initial_state(self):
        if self.destination_folder and os.path.exists(self.destination_folder):
            self.label_info_create.setVisible(False)