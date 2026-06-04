import os
import unittest
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.core.single_instance import SingleInstanceGuard

TEST_TEMP_ROOT = Path(__file__).resolve().parents[1] / ".test_tmp"


class SingleInstanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_second_guard_cannot_acquire_same_lock(self) -> None:
        TEST_TEMP_ROOT.mkdir(exist_ok=True)
        lock_path = TEST_TEMP_ROOT / f"{uuid4().hex}.lock"
        first = SingleInstanceGuard(lock_path)
        second = SingleInstanceGuard(lock_path)
        try:
            self.assertTrue(first.acquire())
            self.assertFalse(second.acquire())
        finally:
            first.release()
            second.release()


if __name__ == "__main__":
    unittest.main()
