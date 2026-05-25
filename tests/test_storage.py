import json
import shutil
import unittest
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from app.core.models import NotesDocument
from app.core.storage import NotesStorage

TEST_TEMP_ROOT = Path(__file__).resolve().parents[1] / ".test_tmp"


@contextmanager
def temporary_project_dir():
    TEST_TEMP_ROOT.mkdir(exist_ok=True)
    temp_dir = TEST_TEMP_ROOT / f"case-{uuid4().hex}"
    temp_dir.mkdir()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


class StorageTests(unittest.TestCase):
    def test_load_creates_empty_file_on_first_start(self) -> None:
        with temporary_project_dir() as temp_dir:
            file_path = Path(temp_dir) / "notes.json"
            storage = NotesStorage(file_path)

            document = storage.load()

            self.assertEqual([], document.lists)
            self.assertTrue(file_path.exists())
            self.assertEqual({"version": 1, "lists": []}, json.loads(file_path.read_text()))

    def test_save_and_load_roundtrip(self) -> None:
        with temporary_project_dir() as temp_dir:
            file_path = Path(temp_dir) / "notes.json"
            storage = NotesStorage(file_path)
            document = NotesDocument.empty()
            note_list = document.add_list("Arbeit")
            note_list.add_item("Angebot pruefen")
            note_list.add_item("Meeting vorbereiten")

            storage.save(document, create_backup=False)
            loaded = storage.load()

            self.assertEqual(1, len(loaded.lists))
            self.assertEqual("Arbeit", loaded.lists[0].name)
            self.assertEqual(
                ["Angebot pruefen", "Meeting vorbereiten"],
                [item.text for item in loaded.lists[0].items],
            )

    def test_save_creates_backup_before_overwrite(self) -> None:
        with temporary_project_dir() as temp_dir:
            file_path = Path(temp_dir) / "notes.json"
            storage = NotesStorage(file_path)
            document = NotesDocument.empty()
            document.add_list("Privat")

            storage.save(document, create_backup=False)
            document.add_list("Ideen")
            storage.save(document)

            backups = list(Path(temp_dir).glob("notes.backup-*.json"))
            self.assertEqual(1, len(backups))
            backup_path = backups[0]
            self.assertTrue(backup_path.exists())
            backup_payload = json.loads(backup_path.read_text())
            self.assertEqual(
                ["Privat"], [note_list["name"] for note_list in backup_payload["lists"]]
            )

    def test_save_rotates_backups(self) -> None:
        with temporary_project_dir() as temp_dir:
            file_path = Path(temp_dir) / "notes.json"
            storage = NotesStorage(file_path, backup_limit=2)
            document = NotesDocument.empty()

            for index in range(4):
                document.add_list(f"Liste {index}")
                storage.save(document)

            backups = list(Path(temp_dir).glob("notes.backup-*.json"))
            self.assertEqual(2, len(backups))

    def test_corrupt_json_is_backed_up_and_replaced(self) -> None:
        with temporary_project_dir() as temp_dir:
            file_path = Path(temp_dir) / "notes.json"
            file_path.write_text("{not valid json", encoding="utf-8")
            storage = NotesStorage(file_path)

            document = storage.load()

            self.assertEqual([], document.lists)
            self.assertIsNotNone(storage.last_recovery_path)
            self.assertTrue(storage.last_recovery_path.exists())
            self.assertIn("notes.corrupt-", storage.last_recovery_path.name)
            self.assertEqual(
                "{not valid json",
                storage.last_recovery_path.read_text(encoding="utf-8"),
            )
            self.assertEqual(
                {"version": 1, "lists": []},
                json.loads(file_path.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
