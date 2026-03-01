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

def apply_dialog_theme(dialog, theme_data):
    """Aplikuje motyw do okna dialogowego (np. QFileDialog)."""
    if not theme_data:
        return

    t = theme_data
    if isinstance(t, str):
        dialog.setStyleSheet(t)
    else:
        dialog.setStyleSheet(f"""
            QFileDialog {{ background-color: {t['bg']}; color: {t['text']}; }}
            QWidget {{ color: {t['text']}; }}
            QTreeView, QListView {{ 
                background-color: {t['widget']}; 
                color: {t['text']}; 
                border: 1px solid {t['border']};
            }}
            QPushButton {{
                background-color: {t['widget']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {t['border']}; 
            }}
            QComboBox {{
                background-color: {t['widget']};
                color: {t['text']};
                border: 1px solid {t['border']};
            }}
            QLineEdit {{
                background-color: {t['widget']};
                color: {t['text']};
                border: 1px solid {t['border']};
            }}
        """)