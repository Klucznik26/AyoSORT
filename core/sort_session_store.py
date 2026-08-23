# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Marek Zubrzycki (Klucznik MZ)
import json
import os
import tempfile
from pathlib import Path

from core.sort_settings_logic import SettingsLogic


class SortSessionStore:
    VERSION = 1

    @staticmethod
    def load() -> dict | None:
        path = SettingsLogic.session_path()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        except (OSError, json.JSONDecodeError, UnicodeError):
            return None
        if not isinstance(data, dict) or data.get("version") != SortSessionStore.VERSION:
            return None
        return data

    @staticmethod
    def save(session: dict) -> None:
        path = SettingsLogic.session_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": SortSessionStore.VERSION, **session}
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=".session-",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(payload, temporary_file, indent=2, ensure_ascii=False)
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, path)
        except (OSError, TypeError, ValueError):
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def clear() -> None:
        SettingsLogic.session_path().unlink(missing_ok=True)
