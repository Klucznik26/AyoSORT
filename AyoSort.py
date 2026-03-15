import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from ui_main import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AyoSORT")
    app.setApplicationVersion("1.3.1")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
