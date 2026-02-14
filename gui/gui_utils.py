from PySide6.QtGui import QPixmap, QPainter, QFont, QIcon
from PySide6.QtCore import Qt, QRect

def create_emoji_icon(emoji):
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    font = QFont()
    font.setPixelSize(24)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, 32, 32), Qt.AlignmentFlag.AlignCenter, emoji)
    painter.end()
    return QIcon(pixmap)