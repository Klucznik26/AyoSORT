#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Klucznik MZ

import sys

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AyoSORT")
    app.setApplicationVersion("1.8.1")
    font = app.font()
    families = set(QFontDatabase.families())
    preferred = ["DejaVu Sans", "Noto Sans", "Liberation Sans"]
    chosen = next((name for name in preferred if name in families), None)
    if chosen:
        font.setFamily(chosen)
        app.setFont(font)

    from gui.sort_main_ui import MainUI

    window = MainUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
