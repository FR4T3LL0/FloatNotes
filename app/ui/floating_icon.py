"""Always-on-top floating launcher for FloatNotes."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QIcon,
    QLinearGradient,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QWidget

from app.core.autostart import (
    AutostartError,
    disable_autostart,
    enable_autostart,
    get_autostart_status,
    get_default_autostart_target,
)
from app.core.settings import AppSettings, AppSettingsStorage
from app.ui import texts as T
from app.ui.geometry import clamp_window_position


class FloatingIconWindow(QWidget):
    """Small draggable launcher that toggles the main notes window."""

    ICON_SIZE = 62
    CLICK_DRAG_THRESHOLD = 6
    SCREEN_MARGIN = 10
    DEFAULT_OPACITY = 0.86
    HOVER_OPACITY = 0.96
    DRAG_OPACITY = 0.92

    def __init__(
        self,
        *,
        main_window: QWidget,
        settings: AppSettings,
        settings_storage: AppSettingsStorage,
        icon: QIcon | None = None,
    ) -> None:
        super().__init__()
        self.main_window = main_window
        self.settings = settings
        self.settings_storage = settings_storage
        self._press_global_pos: QPoint | None = None
        self._press_window_pos: QPoint | None = None
        self._dragged = False
        self._hovered = False
        self._pressed = False
        self._opacity_animation: QPropertyAnimation | None = None

        self.setWindowTitle(T.FLOATING_ICON_TITLE)
        if icon is not None:
            self.setWindowIcon(icon)
        self.setFixedSize(self.ICON_SIZE, self.ICON_SIZE)
        self.setWindowOpacity(self.DEFAULT_OPACITY)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(T.FLOATING_ICON_TOOLTIP)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self._restore_or_set_default_position()

    def enterEvent(self, event: object) -> None:
        self._hovered = True
        self._animate_opacity(self.HOVER_OPACITY)
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: object) -> None:
        self._hovered = False
        if not self._pressed:
            self._animate_opacity(self.DEFAULT_OPACITY)
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_global_pos = event.globalPosition().toPoint()
            self._press_window_pos = self.pos()
            self._dragged = False
            self._pressed = True
            self._animate_opacity(self.DRAG_OPACITY)
            self.update()
            event.accept()
            return
        if event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._press_global_pos is None or self._press_window_pos is None:
            super().mouseMoveEvent(event)
            return

        delta = event.globalPosition().toPoint() - self._press_global_pos
        if delta.manhattanLength() >= self.CLICK_DRAG_THRESHOLD:
            self._dragged = True
        if self._dragged:
            self.move(
                self._bounded_position(
                    self._press_window_pos + delta, event.globalPosition().toPoint()
                )
            )
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            was_dragged = self._dragged
            self._press_global_pos = None
            self._press_window_pos = None
            self._dragged = False
            self._pressed = False
            self._animate_opacity(self.HOVER_OPACITY if self._hovered else self.DEFAULT_OPACITY)
            self.update()
            if was_dragged:
                self.move(self._bounded_position(self.pos(), event.globalPosition().toPoint()))
                self._save_position()
            else:
                self._toggle_main_window()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        shadow_bounds = QRectF(7, 9, self.width() - 14, self.height() - 14)
        painter.setPen(Qt.PenStyle.NoPen)
        shadow_alpha = 42 if self._hovered else 28
        painter.setBrush(QColor(31, 41, 51, shadow_alpha))
        painter.drawRoundedRect(shadow_bounds, 18, 18)
        painter.setBrush(QColor(31, 41, 51, 14))
        painter.drawRoundedRect(shadow_bounds.adjusted(-2, -2, 2, 3), 20, 20)

        bounds = QRectF(5, 4, self.width() - 10, self.height() - 10)
        glass = QLinearGradient(bounds.topLeft(), bounds.bottomRight())
        top_alpha = 250 if self._hovered else 240
        bottom_alpha = 232 if self._hovered else 218
        glass.setColorAt(0.0, QColor(255, 255, 255, top_alpha))
        glass.setColorAt(1.0, QColor(238, 242, 247, bottom_alpha))
        painter.setBrush(glass)
        painter.setPen(QPen(QColor(255, 255, 255, 210), 1))
        painter.drawRoundedRect(bounds, 18, 18)

        note_bounds = QRectF(18, 16, 26, 30)
        painter.setBrush(QColor(37, 99, 235, 26))
        accent_alpha = 190 if self._hovered else 160
        painter.setPen(QPen(QColor(37, 99, 235, accent_alpha), 1.4))
        painter.drawRoundedRect(note_bounds, 7, 7)

        painter.setPen(QPen(QColor(31, 41, 51, 190), 1.6))
        painter.drawLine(24, 26, 38, 26)
        painter.drawLine(24, 32, 36, 32)
        painter.drawLine(24, 38, 33, 38)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(37, 99, 235, 210))
        painter.drawEllipse(QRectF(39, 18, 6, 6))

    def _toggle_main_window(self) -> None:
        if self.main_window.isVisible() and not self.main_window.isMinimized():
            self.main_window.hide()
            return
        self._show_main_window()

    def _show_main_window(self) -> None:
        if self.main_window.isMinimized():
            self.main_window.showNormal()
        else:
            self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _show_context_menu(self, global_pos: QPoint) -> None:
        menu = QMenu(self)
        toggle_action_text = T.HIDE if self.main_window.isVisible() else T.OPEN
        toggle_action = menu.addAction(toggle_action_text)
        autostart_status = get_autostart_status()
        if autostart_status.supported:
            autostart_text = T.AUTOSTART_DISABLE if autostart_status.enabled else T.AUTOSTART_ENABLE
        else:
            autostart_text = T.AUTOSTART_UNAVAILABLE
        autostart_action = menu.addAction(autostart_text)
        autostart_action.setEnabled(autostart_status.supported)
        quit_action = menu.addAction(T.QUIT)
        selected_action = menu.exec(global_pos)
        if selected_action == toggle_action:
            self._toggle_main_window()
        elif selected_action == autostart_action:
            self._toggle_autostart(autostart_status.enabled)
        elif selected_action == quit_action:
            if hasattr(self.main_window, "allow_close"):
                self.main_window.allow_close()
            app = QApplication.instance()
            if app is not None:
                app.quit()

    def _toggle_autostart(self, currently_enabled: bool) -> None:
        if currently_enabled:
            answer = QMessageBox.question(
                self,
                T.AUTOSTART_DISABLE,
                T.AUTOSTART_DISABLE_QUESTION,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
            try:
                disable_autostart()
            except AutostartError as exc:
                QMessageBox.critical(self, T.AUTOSTART_TITLE, str(exc))
                return
            QMessageBox.information(self, T.AUTOSTART_TITLE, T.AUTOSTART_DISABLED)
            return

        target = get_default_autostart_target()
        if target is None:
            QMessageBox.warning(
                self,
                T.AUTOSTART_TITLE,
                T.AUTOSTART_BUILD_REQUIRED,
            )
            return

        answer = QMessageBox.question(
            self,
            T.AUTOSTART_ENABLE,
            T.AUTOSTART_ENABLE_QUESTION.format(target=target),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            enable_autostart(target)
        except AutostartError as exc:
            QMessageBox.critical(self, T.AUTOSTART_TITLE, str(exc))
            return
        QMessageBox.information(self, T.AUTOSTART_TITLE, T.AUTOSTART_ENABLED)

    def _restore_or_set_default_position(self) -> None:
        floating_icon = self.settings.floating_icon
        if floating_icon.has_position:
            self.move(self._bounded_position(QPoint(floating_icon.x or 0, floating_icon.y or 0)))
            return

        screen = QApplication.primaryScreen()
        if screen is None:
            self.move(40, 160)
            return

        available = screen.availableGeometry()
        x = available.right() - self.width() - 28
        y = available.center().y() - self.height() // 2
        self.move(self._bounded_position(QPoint(x, y)))

    def _save_position(self) -> None:
        self.settings.floating_icon.x = self.x()
        self.settings.floating_icon.y = self.y()
        try:
            self.settings_storage.save(self.settings)
        except OSError:
            pass

    def _bounded_position(self, position: QPoint, global_hint: QPoint | None = None) -> QPoint:
        screen = None
        if global_hint is not None:
            screen = QApplication.screenAt(global_hint)
        if screen is None:
            screen = QApplication.screenAt(position)
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is None:
            return position

        available = screen.availableGeometry()
        x, y = clamp_window_position(
            position.x(),
            position.y(),
            self.width(),
            self.height(),
            available.x(),
            available.y(),
            available.width(),
            available.height(),
            margin=self.SCREEN_MARGIN,
        )
        return QPoint(x, y)

    def _animate_opacity(self, target_opacity: float) -> None:
        if self._opacity_animation is not None:
            self._opacity_animation.stop()
        animation = QPropertyAnimation(self, b"windowOpacity", self)
        animation.setDuration(120)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(self.windowOpacity())
        animation.setEndValue(target_opacity)
        animation.start()
        self._opacity_animation = animation
