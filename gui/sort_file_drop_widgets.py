from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

from core.sort_settings_logic import SettingsLogic


class FileDropLabel(QLabel):
    def __init__(self, on_drop_callback=None, parent=None):
        super().__init__(parent)
        self.on_drop_callback = on_drop_callback
        self.source_pixmap = None
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.retranslate_ui()

    def retranslate_ui(self):
        if self.source_pixmap is None:
            self.setText(SettingsLogic.tr('drop_label_text'))

    def set_image_path(self, path: str):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.source_pixmap = None
            self.setText(SettingsLogic.tr('msg_error_load').format(filename=path))
            return
        self.source_pixmap = pixmap
        self._update_scaled_pixmap()

    def clear_preview(self, text: str | None = None):
        self.source_pixmap = None
        self.setPixmap(QPixmap())
        self.setText(text or SettingsLogic.tr('drop_label_text'))

    def _update_scaled_pixmap(self):
        if self.source_pixmap is None:
            return
        scaled = self.source_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled_pixmap()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls() and self.on_drop_callback:
            self.on_drop_callback([url.toLocalFile() for url in event.mimeData().urls()])
            event.acceptProposedAction()
