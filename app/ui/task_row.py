"""Custom task row widget for the notes list."""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from app.core.models import NoteItem
from app.ui import texts as T


class TaskRowWidget(QFrame):
    """Compact, controllable row for a single task."""

    completed_changed = Signal(str, bool)
    selected_requested = Signal(str)
    edit_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, note_item: NoteItem, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.note_item = note_item
        self.setObjectName("TaskRow")
        self.setProperty("active", False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 9, 12, 9)
        layout.setSpacing(12)

        self.active_accent = QFrame(self)
        self.active_accent.setObjectName("TaskActiveAccent")
        self.active_accent.setProperty("active", False)
        self.active_accent.setFixedSize(3, 28)

        self.checkbox = QCheckBox(self)
        self.checkbox.setObjectName("TaskCheck")
        self.checkbox.setChecked(note_item.completed)
        self.checkbox.toggled.connect(self._on_completed_changed)

        self.text_label = QLabel(note_item.text, self)
        self.text_label.setObjectName("TaskText")
        self.text_label.setProperty("completed", note_item.completed)

        self.actions_frame = QFrame(self)
        self.actions_frame.setObjectName("TaskRowActions")
        actions_layout = QHBoxLayout(self.actions_frame)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(6)

        self.edit_button = QPushButton(T.EDIT, self.actions_frame)
        self.edit_button.setObjectName("TaskRowButton")
        self.edit_button.setIcon(_create_edit_icon(QColor("#475467")))
        self.edit_button.setIconSize(QSize(14, 14))
        self.edit_button.clicked.connect(lambda: self.edit_requested.emit(self.note_item.id))

        self.delete_button = QPushButton(T.DELETE, self.actions_frame)
        self.delete_button.setObjectName("TaskRowDangerButton")
        self.delete_button.setIcon(_create_delete_icon(QColor("#B42318")))
        self.delete_button.setIconSize(QSize(14, 14))
        self.delete_button.clicked.connect(lambda: self.delete_requested.emit(self.note_item.id))

        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.delete_button)

        layout.addWidget(self.active_accent)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.actions_frame)
        self.set_active(False)

    def set_active(self, active: bool) -> None:
        self.setProperty("active", active)
        self.active_accent.setProperty("active", active)
        self.actions_frame.setVisible(active)
        self.actions_frame.setProperty("active", active)
        self.checkbox.setProperty("active", active)
        self.text_label.setProperty("active", active)
        for widget in (
            self,
            self.active_accent,
            self.actions_frame,
            self.checkbox,
            self.text_label,
            self.edit_button,
            self.delete_button,
        ):
            self._refresh_style(widget)

    def mousePressEvent(self, event: object) -> None:
        self.selected_requested.emit(self.note_item.id)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mousePressEvent(event)

    def _on_completed_changed(self, completed: bool) -> None:
        self.text_label.setProperty("completed", completed)
        self._refresh_style(self.text_label)
        self.completed_changed.emit(self.note_item.id, completed)

    @staticmethod
    def _refresh_style(widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()


def _create_edit_icon(color: QColor) -> QIcon:
    pixmap = _transparent_icon_pixmap()
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(
        color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin
    )
    painter.setPen(pen)
    painter.drawLine(6, 18, 18, 6)
    painter.drawLine(16, 4, 20, 8)
    painter.drawLine(17, 5, 19, 7)
    painter.drawLine(5, 19, 8, 18)
    painter.drawLine(5, 19, 6, 16)
    painter.end()
    return QIcon(pixmap)


def _create_delete_icon(color: QColor) -> QIcon:
    pixmap = _transparent_icon_pixmap()
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(
        color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin
    )
    painter.setPen(pen)
    painter.drawLine(8, 8, 18, 8)
    painter.drawLine(10, 8, 11, 20)
    painter.drawLine(16, 8, 15, 20)
    painter.drawLine(9, 20, 17, 20)
    painter.drawLine(12, 5, 14, 5)
    painter.drawLine(11, 6, 15, 6)
    painter.drawLine(12, 11, 12, 17)
    painter.drawLine(15, 11, 15, 17)
    painter.drawRoundedRect(QRectF(9, 8, 8, 12), 1.5, 1.5)
    painter.end()
    return QIcon(pixmap)


def _transparent_icon_pixmap() -> QPixmap:
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    return pixmap
