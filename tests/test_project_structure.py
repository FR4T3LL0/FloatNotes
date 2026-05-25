import unittest

from app.core.app_paths import (
    APP_NAME,
    DATA_FILE_NAME,
    SETTINGS_FILE_NAME,
    get_notes_file_path,
    get_settings_file_path,
)


class AppPathsTests(unittest.TestCase):
    def test_notes_file_path_uses_app_name(self) -> None:
        path = get_notes_file_path()

        self.assertIn(APP_NAME, path.parts)
        self.assertEqual(DATA_FILE_NAME, path.name)

    def test_settings_file_path_uses_app_name(self) -> None:
        path = get_settings_file_path()

        self.assertIn(APP_NAME, path.parts)
        self.assertEqual(SETTINGS_FILE_NAME, path.name)


if __name__ == "__main__":
    unittest.main()
