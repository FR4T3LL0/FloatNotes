import unittest

from app.ui.geometry import clamp_window_position


class GeometryTests(unittest.TestCase):
    def test_clamps_position_inside_available_bounds(self) -> None:
        self.assertEqual(
            (10, 10),
            clamp_window_position(-100, -80, 62, 62, 0, 0, 1920, 1080, margin=10),
        )

    def test_clamps_against_right_and_bottom_edges(self) -> None:
        self.assertEqual(
            (1848, 1008),
            clamp_window_position(3000, 2000, 62, 62, 0, 0, 1920, 1080, margin=10),
        )

    def test_respects_offset_screen_geometry(self) -> None:
        self.assertEqual(
            (-1270, 710),
            clamp_window_position(-4000, 2000, 80, 80, -1280, 0, 1280, 800, margin=10),
        )

    def test_handles_tiny_available_area(self) -> None:
        self.assertEqual(
            (0, 0),
            clamp_window_position(100, 100, 80, 80, 0, 0, 40, 40, margin=10),
        )


if __name__ == "__main__":
    unittest.main()
