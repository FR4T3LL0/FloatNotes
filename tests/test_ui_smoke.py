import os
import shutil
import unittest
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.core.models import NotesDocument
from app.core.settings import AppSettings, AppSettingsStorage
from app.core.storage import NotesStorage
from app.ui import texts as T
from app.ui.app_icon import create_app_icon
from app.ui.dialogs import ConfirmDangerDialog, TextInputDialog
from app.ui.floating_icon import FloatingIconWindow
from app.ui.main_window import MainWindow
from app.ui.task_row import TaskRowWidget

TEST_TEMP_ROOT = Path(__file__).resolve().parents[1] / ".test_tmp"


@contextmanager
def temporary_project_dir():
    TEST_TEMP_ROOT.mkdir(exist_ok=True)
    temp_dir = TEST_TEMP_ROOT / f"ui-{uuid4().hex}"
    temp_dir.mkdir()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


class UiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_main_window_and_floating_icon_can_be_created(self) -> None:
        with temporary_project_dir() as temp_dir:
            document = NotesDocument.empty()
            document.add_list("Test")
            storage = NotesStorage(Path(temp_dir) / "notes.json", backup_on_save=False)
            settings_storage = AppSettingsStorage(Path(temp_dir) / "settings.json")
            window = MainWindow(storage=storage, document=document)
            floating_icon = FloatingIconWindow(
                main_window=window,
                settings=AppSettings.default(),
                settings_storage=settings_storage,
                icon=create_app_icon(),
            )

            self.assertEqual(T.APP_NAME, window.windowTitle())
            self.assertEqual(1, window.list_widget.count())
            self.assertEqual(T.FLOATING_ICON_TITLE, floating_icon.windowTitle())

    def test_completed_list_shows_done_badge_and_hides_row_actions(self) -> None:
        with temporary_project_dir() as temp_dir:
            document = NotesDocument.empty()
            note_list = document.add_list("Terraria")
            first = note_list.add_item("Zenit")
            second = note_list.add_item("Test")
            note_list.set_item_completed(first.id, True)
            note_list.set_item_completed(second.id, True)
            storage = NotesStorage(Path(temp_dir) / "notes.json", backup_on_save=False)
            window = MainWindow(storage=storage, document=document)
            row_widget = window.item_list.itemWidget(window.item_list.item(0))

            self.assertEqual(T.ALL_DONE, window.count_badge.text())
            self.assertIsInstance(row_widget, TaskRowWidget)
            self.assertTrue(row_widget.actions_frame.isHidden())
            self.assertFalse(window.selection_hint.isHidden())

    def test_task_rows_are_custom_widgets_and_can_be_selected(self) -> None:
        with temporary_project_dir() as temp_dir:
            document = NotesDocument.empty()
            note_list = document.add_list("Inbox")
            note_item = note_list.add_item("Erste Aufgabe")
            storage = NotesStorage(Path(temp_dir) / "notes.json", backup_on_save=False)
            window = MainWindow(storage=storage, document=document)

            row_widget = window.item_list.itemWidget(window.item_list.item(0))
            self.assertIsInstance(row_widget, TaskRowWidget)

            row_widget.selected_requested.emit(note_item.id)
            self.assertEqual(
                note_item.id, window.item_list.currentItem().data(Qt.ItemDataRole.UserRole)
            )
            self.assertFalse(row_widget.actions_frame.isHidden())

    def test_custom_dialogs_can_be_created(self) -> None:
        text_dialog = TextInputDialog(
            None,
            title=T.RENAME_LIST_TITLE,
            message=T.RENAME_LIST_MESSAGE,
            initial_text="Privat",
            confirm_text=T.RENAME,
        )
        confirm_dialog = ConfirmDangerDialog(
            None,
            title=T.DELETE_LIST_TITLE,
            message="Liste dauerhaft löschen?",
            confirm_text=T.DELETE_LIST_CONFIRM,
        )

        self.assertEqual("FloatNotesDialog", text_dialog.objectName())
        self.assertEqual("Privat", text_dialog.value)
        self.assertTrue(text_dialog.confirm_button.isEnabled())
        self.assertEqual("DialogDangerButton", confirm_dialog.confirm_button.objectName())


if __name__ == "__main__":
    unittest.main()
