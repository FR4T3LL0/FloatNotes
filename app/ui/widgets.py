"""Small reusable UI helpers."""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


def apply_soft_shadow(
    widget: QWidget,
    *,
    blur_radius: int = 34,
    offset_y: int = 14,
    alpha: int = 34,
) -> None:
    """Apply a subtle card shadow to a widget."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setOffset(0, offset_y)
    shadow.setColor(QColor(31, 41, 51, alpha))
    widget.setGraphicsEffect(shadow)
