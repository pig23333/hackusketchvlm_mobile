"""
Unit test for coordinate conversion, spatial matching, and stroke parsing.
All comments and documentation are in English.
"""

import sys
import os
import unittest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.grid_manager import GridManager
from core.stroke_tracker import parse_stroke_tokens, spatial_match_strokes, interpolate_strokes


class TestCoordinateMapping(unittest.TestCase):
    def setUp(self):
        self.img = Image.new("RGB", (288, 308), (255, 255, 255))
        self.gm = GridManager(cell_size=15, adaptive_grid=True, target_cols=50, target_rows=50)
        self.gm.update_grid_for_image(self.img, False)

    def test_grid_dimensions(self):
        """Verify grid dimension calculation for (288, 308) frame."""
        self.assertEqual(self.gm.cell_size, 15)
        self.assertEqual(self.gm.res_x, 20)
        self.assertEqual(self.gm.res_y, 21)

    def test_token_parsing_native_coordinates(self):
        """Verify bottom-left Cartesian mapping to native pixel bounds."""
        xml = """
        <answer>
        <strokes>
          <s1><points>'x4y18'</points><id>left_eye</id></s1>
          <s2><points>'17y19'</points><id>right_eye</id></s2>
        </strokes>
        </answer>
        """
        strokes = parse_stroke_tokens(xml, self.gm, frame_size=(288, 308))
        self.assertEqual(len(strokes), 2)

        # x4 -> (4 - 0.5) * 15 = 52.5
        # y18 -> (21 - 18 + 0.5) * 15 = 52.5
        pt1 = strokes[0]["points_px"][0]
        self.assertAlmostEqual(pt1[0], 52.5, places=1)
        self.assertAlmostEqual(pt1[1], 52.5, places=1)

        # x17 -> (17 - 0.5) * 15 = 247.5
        # y19 -> (21 - 19 + 0.5) * 15 = 37.5
        pt2 = strokes[1]["points_px"][0]
        self.assertAlmostEqual(pt2[0], 247.5, places=1)
        self.assertAlmostEqual(pt2[1], 37.5, places=1)

    def test_spatial_matching(self):
        """Verify spatial Euclidean association avoids identity swapping."""
        strokes_a = [
            {"id": "eye_l", "points_px": [(50.0, 50.0)]},
            {"id": "eye_r", "points_px": [(250.0, 50.0)]},
        ]
        # Swapped IDs in frame B
        strokes_b = [
            {"id": "eye_l", "points_px": [(248.0, 52.0)]},
            {"id": "eye_r", "points_px": [(52.0, 51.0)]},
        ]

        matches = spatial_match_strokes(strokes_a, strokes_b, max_dist=100.0)
        self.assertEqual(len(matches), 2)

        # First stroke (50, 50) must match spatially with (52, 51), NOT (248, 52)
        match_a0 = matches[0]
        self.assertEqual(match_a0[0]["points_px"][0], (50.0, 50.0))
        self.assertEqual(match_a0[1]["points_px"][0], (52.0, 51.0))


if __name__ == "__main__":
    unittest.main()
