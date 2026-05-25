"""JSON storage for FloatNotes."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.app_paths import get_notes_file_path
from app.core.models import NotesDocument

DEFAULT_BACKUP_LIMIT = 5


class StorageError(RuntimeError):
    """Raised when the notes file cannot be read or written safely."""


class NotesStorage:
    """Load and save the local notes JSON document."""

    def __init__(
        self,
        file_path: Path | None = None,
        *,
        backup_on_save: bool = True,
        backup_limit: int = DEFAULT_BACKUP_LIMIT,
    ) -> None:
        self.file_path = file_path or get_notes_file_path()
        self.backup_on_save = backup_on_save
        self.backup_limit = max(1, backup_limit)
        self.last_recovery_path: Path | None = None
        self.last_error: str | None = None

    def load(self) -> NotesDocument:
        """Load the notes document, creating or recovering the file when needed."""
        self.last_recovery_path = None
        self.last_error = None

        if not self.file_path.exists():
            document = NotesDocument.empty()
            self.save(document, create_backup=False)
            return document

        try:
            payload = json.loads(self.file_path.read_text(encoding="utf-8"))
            return NotesDocument.from_dict(payload)
        except OSError as exc:
            raise StorageError(f"Could not read notes file: {self.file_path}") from exc
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            self.last_error = str(exc)
            self.last_recovery_path = self._backup_corrupt_file()
            document = NotesDocument.empty()
            self.save(document, create_backup=False)
            return document

    def save(self, document: NotesDocument, *, create_backup: bool | None = None) -> None:
        """Save the notes document atomically as JSON."""
        if not isinstance(document, NotesDocument):
            raise TypeError("document must be a NotesDocument instance.")

        should_backup = self.backup_on_save if create_backup is None else create_backup
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            if should_backup and self.file_path.exists():
                self._backup_current_file()
            self._write_json(document.to_dict())
        except OSError as exc:
            raise StorageError(f"Could not write notes file: {self.file_path}") from exc

    def _write_json(self, payload: dict[str, Any]) -> None:
        temp_path = self.file_path.with_name(f"{self.file_path.name}.tmp")
        serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        temp_path.write_text(serialized, encoding="utf-8")
        temp_path.replace(self.file_path)

    def _backup_current_file(self) -> Path:
        timestamp = _timestamp()
        backup_path = self.file_path.with_name(
            f"{self.file_path.stem}.backup-{timestamp}{self.file_path.suffix}"
        )
        shutil.copy2(self.file_path, backup_path)
        self._rotate_backups()
        return backup_path

    def _backup_corrupt_file(self) -> Path:
        recovery_path = self.file_path.with_name(
            f"{self.file_path.stem}.corrupt-{_timestamp()}{self.file_path.suffix}"
        )
        shutil.copy2(self.file_path, recovery_path)
        return recovery_path

    def _rotate_backups(self) -> None:
        backups = sorted(
            self.file_path.parent.glob(f"{self.file_path.stem}.backup-*{self.file_path.suffix}"),
            key=lambda path: path.name,
            reverse=True,
        )
        for old_backup in backups[self.backup_limit :]:
            old_backup.unlink(missing_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")
