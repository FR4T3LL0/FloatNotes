"""Core application services for FloatNotes."""

from app.core.autostart import (
    AutostartError,
    AutostartStatus,
    disable_autostart,
    enable_autostart,
    get_autostart_status,
)
from app.core.models import NoteItem, NoteList, NotesDocument
from app.core.settings import AppSettings, AppSettingsStorage, FloatingIconSettings
from app.core.storage import NotesStorage, StorageError

__all__ = [
    "AppSettings",
    "AppSettingsStorage",
    "AutostartError",
    "AutostartStatus",
    "FloatingIconSettings",
    "NoteItem",
    "NoteList",
    "NotesDocument",
    "NotesStorage",
    "StorageError",
    "disable_autostart",
    "enable_autostart",
    "get_autostart_status",
]
