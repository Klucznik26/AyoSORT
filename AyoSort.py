import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication

from gui.sort_main_ui import MainUI


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AyoSORT")
    app.setApplicationVersion("1.7.0")
    window = MainUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
