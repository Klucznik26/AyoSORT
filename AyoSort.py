import sys
import os

# Dodanie katalogu głównego projektu do sys.path, aby Python widział pakiety lokalne
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from gui.app_window import AyoSortApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("AyoSORT")
    app.setApplicationVersion("1.3.0")
    window = AyoSortApp()
    window.show()
    sys.exit(app.exec())