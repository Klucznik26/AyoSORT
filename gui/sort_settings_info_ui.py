# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Marek Zubrzycki (Klucznik MZ)
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.sort_settings_logic import SettingsLogic


class SettingsInfoUI(QDialog):
    def __init__(self, version: str, base_style: str = "", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(450, 680)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_container = QWidget(self)
        self.main_container.setObjectName("sortInfoRoot")
        layout.addWidget(self.main_container)

        outer = QVBoxLayout(self.main_container)
        outer.setContentsMargins(16, 16, 16, 16)

        self.panel = QFrame(self.main_container)
        self.panel.setObjectName("sortInfoPanel")
        outer.addWidget(self.panel)

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(0, 0, 0, 20)
        panel_layout.setSpacing(0)

        top = QHBoxLayout()
        top.setContentsMargins(16, 16, 16, 0)
        top.addStretch()
        self.title_label = QLabel(SettingsLogic.tr("info_title", "Info"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = self.title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.accept)
        top.addStretch()
        top.addWidget(self.title_label)
        top.addStretch()
        top.addWidget(self.btn_close)
        panel_layout.addLayout(top)

        banner = QLabel()
        self._load_banner(banner)
        panel_layout.addWidget(banner)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(25, 10, 25, 10)
        title = QLabel("AyoSORT")
        title.setObjectName("Section")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label = QLabel(f"v {version}")
        version_label.setObjectName("Text")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description = QLabel(
            SettingsLogic.tr(
                "info_desc_main",
                "AyoSORT is a fast and intuitive tool for sorting image files into quality categories.",
            )
        )
        description.setObjectName("Text")
        description.setWordWrap(True)
        content_layout.addWidget(title)
        content_layout.addWidget(version_label)
        content_layout.addWidget(description)
        panel_layout.addWidget(content)
        panel_layout.addStretch()
        btn_close = QPushButton(SettingsLogic.tr("btn_close", "Close"))
        btn_close.setObjectName("runButton")
        btn_close.clicked.connect(self.accept)
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(25, 0, 25, 0)
        button_layout.addWidget(btn_close)
        panel_layout.addLayout(button_layout)
        self.setStyleSheet(
            base_style
            + "#sortInfoRoot { background-color: rgba(10, 25, 20, 0.30); border-radius: 26px; }"
            + "#sortInfoPanel { background-color: rgba(19, 29, 37, 0.94); border-radius: 18px; border: 1px solid rgba(4, 227, 138, 0.20); }"
            + "QLabel#Section { font-size: 15px; font-weight: bold; margin-top: 15px; }"
            + "QLabel#Text { font-size: 12px; }"
            + "QPushButton#runButton { padding: 10px; font-weight: bold; }"
        )
        self.title_label.setStyleSheet(
            "color: #CFE8DC; background: transparent; border: none; font-size: 14px; font-weight: 700;"
        )
        self.btn_close.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; border-radius: 10px; font-size: 16px; }"
            "QPushButton:hover { background: rgba(4, 227, 138, 0.14); }"
        )

    def _load_banner(self, label: QLabel):
        path = Path(__file__).resolve().parent.parent / "assets" / "Ayo2.png"
        if not path.exists():
            return
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            return
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setPixmap(
            pixmap.scaled(390, 390, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
