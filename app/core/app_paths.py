"""Path helpers for local FloatNotes data."""

from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "FloatNotes"
DATA_FILE_NAME = "notes.json"
SETTINGS_FILE_NAME = "settings.json"


def get_app_data_dir() -> Path:
    """Return the user-specific directory for persistent app data."""
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME
    return Path.home() / f".{APP_NAME.lower()}"


def get_notes_file_path() -> Path:
    """Return the JSON data file path used by the storage layer."""
    return get_app_data_dir() / DATA_FILE_NAME


def get_settings_file_path() -> Path:
    """Return the JSON settings file path used for local UI preferences."""
    return get_app_data_dir() / SETTINGS_FILE_NAME
