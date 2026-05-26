"""Single-instance guard for FloatNotes."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QLockFile

from app.core.app_paths import get_app_data_dir

LOCK_FILE_NAME = "floatnotes.lock"


class SingleInstanceGuard:
    """Prevent multiple FloatNotes processes from running in parallel."""

    def __init__(self, lock_path: Path | None = None) -> None:
        self.lock_path = lock_path or get_app_data_dir() / LOCK_FILE_NAME
        self.lock_file = QLockFile(str(self.lock_path))
        self.lock_file.setStaleLockTime(0)

    def acquire(self) -> bool:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        return self.lock_file.tryLock(100)

    def release(self) -> None:
        self.lock_file.unlock()
