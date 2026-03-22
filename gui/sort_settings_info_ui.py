from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from core.sort_settings_logic import SettingsLogic


class SettingsInfoUI(QDialog):
    def __init__(self, version: str, base_style: str = '', parent=None):
        super().__init__(parent)
        self.setWindowTitle(SettingsLogic.tr('info_title', 'Info'))
        self.setFixedSize(450, 680)
        self.setStyleSheet(base_style + "QLabel#Section { font-size: 15px; font-weight: bold; margin-top: 15px; } QLabel#Text { font-size: 12px; } QPushButton { padding: 10px; font-weight: bold; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 20)
        banner = QLabel()
        self._load_banner(banner)
        layout.addWidget(banner)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(25, 10, 25, 10)
        title = QLabel('AyoSORT'); title.setObjectName('Section'); title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label = QLabel(f'v {version}'); version_label.setObjectName('Text'); version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description = QLabel(SettingsLogic.tr('info_desc_main', 'AyoSORT is a fast and intuitive tool for sorting image files into quality categories.'))
        description.setObjectName('Text'); description.setWordWrap(True)
        content_layout.addWidget(title); content_layout.addWidget(version_label); content_layout.addWidget(description)
        layout.addWidget(content); layout.addStretch()
        btn_close = QPushButton(SettingsLogic.tr('btn_close', 'Close'))
        btn_close.clicked.connect(self.accept)
        button_layout = QVBoxLayout(); button_layout.setContentsMargins(25, 0, 25, 0); button_layout.addWidget(btn_close)
        layout.addLayout(button_layout)

    def _load_banner(self, label: QLabel):
        path = Path(__file__).resolve().parent.parent / 'assets' / 'Ayo.png'
        if not path.exists():
            return
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            return
        label.setPixmap(pixmap.scaled(450, 250, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
