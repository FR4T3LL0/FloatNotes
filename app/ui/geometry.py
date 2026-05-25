"""Geometry helpers for desktop UI windows."""

from __future__ import annotations


def clamp_window_position(
    x: int,
    y: int,
    window_width: int,
    window_height: int,
    available_x: int,
    available_y: int,
    available_width: int,
    available_height: int,
    *,
    margin: int = 10,
) -> tuple[int, int]:
    """Clamp a window position so the whole window remains visible."""
    safe_margin = max(0, margin)
    min_x = available_x + safe_margin
    min_y = available_y + safe_margin
    max_x = available_x + available_width - window_width - safe_margin
    max_y = available_y + available_height - window_height - safe_margin

    if max_x < min_x:
        min_x = available_x
        max_x = available_x
    if max_y < min_y:
        min_y = available_y
        max_y = available_y

    return (
        min(max(x, min_x), max_x),
        min(max(y, min_y), max_y),
    )
