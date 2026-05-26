"""Main application window for FloatNotes."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.models import NoteList, NotesDocument
from app.core.storage import NotesStorage, StorageError
from app.ui import texts as T
from app.ui.dialogs import confirm_danger, request_text
from app.ui.task_row import TaskRowWidget
from app.ui.widgets import apply_soft_shadow


class MainWindow(QMainWindow):
    """Main notes window bound to the local JSON document."""

    def __init__(
        self,
        *,
        storage: NotesStorage,
        document: NotesDocument,
        startup_message: str | None = None,
    ) -> None:
        super().__init__()
        self.storage = storage
        self.document = document
        self.selected_list_id: str | None = None
        self._is_rendering_items = False
        self._allow_close = False
        self._pending_save_message: str | None = None
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(250)
        self._save_timer.timeout.connect(self._flush_pending_save)
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self._flush_pending_save)

        self.setWindowTitle(T.APP_NAME)
        self.resize(980, 640)
        self.setMinimumSize(820, 520)
        self._build_layout()
        self._install_shortcuts()
        self._populate_lists()
        self._show_startup_message(startup_message)

    def _build_layout(self) -> None:
        root = QWidget(self)
        root.setObjectName("AppRoot")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QFrame(root)
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(24, 24, 18, 24)
        sidebar_layout.setSpacing(16)

        title = QLabel(T.APP_NAME, sidebar)
        title.setObjectName("AppTitle")

        subtitle = QLabel(T.LOCAL_NOTES)
        subtitle.setObjectName("MutedText")
        subtitle.setWordWrap(True)

        sidebar_caption = QLabel(T.LISTS, sidebar)
        sidebar_caption.setObjectName("SidebarCaption")

        self.list_widget = QListWidget(sidebar)
        self.list_widget.setObjectName("ListNavigation")
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget.currentItemChanged.connect(self._on_selected_list_changed)
        self.list_widget.model().rowsMoved.connect(self._on_lists_reordered)

        self.add_list_button = QPushButton(T.NEW_LIST, sidebar)
        self.add_list_button.clicked.connect(self._create_list)

        list_actions = QHBoxLayout()
        list_actions.setSpacing(8)
        self.rename_list_button = QPushButton(T.RENAME, sidebar)
        self.rename_list_button.setObjectName("SecondaryButton")
        self.rename_list_button.clicked.connect(self._rename_selected_list)
        self.delete_list_button = QPushButton(T.DELETE, sidebar)
        self.delete_list_button.setObjectName("DangerButton")
        self.delete_list_button.clicked.connect(self._delete_selected_list)
        list_actions.addWidget(self.rename_list_button)
        list_actions.addWidget(self.delete_list_button)

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(sidebar_caption)
        sidebar_layout.addWidget(self.list_widget, 1)
        sidebar_layout.addLayout(list_actions)
        sidebar_layout.addWidget(self.add_list_button)

        content_area = QWidget(root)
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(18)

        self.panel = QFrame(content_area)
        self.panel.setObjectName("ContentPanel")
        apply_soft_shadow(self.panel)
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        panel_body = QFrame(self.panel)
        panel_body.setObjectName("PanelBody")
        panel_body_layout = QVBoxLayout(panel_body)
        panel_body_layout.setContentsMargins(28, 28, 28, 24)
        panel_body_layout.setSpacing(18)

        header_row = QHBoxLayout()
        header_row.setSpacing(14)
        title_column = QVBoxLayout()
        title_column.setSpacing(4)

        self.section_title = QLabel(T.NO_LIST_SELECTED, panel_body)
        self.section_title.setObjectName("SectionTitle")

        self.meta_label = QLabel(
            T.ALL_NOTES_LOCAL,
            panel_body,
        )
        self.meta_label.setObjectName("MutedText")
        self.meta_label.setWordWrap(True)

        title_column.addWidget(self.section_title)
        title_column.addWidget(self.meta_label)

        self.count_badge = QLabel(T.READY, panel_body)
        self.count_badge.setObjectName("CountBadge")
        self.count_badge.setProperty("done", False)
        self.count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_row.addLayout(title_column, 1)
        header_row.addWidget(self.count_badge, alignment=Qt.AlignmentFlag.AlignTop)

        self.item_list = QListWidget(panel_body)
        self.item_list.setObjectName("NotesItems")
        self.item_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.item_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.item_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.item_list.currentItemChanged.connect(self._on_selected_item_changed)
        self.item_list.itemDoubleClicked.connect(self._edit_selected_item)
        self.item_list.model().rowsMoved.connect(self._on_items_reordered)

        self.empty_label = QLabel(panel_body)
        self.empty_label.setObjectName("EmptyState")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)

        self.selection_hint = QLabel(T.NO_TASK_SELECTED, panel_body)
        self.selection_hint.setObjectName("SelectionHint")
        self.selection_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selection_hint.setWordWrap(True)

        input_footer = QFrame(self.panel)
        input_footer.setObjectName("InputFooter")
        input_footer_layout = QHBoxLayout(input_footer)
        input_footer_layout.setContentsMargins(28, 16, 28, 16)
        input_footer_layout.setSpacing(12)

        input_frame = QFrame(input_footer)
        input_frame.setObjectName("InputBar")
        input_frame_layout = QHBoxLayout(input_frame)
        input_frame_layout.setContentsMargins(14, 6, 14, 6)
        input_frame_layout.setSpacing(10)

        self.entry = QLineEdit(input_frame)
        self.entry.setPlaceholderText(T.NEW_TASK_PLACEHOLDER)
        self.entry.textChanged.connect(self._update_actions)

        self.add_item_button = QPushButton(T.ADD, input_frame)
        self.add_item_button.setObjectName("AddItemButton")
        self.add_item_button.clicked.connect(self._add_item)
        self.entry.returnPressed.connect(self._add_item)
        input_frame_layout.addWidget(self.entry, 1)
        input_footer_layout.addWidget(input_frame, 1)
        input_footer_layout.addWidget(self.add_item_button)

        panel_body_layout.addLayout(header_row)
        panel_body_layout.addWidget(self.item_list, 1)
        panel_body_layout.addWidget(self.empty_label, 1)
        panel_body_layout.addWidget(self.selection_hint, 1)

        panel_layout.addWidget(panel_body, 1)
        panel_layout.addWidget(input_footer)

        content_layout.addWidget(self.panel, 1)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(content_area, 1)
        self.setCentralWidget(root)

    def closeEvent(self, event: object) -> None:
        self._flush_pending_save()
        if not self._allow_close:
            self.hide()
            event.ignore()
            return
        super().closeEvent(event)

    def allow_close(self) -> None:
        self._allow_close = True

    def _install_shortcuts(self) -> None:
        self._shortcuts: list[QShortcut] = []
        shortcuts = {
            "Ctrl+N": self._create_list,
            "F2": self._rename_selected_list,
            "Ctrl+E": self._edit_selected_item,
            "Delete": self._delete_selected_item,
            "Ctrl+Return": self._add_item,
            "Ctrl+F": self._focus_entry,
            "Esc": self.hide,
        }
        for sequence, handler in shortcuts.items():
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(handler)
            self._shortcuts.append(shortcut)

    def _populate_lists(self, selected_list_id: str | None = None) -> None:
        selected_id = selected_list_id or self.selected_list_id
        available_ids = {note_list.id for note_list in self.document.lists}
        if selected_id not in available_ids:
            selected_id = self.document.lists[0].id if self.document.lists else None

        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        selected_row = -1
        for note_list in self.document.lists:
            is_active = note_list.id == selected_id
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 64))
            item.setData(Qt.ItemDataRole.UserRole, note_list.id)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(
                item,
                self._create_list_row_widget(note_list, is_active=is_active),
            )
            if is_active:
                selected_row = self.list_widget.count() - 1
        if selected_row >= 0:
            self.list_widget.setCurrentRow(selected_row)
        self.list_widget.blockSignals(False)

        self.selected_list_id = selected_id
        self._render_selected_list()
        self._update_actions()

    def _create_list_row_widget(self, note_list: NoteList, *, is_active: bool) -> QWidget:
        row = QFrame(self.list_widget)
        row.setObjectName("ListRow")
        row.setProperty("active", is_active)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 10, 0)
        row_layout.setSpacing(12)

        accent = QFrame(row)
        accent.setObjectName("ListAccent")
        accent.setProperty("active", is_active)
        accent.setFixedWidth(4)

        icon = QLabel("☷", row)
        icon.setObjectName("ListIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setProperty("active", is_active)
        icon.setFixedSize(38, 38)

        name = QLabel(note_list.name, row)
        name.setObjectName("ListName")
        name.setProperty("active", is_active)

        count = QLabel(str(len(note_list.items)), row)
        count.setObjectName("ListCountBadge")
        count.setProperty("active", is_active)
        count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count.setFixedSize(34, 34)

        row_layout.addWidget(accent)
        row_layout.addWidget(icon)
        row_layout.addWidget(name, 1)
        row_layout.addWidget(count)
        return row

    def _refresh_list_row_states(self) -> None:
        for row_index in range(self.list_widget.count()):
            item = self.list_widget.item(row_index)
            widget = self.list_widget.itemWidget(item)
            if widget is None:
                continue
            is_active = item.data(Qt.ItemDataRole.UserRole) == self.selected_list_id
            for child in [widget, *widget.findChildren(QWidget)]:
                if child.property("active") is not None:
                    child.setProperty("active", is_active)
                    child.style().unpolish(child)
                    child.style().polish(child)
            widget.update()

    def _on_selected_list_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        self.selected_list_id = current.data(Qt.ItemDataRole.UserRole) if current else None
        self._refresh_list_row_states()
        self._render_selected_list()

    def _on_lists_reordered(self, *_args: object) -> None:
        ordered_ids = []
        for row in range(self.list_widget.count()):
            list_id = self.list_widget.item(row).data(Qt.ItemDataRole.UserRole)
            if isinstance(list_id, str):
                ordered_ids.append(list_id)
        if self.document.reorder_lists(ordered_ids) and self._save_document(T.LISTS_SORTED):
            self._populate_lists(self.selected_list_id)

    def _render_selected_list(self, selected_item_id: str | None = None) -> None:
        selected = self._selected_note_list()
        self._is_rendering_items = True
        self.item_list.blockSignals(True)
        self.item_list.clear()

        if selected is None:
            self.item_list.blockSignals(False)
            self._is_rendering_items = False
            self.section_title.setText(T.NO_LISTS_TITLE)
            self.meta_label.setText(T.NO_LISTS_HELP)
            self._set_count_badge(T.READY)
            self.item_list.hide()
            self.empty_label.show()
            self.empty_label.setText(T.NO_NOTES)
            self.selection_hint.hide()
            self._update_actions()
            return

        self.section_title.setText(selected.name)
        completed_count = sum(1 for item in selected.items if item.completed)
        open_count = len(selected.items) - completed_count
        self.meta_label.setText(
            T.TASKS_META.format(total=len(selected.items), completed=completed_count)
        )
        if selected.items and open_count == 0:
            self._set_count_badge(T.ALL_DONE, done=True)
        elif selected.items:
            self._set_count_badge(T.OPEN_TASKS.format(count=open_count))
        else:
            self._set_count_badge(T.READY)

        if not selected.items:
            self.item_list.blockSignals(False)
            self._is_rendering_items = False
            self.item_list.hide()
            self.empty_label.show()
            self.empty_label.setText(T.EMPTY_LIST_HELP)
            self.selection_hint.hide()
            self._update_actions()
            return

        self.empty_label.hide()
        self.item_list.show()
        selected_row = -1
        for note_item in selected.items:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 62))
            item.setData(Qt.ItemDataRole.UserRole, note_item.id)
            self.item_list.addItem(item)
            row_widget = TaskRowWidget(note_item, self.item_list)
            row_widget.completed_changed.connect(self._on_task_completed_changed)
            row_widget.selected_requested.connect(self._select_item_by_id)
            row_widget.edit_requested.connect(self._edit_item_by_id)
            row_widget.delete_requested.connect(self._delete_item_by_id)
            self.item_list.setItemWidget(item, row_widget)
            if note_item.id == selected_item_id:
                selected_row = self.item_list.count() - 1
        if selected_row >= 0:
            self.item_list.setCurrentRow(selected_row)
        else:
            self.item_list.setCurrentRow(-1)
            self.item_list.clearSelection()
        self.item_list.blockSignals(False)
        self._is_rendering_items = False
        self._refresh_task_row_states()
        self.selection_hint.setVisible(selected_row < 0)
        self._update_actions()

    def _selected_note_list(self) -> NoteList | None:
        if self.selected_list_id is None:
            return None
        return self.document.get_list(self.selected_list_id)

    def _set_count_badge(self, text: str, *, done: bool = False) -> None:
        self.count_badge.setText(text)
        self.count_badge.setProperty("done", done)
        self.count_badge.style().unpolish(self.count_badge)
        self.count_badge.style().polish(self.count_badge)

    def _selected_item_id(self) -> str | None:
        current_item = self.item_list.currentItem()
        if current_item is None or not current_item.isSelected():
            return None
        item_id = current_item.data(Qt.ItemDataRole.UserRole)
        return item_id if isinstance(item_id, str) else None

    def _create_list(self, _checked: bool = False) -> None:
        name, accepted = request_text(
            self,
            title=T.CREATE_LIST_TITLE,
            message=T.CREATE_LIST_MESSAGE,
            confirm_text=T.CREATE,
        )
        if not accepted:
            return
        clean_name = name.strip()
        if not clean_name:
            self._show_message(T.LIST_NAME_EMPTY)
            return

        note_list = self.document.add_list(clean_name)
        if self._save_document(T.LIST_SAVED):
            self._populate_lists(note_list.id)

    def _rename_selected_list(self, _checked: bool = False) -> None:
        selected = self._selected_note_list()
        if selected is None:
            return

        name, accepted = request_text(
            self,
            title=T.RENAME_LIST_TITLE,
            message=T.RENAME_LIST_MESSAGE,
            initial_text=selected.name,
            confirm_text=T.RENAME,
        )
        if not accepted:
            return
        try:
            selected.rename(name)
        except ValueError:
            self._show_message(T.LIST_NAME_EMPTY)
            return

        if self._save_document(T.LIST_RENAMED):
            self._populate_lists(selected.id)

    def _delete_selected_list(self, _checked: bool = False) -> None:
        selected = self._selected_note_list()
        if selected is None:
            return

        if not confirm_danger(
            self,
            title=T.DELETE_LIST_TITLE,
            message=T.DELETE_LIST_MESSAGE.format(name=selected.name),
            confirm_text=T.DELETE_LIST_CONFIRM,
        ):
            return

        if self.document.remove_list(selected.id) and self._save_document(T.LIST_DELETED):
            self._populate_lists()

    def _add_item(self, _checked: bool = False) -> None:
        selected = self._selected_note_list()
        if selected is None:
            return
        text = self.entry.text().strip()
        if not text:
            return

        try:
            note_item = selected.add_item(text)
        except ValueError:
            self._show_message(T.TASK_TEXT_EMPTY)
            return

        if self._save_document(T.TASK_SAVED):
            self.entry.clear()
            self._populate_lists(selected.id)
            self._render_selected_list(note_item.id)

    def _edit_selected_item(self, _trigger: object = None) -> None:
        selected = self._selected_note_list()
        item_id = self._selected_item_id()
        if selected is None or item_id is None:
            return
        self._edit_item_by_id(item_id)

    def _edit_item_by_id(self, item_id: str) -> None:
        selected = self._selected_note_list()
        if selected is None:
            return
        note_item = selected.get_item(item_id)
        if note_item is None:
            return

        text, accepted = request_text(
            self,
            title=T.EDIT_TASK_TITLE,
            message=T.EDIT_TASK_MESSAGE,
            initial_text=note_item.text,
            confirm_text=T.SAVE,
        )
        if not accepted:
            return

        try:
            selected.update_item(note_item.id, text)
        except ValueError:
            self._show_message(T.TASK_TEXT_EMPTY)
            return

        if self._save_document(T.TASK_UPDATED):
            self._populate_lists(selected.id)
            self._render_selected_list(note_item.id)

    def _delete_selected_item(self, _checked: bool = False) -> None:
        selected = self._selected_note_list()
        item_id = self._selected_item_id()
        if selected is None or item_id is None:
            return
        self._delete_item_by_id(item_id)

    def _delete_item_by_id(self, item_id: str) -> None:
        selected = self._selected_note_list()
        if selected is None:
            return
        note_item = selected.get_item(item_id)
        if note_item is None:
            return

        if not confirm_danger(
            self,
            title=T.DELETE_TASK_TITLE,
            message=T.DELETE_TASK_MESSAGE.format(text=note_item.text),
            confirm_text=T.DELETE_TASK_CONFIRM,
        ):
            return

        if selected.remove_item(item_id) and self._save_document(T.TASK_DELETED):
            self._populate_lists(selected.id)

    def _on_selected_item_changed(
        self,
        _current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        self._refresh_task_row_states()
        self._update_actions()

    def _on_task_completed_changed(self, item_id: str, completed: bool) -> None:
        if self._is_rendering_items:
            return
        selected = self._selected_note_list()
        if selected is None:
            return
        if selected.set_item_completed(item_id, completed) and self._save_document(T.STATUS_SAVED):
            self._populate_lists(selected.id)
            self._render_selected_list(item_id)

    def _refresh_task_row_states(self) -> None:
        for row in range(self.item_list.count()):
            item = self.item_list.item(row)
            widget = self.item_list.itemWidget(item)
            if isinstance(widget, TaskRowWidget):
                widget.set_active(item.isSelected())

    def _select_item_by_id(self, item_id: str) -> None:
        for row in range(self.item_list.count()):
            item = self.item_list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == item_id:
                self.item_list.setCurrentRow(row)
                return

    def _on_items_reordered(self, *_args: object) -> None:
        selected = self._selected_note_list()
        if selected is None:
            return
        ordered_ids = []
        for row in range(self.item_list.count()):
            item_id = self.item_list.item(row).data(Qt.ItemDataRole.UserRole)
            if isinstance(item_id, str):
                ordered_ids.append(item_id)
        if selected.reorder_items(ordered_ids) and self._save_document(T.TASKS_SORTED):
            self._populate_lists(selected.id)

    def _update_actions(self) -> None:
        has_list = self._selected_note_list() is not None
        has_item = self._selected_item_id() is not None
        has_entry_text = bool(self.entry.text().strip())

        self.rename_list_button.setEnabled(has_list)
        self.delete_list_button.setEnabled(has_list)
        self.entry.setEnabled(has_list)
        self.add_item_button.setEnabled(has_list and has_entry_text)
        self.selection_hint.setVisible(has_list and not self.item_list.isHidden() and not has_item)

    def _save_document(self, message: str) -> bool:
        self._pending_save_message = message
        self._save_timer.start()
        return True

    def _flush_pending_save(self) -> None:
        if self._pending_save_message is None:
            return
        message = self._pending_save_message
        self._pending_save_message = None
        self._save_timer.stop()
        try:
            self.storage.save(self.document)
        except StorageError as exc:
            QMessageBox.critical(self, T.STORAGE_ERROR_TITLE, str(exc))
            self._show_message(T.STORAGE_FAILED)
            return
        self._show_message(message)

    def _focus_entry(self) -> None:
        if self.entry.isEnabled():
            self.entry.setFocus()
            self.entry.selectAll()

    def _show_startup_message(self, startup_message: str | None) -> None:
        message = startup_message or T.STORAGE_LOCATION.format(path=self.storage.file_path)
        self.statusBar().showMessage(message)

    def _show_message(self, message: str) -> None:
        self.statusBar().showMessage(message, 5000)
