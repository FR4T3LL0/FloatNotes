"""Data models for notes, lists, and documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

SCHEMA_VERSION = 1


def new_id() -> str:
    """Return a stable random id for persisted entities."""
    return str(uuid4())


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _string_or_default(value: Any, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return default


def _int_or_default(value: Any, default: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass
class NoteItem:
    """Single bullet point inside a note list."""

    text: str
    id: str = field(default_factory=new_id)
    completed: bool = False
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    order: int = 0

    @classmethod
    def create(cls, text: str, order: int = 0) -> "NoteItem":
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Note item text cannot be empty.")
        now = utc_now_iso()
        return cls(text=clean_text, created_at=now, updated_at=now, order=order)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NoteItem":
        if not isinstance(data, dict):
            raise ValueError("Note item must be a JSON object.")

        text = data.get("text", "")
        if text is None:
            text = ""
        if not isinstance(text, str):
            text = str(text)

        now = utc_now_iso()
        return cls(
            id=_string_or_default(data.get("id"), new_id()),
            text=text,
            completed=bool(data.get("completed", data.get("done", False))),
            created_at=_string_or_default(data.get("created_at"), now),
            updated_at=_string_or_default(data.get("updated_at"), now),
            order=_int_or_default(data.get("order"), 0),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "completed": self.completed,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "order": self.order,
        }

    def update_text(self, text: str) -> None:
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Note item text cannot be empty.")
        self.text = clean_text
        self.touch()

    def set_completed(self, completed: bool) -> None:
        self.completed = completed
        self.touch()

    def touch(self) -> None:
        self.updated_at = utc_now_iso()


@dataclass
class NoteList:
    """Named collection of note items."""

    name: str
    id: str = field(default_factory=new_id)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    items: list[NoteItem] = field(default_factory=list)

    @classmethod
    def create(cls, name: str) -> "NoteList":
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Note list name cannot be empty.")
        now = utc_now_iso()
        return cls(name=clean_name, created_at=now, updated_at=now)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NoteList":
        if not isinstance(data, dict):
            raise ValueError("Note list must be a JSON object.")

        raw_items = data.get("items", [])
        if raw_items is None:
            raw_items = []
        if not isinstance(raw_items, list):
            raise ValueError("Note list items must be a JSON array.")

        items: list[NoteItem] = []
        for index, raw_item in enumerate(raw_items):
            item = NoteItem.from_dict(raw_item)
            if "order" not in raw_item:
                item.order = index
            items.append(item)

        items.sort(key=lambda item: item.order)
        now = utc_now_iso()
        return cls(
            id=_string_or_default(data.get("id"), new_id()),
            name=_string_or_default(data.get("name"), "Untitled"),
            created_at=_string_or_default(data.get("created_at"), now),
            updated_at=_string_or_default(data.get("updated_at"), now),
            items=items,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "items": [item.to_dict() for item in sorted(self.items, key=lambda item: item.order)],
        }

    def rename(self, name: str) -> None:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Note list name cannot be empty.")
        self.name = clean_name
        self.touch()

    def add_item(self, text: str) -> NoteItem:
        item = NoteItem.create(text=text, order=self.next_order())
        self.items.append(item)
        self.touch()
        return item

    def get_item(self, item_id: str) -> NoteItem | None:
        return next((item for item in self.items if item.id == item_id), None)

    def update_item(self, item_id: str, text: str) -> bool:
        item = self.get_item(item_id)
        if item is None:
            return False
        item.update_text(text)
        self.touch()
        return True

    def set_item_completed(self, item_id: str, completed: bool) -> bool:
        item = self.get_item(item_id)
        if item is None:
            return False
        item.set_completed(completed)
        self.touch()
        return True

    def remove_item(self, item_id: str) -> bool:
        original_count = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]
        removed = len(self.items) != original_count
        if removed:
            self._normalize_item_order()
            self.touch()
        return removed

    def next_order(self) -> int:
        if not self.items:
            return 0
        return max(item.order for item in self.items) + 1

    def touch(self) -> None:
        self.updated_at = utc_now_iso()

    def _normalize_item_order(self) -> None:
        ordered_items = sorted(self.items, key=lambda item: item.order)
        for index, item in enumerate(ordered_items):
            item.order = index
        self.items = ordered_items

    def reorder_items(self, item_ids: list[str]) -> bool:
        if set(item_ids) != {item.id for item in self.items}:
            return False
        items_by_id = {item.id: item for item in self.items}
        self.items = [items_by_id[item_id] for item_id in item_ids]
        for index, item in enumerate(self.items):
            item.order = index
        self.touch()
        return True


@dataclass
class NotesDocument:
    """Root JSON document for all persisted notes."""

    version: int = SCHEMA_VERSION
    lists: list[NoteList] = field(default_factory=list)

    @classmethod
    def empty(cls) -> "NotesDocument":
        return cls()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NotesDocument":
        if not isinstance(data, dict):
            raise ValueError("Notes document must be a JSON object.")

        raw_lists = data.get("lists", [])
        if raw_lists is None:
            raw_lists = []
        if not isinstance(raw_lists, list):
            raise ValueError("Notes document lists must be a JSON array.")

        version = _int_or_default(data.get("version"), SCHEMA_VERSION)
        return cls(
            version=version,
            lists=[NoteList.from_dict(raw_list) for raw_list in raw_lists],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "lists": [note_list.to_dict() for note_list in self.lists],
        }

    def add_list(self, name: str) -> NoteList:
        note_list = NoteList.create(name)
        self.lists.append(note_list)
        return note_list

    def get_list(self, list_id: str) -> NoteList | None:
        return next((note_list for note_list in self.lists if note_list.id == list_id), None)

    def remove_list(self, list_id: str) -> bool:
        original_count = len(self.lists)
        self.lists = [note_list for note_list in self.lists if note_list.id != list_id]
        return len(self.lists) != original_count

    def reorder_lists(self, list_ids: list[str]) -> bool:
        if set(list_ids) != {note_list.id for note_list in self.lists}:
            return False
        lists_by_id = {note_list.id: note_list for note_list in self.lists}
        self.lists = [lists_by_id[list_id] for list_id in list_ids]
        return True
