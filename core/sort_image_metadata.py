# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Klucznik MZ
from datetime import datetime
from pathlib import Path

from PySide6.QtGui import QImageReader


def _format_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def read_image_metadata(path: str | Path) -> dict[str, str]:
    image_path = Path(path)
    result = {
        "name": image_path.name,
        "dimensions": "—",
        "size": "—",
        "camera": "—",
        "captured": "—",
        "exposure": "—",
    }
    try:
        result["size"] = _format_size(image_path.stat().st_size)
    except OSError:
        return result

    reader = QImageReader(str(image_path))
    dimensions = reader.size()
    if dimensions.isValid():
        result["dimensions"] = f"{dimensions.width()} × {dimensions.height()} px"

    try:
        from PIL import ExifTags, Image

        with Image.open(image_path) as image:
            if result["dimensions"] == "—":
                result["dimensions"] = f"{image.width} × {image.height} px"
            exif = image.getexif()
            tags = {ExifTags.TAGS.get(key, key): value for key, value in exif.items()}
            make = str(tags.get("Make", "")).strip()
            model = str(tags.get("Model", "")).strip()
            result["camera"] = " ".join(part for part in (make, model) if part) or "—"
            captured = tags.get("DateTimeOriginal") or tags.get("DateTime")
            if captured:
                try:
                    result["captured"] = datetime.strptime(str(captured), "%Y:%m:%d %H:%M:%S").strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError:
                    result["captured"] = str(captured)
            exposure = tags.get("ExposureTime")
            aperture = tags.get("FNumber")
            iso = tags.get("ISOSpeedRatings") or tags.get("PhotographicSensitivity")
            focal = tags.get("FocalLength")
            parts = []
            if exposure:
                parts.append(f"{exposure} s")
            if aperture:
                parts.append(f"f/{float(aperture):g}")
            if iso:
                parts.append(f"ISO {iso}")
            if focal:
                parts.append(f"{float(focal):g} mm")
            result["exposure"] = " · ".join(parts) or "—"
    except (ImportError, OSError, ValueError, TypeError):
        pass
    return result
