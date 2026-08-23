# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Klucznik MZ
from PySide6.QtWidgets import QHBoxLayout, QWidget

from gui.sort_batch_ui import BatchUI
from gui.sort_file_drop_ui import FileDropUI
from gui.sort_preview_ui import PreviewUI
from gui.sort_settings_ui import SettingsUI


class SortWorkspaceUI(QWidget):
    def __init__(self, version: str, on_drop_callback=None, parent=None):
        super().__init__(parent)
        self.settings_ui = SettingsUI(version, self)
        self.batch_ui = BatchUI(self)
        self.file_drop_ui = FileDropUI(on_drop_callback, self)
        self.preview_ui = PreviewUI(self)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.settings_ui)
        layout.addWidget(self.batch_ui)
        layout.addWidget(self.file_drop_ui)
        layout.addWidget(self.preview_ui)

    def retranslate_ui(self):
        self.settings_ui.retranslate_ui()
        self.batch_ui.retranslate_ui()
        self.file_drop_ui.retranslate_ui()
        self.preview_ui.retranslate_ui()
        self.batch_ui.retranslate_destination()

    def set_destination_info(self, path: str | None, fixed: bool, categories: list[str], available: bool):
        self.batch_ui.set_destination_info(path, fixed, categories, available)
