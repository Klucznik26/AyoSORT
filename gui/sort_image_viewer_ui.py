# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Marek Zubrzycki (Klucznik MZ)
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from core.sort_settings_logic import SettingsLogic
from gui.sort_file_drop_widgets import FileDropLabel


def _viewer_toolbar(view: FileDropLabel):
    layout = QHBoxLayout()
    actions = (
        ("viewer_zoom_out_button", "Zoom out", lambda: view.zoom_by(1 / 1.2)),
        ("viewer_zoom_in_button", "Zoom in", lambda: view.zoom_by(1.2)),
        ("viewer_actual_size_button", "Actual size", view.actual_size),
        ("viewer_fit_button", "Fit to window", view.fit_to_window),
    )
    for key, fallback, callback in actions:
        label = "1:1 / 100%" if key == "viewer_actual_size_button" else SettingsLogic.tr(key, fallback)
        button = QPushButton(label)
        button.setToolTip(SettingsLogic.tr(key, fallback))
        button.clicked.connect(callback)
        layout.addWidget(button)
    layout.addStretch()
    return layout


class FullScreenImageDialog(QDialog):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Path(image_path).name)
        self.setWindowFlag(Qt.WindowType.Window, True)
        layout = QVBoxLayout(self)
        self.viewer = FileDropLabel()
        self.viewer.setMinimumSize(320, 240)
        self.viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar = _viewer_toolbar(self.viewer)
        close_button = QPushButton(SettingsLogic.tr("btn_close", "Close"))
        close_button.clicked.connect(self.close)
        toolbar.addWidget(close_button)
        layout.addLayout(toolbar)
        layout.addWidget(self.viewer, 1)
        self.viewer.set_image_path(image_path)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.close)
        QShortcut(QKeySequence(Qt.Key.Key_F11), self).activated.connect(self.close)
        self.showFullScreen()


class CompareImagesDialog(QDialog):
    def __init__(self, image_paths: list[str], left_path: str, right_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(SettingsLogic.tr("viewer_compare_title", "Compare images"))
        if parent is not None:
            self.resize(max(820, round(parent.width() * 0.9)), max(560, round(parent.height() * 0.9)))
        else:
            self.resize(1000, 650)
        root = QVBoxLayout(self)
        columns = QHBoxLayout()
        root.addLayout(columns, 1)
        self.image_paths = list(dict.fromkeys(image_paths))
        self.selectors = []
        self.viewers = []
        initial_paths = (left_path, right_path)
        name_counts = {}
        for path in self.image_paths:
            name_counts[Path(path).name] = name_counts.get(Path(path).name, 0) + 1
        for side, path in enumerate(initial_paths):
            column = QVBoxLayout()
            selector_row = QHBoxLayout()
            number = QLabel(f"{side + 1}.")
            selector = QComboBox()
            selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            accessible_name = f"{SettingsLogic.tr('viewer_compare_button', 'Compare')} {side + 1}"
            selector.setAccessibleName(accessible_name)
            selector.setToolTip(accessible_name)
            for candidate in self.image_paths:
                candidate_path = Path(candidate)
                label = candidate_path.name if name_counts[candidate_path.name] == 1 else str(candidate_path)
                selector.addItem(label, candidate)
            selected_index = selector.findData(path)
            selector.setCurrentIndex(max(0, selected_index))
            selector_row.addWidget(number)
            selector_row.addWidget(selector, 1)
            viewer = FileDropLabel()
            viewer.setMinimumSize(300, 300)
            viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            column.addLayout(selector_row)
            column.addLayout(_viewer_toolbar(viewer))
            column.addWidget(viewer, 1)
            viewer.set_image_path(path)
            columns.addLayout(column, 1)
            self.selectors.append(selector)
            self.viewers.append(viewer)
            selector.currentIndexChanged.connect(lambda index, selected_side=side: self._select_image(selected_side, index))
        close_button = QPushButton(SettingsLogic.tr("btn_close", "Close"))
        close_button.clicked.connect(self.close)
        root.addWidget(close_button, 0, Qt.AlignmentFlag.AlignRight)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.close)

    def _select_image(self, side: int, index: int):
        if index < 0:
            return
        selected_path = self.selectors[side].itemData(index)
        if not selected_path:
            return
        other_side = 1 - side
        other_selector = self.selectors[other_side]
        if selected_path == other_selector.currentData() and len(self.image_paths) > 1:
            replacement = next(path for path in self.image_paths if path != selected_path)
            other_selector.blockSignals(True)
            other_selector.setCurrentIndex(other_selector.findData(replacement))
            other_selector.blockSignals(False)
            self.viewers[other_side].set_image_path(replacement)
        self.viewers[side].set_image_path(selected_path)
