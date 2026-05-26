"""System tray integration for FloatNotes."""

from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget

from app.ui import texts as T


class TrayIconController:
    """Small system tray controller for app-level actions."""

    def __init__(self, *, main_window: QWidget, floating_icon: QWidget, icon: QIcon) -> None:
        self.main_window = main_window
        self.floating_icon = floating_icon
        self.tray_icon = QSystemTrayIcon(icon, main_window)
        self.tray_icon.setToolTip(T.APP_NAME)
        self.menu = self._build_menu()
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self._on_activated)

    def show(self) -> None:
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()

    def _build_menu(self) -> QMenu:
        menu = QMenu()
        self.toggle_action = menu.addAction(T.OPEN)
        show_launcher_action = menu.addAction(T.SHOW_FLOATING_ICON)
        menu.addSeparator()
        quit_action = menu.addAction(T.QUIT)

        menu.aboutToShow.connect(self._sync_menu_state)
        self.toggle_action.triggered.connect(self._toggle_main_window)
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

    def _toggle_main_window(self) -> None:
        if self.main_window.isVisible() and not self.main_window.isMinimized():
            self.main_window.hide()
            return
        self._show_main_window()

    def _show_floating_icon(self) -> None:
        self.floating_icon.show()
        self.floating_icon.raise_()

    def _quit(self) -> None:
        if hasattr(self.main_window, "allow_close"):
            self.main_window.allow_close()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _sync_menu_state(self) -> None:
        if self.main_window.isVisible() and not self.main_window.isMinimized():
            self.toggle_action.setText(T.HIDE)
        else:
            self.toggle_action.setText(T.OPEN)
