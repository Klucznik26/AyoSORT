from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QLabel, QSizePolicy

from core.translator import translator


class DropArea(QLabel):
    def __init__(self, parent=None, on_drop_callback=None):
        super().__init__(parent)
        self.on_drop_callback = on_drop_callback
        self.setFixedWidth(480)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(translator.get("drop_label_text"))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls() and self.on_drop_callback:
            paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self.on_drop_callback(paths)
            event.acceptProposedAction()
