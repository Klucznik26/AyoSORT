# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Klucznik MZ
from PySide6.QtGui import QBitmap, QPixmap, QRegion


def crop_alpha_pixmap(pixmap: QPixmap) -> QPixmap:
    if pixmap.isNull():
        return pixmap
    try:
        mask = QBitmap.fromImage(pixmap.toImage().createAlphaMask())
        rect = QRegion(mask).boundingRect()
        if rect.isValid() and not rect.isEmpty() and rect.width() > 4 and rect.height() > 4:
            return pixmap.copy(rect)
    except RuntimeError:
        pass
    image = pixmap.toImage()
    width = image.width()
    height = image.height()
    min_x, min_y, max_x, max_y = width, height, -1, -1
    for y in range(height):
        for x in range(width):
            if image.pixelColor(x, y).alpha() > 5:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if min_x <= max_x and min_y <= max_y:
        return pixmap.copy(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    return pixmap
