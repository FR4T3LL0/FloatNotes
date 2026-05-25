"""Windows autostart helpers for FloatNotes.

This module only changes autostart when its enable/disable functions are called
explicitly. It performs no work at import time.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

AUTOSTART_APP_NAME = "FloatNotes"
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


class AutostartError(RuntimeError):
    """Raised when autostart cannot be read or changed."""


@dataclass(frozen=True)
class AutostartStatus:
    """Current autostart state for the current Windows user."""

    supported: bool
    enabled: bool
    command: str | None = None


def is_autostart_supported() -> bool:
    """Return whether the current platform supports the Windows Run key."""
    return platform.system() == "Windows"


def build_autostart_command(executable_path: str | Path) -> str:
    """Return the command stored in the Windows Run key."""
    return _quote_windows_argument(Path(executable_path))


def get_default_autostart_target(project_root: Path | None = None) -> Path | None:
    """Return the executable that should be used for autostart.

    In a PyInstaller build this is `sys.executable`. During development we only
    return the built EXE if it exists, so source runs do not accidentally
    autostart `python.exe`.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable)

    root = project_root or Path(__file__).resolve().parents[2]
    built_exe = root / "dist" / "FloatNotes" / "FloatNotes.exe"
    if built_exe.exists():
        return built_exe
    return None


def get_autostart_status(value_name: str = AUTOSTART_APP_NAME) -> AutostartStatus:
    """Return whether FloatNotes is registered for current-user autostart."""
    if not is_autostart_supported():
        return AutostartStatus(supported=False, enabled=False)

    winreg = _winreg()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            command, _value_type = winreg.QueryValueEx(key, value_name)
    except FileNotFoundError:
        return AutostartStatus(supported=True, enabled=False)
    except OSError as exc:
        raise AutostartError("Could not read Windows autostart status.") from exc

    return AutostartStatus(supported=True, enabled=bool(command), command=str(command))


def enable_autostart(
    executable_path: str | Path | None = None,
    value_name: str = AUTOSTART_APP_NAME,
) -> str:
    """Enable current-user autostart and return the stored command."""
    if not is_autostart_supported():
        raise AutostartError("Autostart is only supported on Windows.")

    target = (
        Path(executable_path) if executable_path is not None else get_default_autostart_target()
    )
    if target is None:
        raise AutostartError("Build the EXE first or pass an explicit executable path.")
    if not target.exists():
        raise AutostartError(f"Autostart target does not exist: {target}")

    command = build_autostart_command(target)
    winreg = _winreg()
    try:
        with winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, command)
    except OSError as exc:
        raise AutostartError("Could not enable Windows autostart.") from exc
    return command


def disable_autostart(value_name: str = AUTOSTART_APP_NAME) -> bool:
    """Disable current-user autostart. Returns True when a value was removed."""
    if not is_autostart_supported():
        raise AutostartError("Autostart is only supported on Windows.")

    winreg = _winreg()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, value_name)
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise AutostartError("Could not disable Windows autostart.") from exc
    return True


def _quote_windows_argument(value: str | Path) -> str:
    text = str(value)
    return f'"{text.replace(chr(34), chr(92) + chr(34))}"'


def _winreg() -> Any:
    try:
        import winreg
    except ImportError as exc:
        raise AutostartError("The Windows registry API is not available.") from exc
    return winreg
