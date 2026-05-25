"""Application entry point for FloatNotes."""

from __future__ import annotations

import sys


def main() -> int:
    """Start the Qt application."""
    try:
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QApplication
    except ModuleNotFoundError as exc:
        if exc.name == "PySide6":
            raise SystemExit(
                "PySide6 is not installed. Run: pip install -r requirements.txt"
            ) from exc
        raise

    from app.core.models import NotesDocument
    from app.core.settings import AppSettingsStorage
    from app.core.storage import NotesStorage, StorageError
    from app.ui.app_icon import create_app_icon
    from app.ui.floating_icon import FloatingIconWindow
    from app.ui.main_window import MainWindow
    from app.ui.styles import APP_STYLE
    from app.ui.tray_icon import TrayIconController

    app = QApplication(sys.argv)
    app.setApplicationName("FloatNotes")
    app.setOrganizationName("FloatNotes")
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(APP_STYLE)
    app_icon: QIcon = create_app_icon()
    app.setWindowIcon(app_icon)

    storage = NotesStorage()
    settings_storage = AppSettingsStorage()
    settings = settings_storage.load()
    startup_message = None
    try:
        document = storage.load()
    except StorageError as exc:
        document = NotesDocument.empty()
        startup_message = f"Speicher konnte nicht geladen werden: {exc}"
    else:
        if storage.last_recovery_path is not None:
            startup_message = f"Beschädigte JSON gesichert: {storage.last_recovery_path}"

    window = MainWindow(storage=storage, document=document, startup_message=startup_message)
    window.setWindowIcon(app_icon)
    floating_icon = FloatingIconWindow(
        main_window=window,
        settings=settings,
        settings_storage=settings_storage,
        icon=app_icon,
    )
    floating_icon.show()
    tray_icon = TrayIconController(main_window=window, floating_icon=floating_icon, icon=app_icon)
    tray_icon.show()

    app.floatnotes_floating_icon = floating_icon
    app.floatnotes_tray_icon = tray_icon

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
