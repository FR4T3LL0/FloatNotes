"""System tray integration for FloatNotes."""

from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget


class TrayIconController:
    """Small system tray controller for app-level actions."""

    def __init__(self, *, main_window: QWidget, floating_icon: QWidget, icon: QIcon) -> None:
        self.main_window = main_window
        self.floating_icon = floating_icon
        self.tray_icon = QSystemTrayIcon(icon, main_window)
        self.tray_icon.setToolTip("FloatNotes")
        self.menu = self._build_menu()
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self._on_activated)

    def show(self) -> None:
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()

    def _build_menu(self) -> QMenu:
        menu = QMenu()
        open_action = menu.addAction("Öffnen")
        hide_action = menu.addAction("Ausblenden")
        show_launcher_action = menu.addAction("Floating-Icon anzeigen")
        menu.addSeparator()
        quit_action = menu.addAction("Beenden")

        open_action.triggered.connect(self._show_main_window)
        hide_action.triggered.connect(self.main_window.hide)
        show_launcher_action.triggered.connect(self._show_floating_icon)
        quit_action.triggered.connect(self._quit)
        return menu

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.main_window.isVisible() and not self.main_window.isMinimized():
                self.main_window.hide()
            else:
                self._show_main_window()

    def _show_main_window(self) -> None:
        if self.main_window.isMinimized():
            self.main_window.showNormal()
        else:
            self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _show_floating_icon(self) -> None:
        self.floating_icon.show()
        self.floating_icon.raise_()

    def _quit(self) -> None:
        app = QApplication.instance()
        if app is not None:
            app.quit()
