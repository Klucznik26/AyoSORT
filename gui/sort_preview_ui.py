from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QListWidget, QSizePolicy, QVBoxLayout

from core.sort_settings_logic import SettingsLogic
from gui.sort_preview_widgets import PreviewFanWidget


class PreviewUI(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('rightPanel')
        self.setMinimumWidth(260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.top_glass = self._create_glass(layout, 1)
        self.mid_glass = self._create_glass(layout, 2)
        self.bottom_glass = self._create_glass(layout, 1)
        self.image_fan = PreviewFanWidget(); self.image_fan.hide()
        fan_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding); fan_policy.setRetainSizeWhenHidden(True); self.image_fan.setSizePolicy(fan_policy)
        self.file_count_label = QLabel('')
        self.file_count_label.setObjectName('fileCountLabel')
        self.file_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_count_label.hide()
        self.top_glass.layout().addWidget(self.image_fan)
        self.top_glass.layout().addWidget(self.file_count_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.file_list = QListWidget()
        self.file_list.setObjectName('fileList')
        self.mid_glass.layout().addWidget(self.file_list)
        self.mini_logo = QLabel()
        self.mini_logo.setObjectName('cornerLogo')
        self.mini_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bottom_glass.layout().addWidget(self.mini_logo, 0, Qt.AlignmentFlag.AlignCenter)
        self._load_logo()

    def _create_glass(self, parent_layout, stretch):
        frame = QFrame()
        frame.setStyleSheet('QFrame { background-color: rgba(150, 150, 150, 0.1); border-radius: 12px; border: 1px solid rgba(150, 150, 150, 0.15); }')
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        parent_layout.addWidget(frame, stretch)
        return frame

    def _load_logo(self):
        path = Path(__file__).resolve().parent.parent / 'assets' / 'AyoSORT.png'
        if path.exists():
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                self.mini_logo.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                return
        self.mini_logo.setText('AyoSORT')

    def retranslate_ui(self):
        if self.file_list.count() == 0:
            self.file_count_label.hide()

    def update_files(self, file_names: list[str], sample_paths: list[str]):
        self.file_list.clear()
        self.file_list.addItems(file_names)
        self.image_fan.set_images(sample_paths)
        if file_names:
            self.file_count_label.setText(SettingsLogic.tr('label_file_count').format(count=len(file_names)))
            self.file_count_label.setVisible(len(file_names) > 1)
        else:
            self.file_count_label.hide()

    def clear_files(self, completed: bool = False):
        self.file_list.clear()
        self.image_fan.set_images([])
        self.file_count_label.hide()
