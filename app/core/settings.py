"""Local UI settings for FloatNotes."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.app_paths import get_settings_file_path


@dataclass
class FloatingIconSettings:
    """Persisted settings for the floating launcher."""

    x: int | None = None
    y: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FloatingIconSettings":
        return cls(
            x=_optional_int(data.get("x")),
            y=_optional_int(data.get("y")),
        )

    def to_dict(self) -> dict[str, int | None]:
        return {
            "x": self.x,
            "y": self.y,
        }

    @property
    def has_position(self) -> bool:
        return self.x is not None and self.y is not None


@dataclass
class AppSettings:
    """Root settings document for lightweight UI preferences."""

    floating_icon: FloatingIconSettings = field(default_factory=FloatingIconSettings)

    @classmethod
    def default(cls) -> "AppSettings":
        return cls()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppSettings":
        if not isinstance(data, dict):
            raise ValueError("Settings document must be a JSON object.")
        raw_floating_icon = data.get("floating_icon", {})
        if not isinstance(raw_floating_icon, dict):
            raw_floating_icon = {}
        return cls(floating_icon=FloatingIconSettings.from_dict(raw_floating_icon))

    def to_dict(self) -> dict[str, Any]:
        return {
            "floating_icon": self.floating_icon.to_dict(),
        }


class AppSettingsStorage:
    """Load and save lightweight local settings."""

    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path = file_path or get_settings_file_path()
        self.last_recovery_path: Path | None = None

    def load(self) -> AppSettings:
        self.last_recovery_path = None
        if not self.file_path.exists():
            return AppSettings.default()

        try:
            payload = json.loads(self.file_path.read_text(encoding="utf-8"))
            return AppSettings.from_dict(payload)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            self.last_recovery_path = self._backup_corrupt_file()
            return AppSettings.default()

    def save(self, settings: AppSettings) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.file_path.with_name(f"{self.file_path.name}.tmp")
        temp_path.write_text(
            json.dumps(settings.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temp_path.replace(self.file_path)

    def _backup_corrupt_file(self) -> Path:
        recovery_path = self.file_path.with_name(
            f"{self.file_path.stem}.corrupt-{_timestamp()}{self.file_path.suffix}"
        )
        shutil.copy2(self.file_path, recovery_path)
        return recovery_path


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _timestamp() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")
