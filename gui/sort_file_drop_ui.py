from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from core.sort_settings_logic import SettingsLogic
from gui.sort_file_drop_widgets import FileDropLabel


class FileDropUI(QFrame):
    def __init__(self, on_drop_callback=None, parent=None):
        super().__init__(parent)
        self.setObjectName('rightPanel')
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        self.drop_label = FileDropLabel(on_drop_callback, self)
        self.drop_label.setObjectName('dropArea')
        layout.addWidget(self.drop_label)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        drop_height = event.size().height() - 30
        if drop_height <= 0:
            return
        drop_width = int(drop_height * (2 / 3))
        panel_width = drop_width + 30
        if self.width() != panel_width:
            self.setFixedWidth(panel_width)
        self.drop_label.setFixedSize(drop_width, drop_height)

    def retranslate_ui(self):
        self.drop_label.retranslate_ui()

    def show_preview(self, path: str):
        self.drop_label.set_image_path(path)

    def show_finished(self):
        self.drop_label.clear_preview(SettingsLogic.tr('label_end_sorting'))

    def reset_preview(self):
        self.drop_label.clear_preview()

    def current_pixmap(self):
        return self.drop_label.pixmap()
