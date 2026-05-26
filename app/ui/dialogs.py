"""Small FloatNotes-styled dialogs."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui import texts as T
from app.ui.widgets import apply_soft_shadow


class FloatNotesDialog(QDialog):
    """Base dialog with the same quiet surface language as the main window."""

    def __init__(self, parent: QWidget | None, *, title: str, message: str) -> None:
        super().__init__(parent)
        self.setObjectName("FloatNotesDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowSystemMenuHint
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)

        self.panel = QFrame(self)
        self.panel.setObjectName("DialogPanel")
        apply_soft_shadow(self.panel)
        root.addWidget(self.panel)

        self.panel_layout = QVBoxLayout(self.panel)
        self.panel_layout.setContentsMargins(24, 22, 24, 22)
        self.panel_layout.setSpacing(14)

        title_label = QLabel(title, self.panel)
        title_label.setObjectName("DialogTitle")

        message_label = QLabel(message, self.panel)
        message_label.setObjectName("DialogMessage")
        message_label.setWordWrap(True)

        self.panel_layout.addWidget(title_label)
        self.panel_layout.addWidget(message_label)


class TextInputDialog(FloatNotesDialog):
    """Dialog that asks for a single text value."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        title: str,
        message: str,
        initial_text: str = "",
        confirm_text: str = T.SAVE,
    ) -> None:
        super().__init__(parent, title=title, message=message)
        self.input = QLineEdit(self.panel)
        self.input.setObjectName("DialogInput")
        self.input.setText(initial_text)
        self.input.selectAll()
        self.input.textChanged.connect(self._sync_confirm_state)
        self.input.returnPressed.connect(self._accept_if_valid)
        self.panel_layout.addWidget(self.input)

        self.cancel_button = QPushButton(T.CANCEL, self.panel)
        self.cancel_button.setObjectName("SecondaryButton")
        self.cancel_button.clicked.connect(self.reject)

        self.confirm_button = QPushButton(confirm_text, self.panel)
        self.confirm_button.setObjectName("DialogPrimaryButton")
        self.confirm_button.setDefault(True)
        self.confirm_button.clicked.connect(self.accept)

        button_row = _button_row(self.cancel_button, self.confirm_button)
        self.panel_layout.addLayout(button_row)
        self._sync_confirm_state()

    @property
    def value(self) -> str:
        return self.input.text().strip()

    def _sync_confirm_state(self) -> None:
        self.confirm_button.setEnabled(bool(self.value))

    def _accept_if_valid(self) -> None:
        if self.value:
            self.accept()


class ConfirmDangerDialog(FloatNotesDialog):
    """Dialog for destructive confirmations."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        title: str,
        message: str,
        confirm_text: str = T.DELETE,
    ) -> None:
        super().__init__(parent, title=title, message=message)
        self.cancel_button = QPushButton(T.CANCEL, self.panel)
        self.cancel_button.setObjectName("SecondaryButton")
        self.cancel_button.clicked.connect(self.reject)

        self.confirm_button = QPushButton(confirm_text, self.panel)
        self.confirm_button.setObjectName("DialogDangerButton")
        self.confirm_button.clicked.connect(self.accept)

        button_row = _button_row(self.cancel_button, self.confirm_button)
        self.panel_layout.addLayout(button_row)


def request_text(
    parent: QWidget,
    *,
    title: str,
    message: str,
    initial_text: str = "",
    confirm_text: str = T.SAVE,
) -> tuple[str, bool]:
    """Show a styled text dialog and return the stripped value plus accepted state."""
    dialog = TextInputDialog(
        parent,
        title=title,
        message=message,
        initial_text=initial_text,
        confirm_text=confirm_text,
    )
    accepted = dialog.exec() == QDialog.DialogCode.Accepted
    return dialog.value, accepted


def confirm_danger(
    parent: QWidget,
    *,
    title: str,
    message: str,
    confirm_text: str = T.DELETE,
) -> bool:
    """Show a styled destructive confirmation dialog."""
    dialog = ConfirmDangerDialog(
        parent,
        title=title,
        message=message,
        confirm_text=confirm_text,
    )
    return dialog.exec() == QDialog.DialogCode.Accepted


def _button_row(*buttons: QPushButton) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setContentsMargins(0, 6, 0, 0)
    row.setSpacing(10)
    row.addStretch(1)
    for button in buttons:
        row.addWidget(button)
    return row
