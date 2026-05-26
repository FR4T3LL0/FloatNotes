import unittest

from app.core.models import NoteItem, NoteList, NotesDocument


class ModelTests(unittest.TestCase):
    def test_note_list_sorts_items_by_order_when_loaded(self) -> None:
        note_list = NoteList.from_dict(
            {
                "id": "list-1",
                "name": "Sortiert",
                "created_at": "2026-05-23T20:00:00Z",
                "updated_at": "2026-05-23T20:00:00Z",
                "items": [
                    {"id": "item-2", "text": "Zweiter", "order": 2},
                    {"id": "item-1", "text": "Erster", "order": 1},
                ],
            }
        )

        self.assertEqual(["Erster", "Zweiter"], [item.text for item in note_list.items])

    def test_document_finds_selected_list_by_id(self) -> None:
        document = NotesDocument(lists=[NoteList(name="Privat", id="private")])

        self.assertEqual("Privat", document.get_list("private").name)
        self.assertIsNone(document.get_list("missing"))

    def test_completed_item_roundtrip_uses_completed_key(self) -> None:
        item = NoteItem.from_dict({"id": "item", "text": "Fertig", "done": True})

        self.assertTrue(item.completed)
        self.assertTrue(item.to_dict()["completed"])
        self.assertNotIn("done", item.to_dict())

    def test_list_crud_updates_items_and_order(self) -> None:
        note_list = NoteList.create("Privat")

        first = note_list.add_item("Erster Punkt")
        second = note_list.add_item("Zweiter Punkt")
        self.assertEqual([0, 1], [item.order for item in note_list.items])

        self.assertTrue(note_list.update_item(second.id, "Zweiter Punkt aktualisiert"))
        self.assertEqual("Zweiter Punkt aktualisiert", note_list.get_item(second.id).text)

        self.assertTrue(note_list.set_item_completed(first.id, True))
        self.assertTrue(note_list.get_item(first.id).completed)

        self.assertTrue(note_list.remove_item(first.id))
        self.assertEqual([second.id], [item.id for item in note_list.items])
        self.assertEqual([0], [item.order for item in note_list.items])

    def test_list_reorders_items_and_rejects_incomplete_ids(self) -> None:
        note_list = NoteList.create("Privat")
        first = note_list.add_item("Erster Punkt")
        second = note_list.add_item("Zweiter Punkt")
        third = note_list.add_item("Dritter Punkt")

        self.assertTrue(note_list.reorder_items([third.id, first.id, second.id]))
        self.assertEqual([third.id, first.id, second.id], [item.id for item in note_list.items])
        self.assertEqual([0, 1, 2], [item.order for item in note_list.items])
        self.assertFalse(note_list.reorder_items([third.id, first.id]))

    def test_document_add_rename_and_remove_list(self) -> None:
        document = NotesDocument.empty()

        note_list = document.add_list("Arbeit")
        note_list.rename("Fokus")

        self.assertEqual("Fokus", document.get_list(note_list.id).name)
        self.assertTrue(document.remove_list(note_list.id))
        self.assertIsNone(document.get_list(note_list.id))

    def test_document_reorders_lists_and_rejects_incomplete_ids(self) -> None:
        document = NotesDocument.empty()
        first = document.add_list("Erste Liste")
        second = document.add_list("Zweite Liste")
        third = document.add_list("Dritte Liste")

        self.assertTrue(document.reorder_lists([second.id, third.id, first.id]))
        self.assertEqual([second.id, third.id, first.id], [item.id for item in document.lists])
        self.assertFalse(document.reorder_lists([second.id, first.id]))

    def test_empty_names_and_text_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NoteList.create("   ")
        with self.assertRaises(ValueError):
            NoteItem.create("")


if __name__ == "__main__":
    unittest.main()
