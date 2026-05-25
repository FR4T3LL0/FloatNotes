"""Application icon helpers."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon

ICON_FILE_NAME = "floatnotes.ico"


def get_icon_path() -> Path:
    """Return the icon path in source and PyInstaller builds."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "app" / "assets" / ICON_FILE_NAME
    return Path(__file__).resolve().parents[1] / "assets" / ICON_FILE_NAME


def create_app_icon() -> QIcon:
    """Return the FloatNotes app icon."""
    icon_path = get_icon_path()
    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()
