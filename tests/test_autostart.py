import shutil
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import app.core.autostart as autostart
from app.core.autostart import (
    build_autostart_command,
    disable_autostart,
    enable_autostart,
    get_autostart_status,
    get_default_autostart_target,
    is_autostart_supported,
)

TEST_TEMP_ROOT = Path(__file__).resolve().parents[1] / ".test_tmp"


@contextmanager
def temporary_project_dir():
    TEST_TEMP_ROOT.mkdir(exist_ok=True)
    temp_dir = TEST_TEMP_ROOT / f"autostart-{uuid4().hex}"
    temp_dir.mkdir()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


class AutostartTests(unittest.TestCase):
    def test_build_autostart_command_quotes_executable_path(self) -> None:
        command = build_autostart_command(r"C:\Program Files\FloatNotes\FloatNotes.exe")

        self.assertEqual(r'"C:\Program Files\FloatNotes\FloatNotes.exe"', command)

    def test_default_target_prefers_built_exe_under_project_root(self) -> None:
        with temporary_project_dir() as temp_dir:
            exe_path = Path(temp_dir) / "dist" / "FloatNotes" / "FloatNotes.exe"
            exe_path.parent.mkdir(parents=True)
            exe_path.write_text("placeholder", encoding="utf-8")

            self.assertEqual(exe_path, get_default_autostart_target(Path(temp_dir)))

    def test_default_target_is_none_without_built_exe(self) -> None:
        with temporary_project_dir() as temp_dir:
            self.assertIsNone(get_default_autostart_target(Path(temp_dir)))

    def test_autostart_supported_returns_boolean(self) -> None:
        self.assertIsInstance(is_autostart_supported(), bool)

    def test_enable_and_disable_autostart_with_mocked_registry(self) -> None:
        fake_registry = FakeWinreg()
        with temporary_project_dir() as temp_dir:
            exe_path = Path(temp_dir) / "FloatNotes.exe"
            exe_path.write_text("placeholder", encoding="utf-8")

            with (
                patch.object(autostart, "is_autostart_supported", return_value=True),
                patch.object(autostart, "_winreg", return_value=fake_registry),
            ):
                command = enable_autostart(exe_path)
                status = get_autostart_status()

                self.assertTrue(status.enabled)
                self.assertEqual(command, status.command)
                self.assertTrue(disable_autostart())
                self.assertFalse(get_autostart_status().enabled)


class FakeKey:
    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False


class FakeWinreg:
    HKEY_CURRENT_USER = object()
    KEY_READ = 1
    KEY_SET_VALUE = 2
    REG_SZ = 1

    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def OpenKey(self, _root, _path, _reserved, _access):
        return FakeKey()

    def CreateKeyEx(self, _root, _path, _reserved, _access):
        return FakeKey()

    def QueryValueEx(self, _key, name):
        if name not in self.values:
            raise FileNotFoundError(name)
        return self.values[name], self.REG_SZ

    def SetValueEx(self, _key, name, _reserved, _value_type, value):
        self.values[name] = value

    def DeleteValue(self, _key, name):
        if name not in self.values:
            raise FileNotFoundError(name)
        del self.values[name]


if __name__ == "__main__":
    unittest.main()
