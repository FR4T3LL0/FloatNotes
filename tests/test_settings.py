import json
import shutil
import unittest
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from app.core.settings import AppSettings, AppSettingsStorage, FloatingIconSettings

TEST_TEMP_ROOT = Path(__file__).resolve().parents[1] / ".test_tmp"


@contextmanager
def temporary_project_dir():
    TEST_TEMP_ROOT.mkdir(exist_ok=True)
    temp_dir = TEST_TEMP_ROOT / f"settings-{uuid4().hex}"
    temp_dir.mkdir()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


class SettingsTests(unittest.TestCase):
    def test_missing_settings_returns_default(self) -> None:
        with temporary_project_dir() as temp_dir:
            storage = AppSettingsStorage(Path(temp_dir) / "settings.json")

            settings = storage.load()

            self.assertFalse(settings.floating_icon.has_position)

    def test_settings_roundtrip_persists_floating_icon_position(self) -> None:
        with temporary_project_dir() as temp_dir:
            file_path = Path(temp_dir) / "settings.json"
            storage = AppSettingsStorage(file_path)
            settings = AppSettings(floating_icon=FloatingIconSettings(x=120, y=240))

            storage.save(settings)
            loaded = storage.load()

            self.assertEqual(120, loaded.floating_icon.x)
            self.assertEqual(240, loaded.floating_icon.y)
            self.assertEqual(
                {"floating_icon": {"x": 120, "y": 240}},
                json.loads(file_path.read_text(encoding="utf-8")),
            )

    def test_corrupt_settings_are_backed_up(self) -> None:
        with temporary_project_dir() as temp_dir:
            file_path = Path(temp_dir) / "settings.json"
            file_path.write_text("{broken", encoding="utf-8")
            storage = AppSettingsStorage(file_path)

            settings = storage.load()

            self.assertFalse(settings.floating_icon.has_position)
            self.assertIsNotNone(storage.last_recovery_path)
            self.assertTrue(storage.last_recovery_path.exists())
            self.assertIn("settings.corrupt-", storage.last_recovery_path.name)
            self.assertEqual("{broken", storage.last_recovery_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
