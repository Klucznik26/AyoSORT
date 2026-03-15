import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from core.translator import translator


class InfoWindow(QDialog):
    def __init__(self, version: str, base_style="", parent=None):
        super().__init__(parent)
        self.version = version
        self.setWindowTitle(translator.get("info_title", "Info"))
        self.setFixedSize(450, 680)
        self.setStyleSheet(
            base_style
            + """
            QLabel#Section { font-size: 15px; font-weight: bold; margin-top: 15px; }
            QLabel#Text { font-size: 12px; }
            QPushButton {
                padding: 10px;
                font-weight: bold;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(10)

        self.banner = QLabel()
        self._load_banner()
        layout.addWidget(self.banner)

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(25, 10, 25, 10)

        title = QLabel("AyoSORT")
        title.setObjectName("Section")
        title.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(title)

        version_label = QLabel(f"v {self.version}")
        version_label.setObjectName("Text")
        version_label.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(version_label)

        description = QLabel(
            translator.get(
                "info_desc_main",
                "AyoSORT is a fast and intuitive tool for sorting image files into quality categories.",
            )
        )
        description.setObjectName("Text")
        description.setWordWrap(True)
        c_layout.addWidget(description)

        layout.addWidget(content)
        layout.addStretch()

        btn_close = QPushButton(translator.get("btn_close", "Close"))
        btn_close.clicked.connect(self.accept)
        btn_container = QVBoxLayout()
        btn_container.setContentsMargins(25, 0, 25, 0)
        btn_container.addWidget(btn_close)
        layout.addLayout(btn_container)

    def _load_banner(self):
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        banner_path = os.path.join(root_path, "assets", "Ayo.png")
        if not os.path.exists(banner_path):
            return

        pix = QPixmap(banner_path)
        if pix.isNull():
            return

        self.banner.setPixmap(
            pix.scaled(
                450,
                250,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
