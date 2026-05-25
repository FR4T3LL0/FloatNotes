"""Create the FloatNotes ICO asset without external dependencies."""

from __future__ import annotations

import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "app" / "assets" / "floatnotes.ico"
SIZE = 64


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pixels = [_pixel(x, y) for y in range(SIZE) for x in range(SIZE)]
    dib = _bitmap_info_header() + _bgra_rows(pixels) + _and_mask()
    ico_header = struct.pack("<HHH", 0, 1, 1)
    directory = struct.pack("<BBBBHHII", SIZE, SIZE, 0, 0, 1, 32, len(dib), 22)
    OUTPUT.write_bytes(ico_header + directory + dib)
    print(OUTPUT)


def _bitmap_info_header() -> bytes:
    return struct.pack(
        "<IIIHHIIIIII",
        40,
        SIZE,
        SIZE * 2,
        1,
        32,
        0,
        SIZE * SIZE * 4,
        0,
        0,
        0,
        0,
    )


def _bgra_rows(pixels: list[tuple[int, int, int, int]]) -> bytes:
    rows: list[bytes] = []
    for y in range(SIZE - 1, -1, -1):
        row = bytearray()
        for x in range(SIZE):
            red, green, blue, alpha = pixels[y * SIZE + x]
            row.extend((blue, green, red, alpha))
        rows.append(bytes(row))
    return b"".join(rows)


def _and_mask() -> bytes:
    row_size = ((SIZE + 31) // 32) * 4
    return b"\x00" * row_size * SIZE


def _pixel(x: int, y: int) -> tuple[int, int, int, int]:
    alpha = _rounded_rect_alpha(x, y, 6, 6, 52, 52, 15)
    if alpha == 0:
        return 0, 0, 0, 0

    t = (x + y) / (SIZE * 2)
    red = int(250 - 18 * t)
    green = int(252 - 15 * t)
    blue = int(255 - 10 * t)

    note_alpha = _rounded_rect_alpha(x, y, 21, 17, 24, 31, 6)
    if note_alpha:
        blend = note_alpha / 255
        red = int(red * (1 - blend) + 37 * blend)
        green = int(green * (1 - blend) + 99 * blend)
        blue = int(blue * (1 - blend) + 235 * blend)

    if 27 <= y <= 29 and 26 <= x <= 40:
        red, green, blue = 31, 41, 51
    if 35 <= y <= 37 and 26 <= x <= 38:
        red, green, blue = 31, 41, 51
    if 43 <= y <= 45 and 26 <= x <= 35:
        red, green, blue = 31, 41, 51

    if (x - 44) ** 2 + (y - 19) ** 2 <= 16:
        red, green, blue = 37, 99, 235

    return red, green, blue, alpha


def _rounded_rect_alpha(x: int, y: int, left: int, top: int, width: int, height: int, radius: int) -> int:
    right = left + width - 1
    bottom = top + height - 1
    if x < left or x > right or y < top or y > bottom:
        return 0

    cx = min(max(x, left + radius), right - radius)
    cy = min(max(y, top + radius), bottom - radius)
    distance = math.hypot(x - cx, y - cy)
    if distance <= radius - 1:
        return 255
    if distance >= radius + 1:
        return 0
    return int((radius + 1 - distance) / 2 * 255)


if __name__ == "__main__":
    main()
