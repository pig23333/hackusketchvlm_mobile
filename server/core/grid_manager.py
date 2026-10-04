"""
Grid Manager - Handles dynamic grid sizing, adaptive cell dimensioning,
and image placement for sketch annotations.
"""

import math
from typing import Tuple, Dict, Optional
from PIL import Image, ImageOps
from .utils import create_grid_image


class GridManager:
    """Manages dynamic coordinate grid creation and image canvas placement."""

    def __init__(
        self,
        cell_size: int = 15,
        min_grid: int = 10,
        max_grid: int = 100,
        *,
        adaptive_grid: bool = False,
        target_cols: int = 50,
        target_rows: int = 50,
        min_cell_px: int = 15,
        max_cell_px: int = 60,
    ):
        self.cell_size = cell_size
        self.min_grid = min_grid
        self.max_grid = max_grid

        # Adaptive configuration for high-resolution images
        self.adaptive_grid = adaptive_grid
        self.target_cols = max(1, int(target_cols))
        self.target_rows = max(1, int(target_rows))
        self.min_cell_px = max(4, int(min_cell_px))
        self.max_cell_px = max(self.min_cell_px, int(max_cell_px))

        # Current state
        self.res_x = 50
        self.res_y = 50
        self.grid_size = (765, 765)
        self.grid_image = None
        self.positions = {}

    def update_grid_for_image(self, img: Image.Image, show_full_grid: bool = False) -> bool:
        """Recompute optimal grid dimensions for the given input image."""
        w, h = img.size
        old_state = (self.res_x, self.res_y, self.grid_size)
        self._recompute_grid(w, h, show_full_grid)
        return (self.res_x, self.res_y, self.grid_size) != old_state

    def _recompute_grid(self, w: int, h: int, show_full_grid: bool):
        """Derive cell size and row/col counts based on image aspect ratio."""
        if self.adaptive_grid:
            cs_w = math.ceil(w / self.target_cols)
            cs_h = math.ceil(h / self.target_rows)
            dyn_cell = max(cs_w, cs_h)
            dyn_cell = max(self.min_cell_px, min(self.max_cell_px, dyn_cell))
            self.cell_size = int(dyn_cell)

        self.res_x = max(self.min_grid, min(self.max_grid, math.ceil(w / self.cell_size)))
        self.res_y = max(self.min_grid, min(self.max_grid, math.ceil(h / self.cell_size)))

        # +1 cell for left label column, +1 cell for bottom label row
        self.grid_size = (
            self.res_x * self.cell_size + self.cell_size,
            self.res_y * self.cell_size + self.cell_size,
        )

        self.grid_image, self.positions = create_grid_image(
            res_x=self.res_x,
            res_y=self.res_y,
            cell_size=self.cell_size,
            header_size=self.cell_size,
            full=show_full_grid,
        )

    def place_image_on_canvas(self, img: Image.Image, bgcolor=(255, 255, 255)) -> Image.Image:
        """
        Paste image onto the canvas leaving room for the left ruler column
        and bottom ruler row.
        """
        canvas = Image.new("RGB", self.grid_size, bgcolor)
        # Shifted by cell_size from left; top-aligned
        canvas.paste(img.convert("RGB"), (self.cell_size, 0))
        return canvas

    def overlay_grid(self, img_rgb: Image.Image) -> Image.Image:
        """Overlay transparent lattice lines on top of canvas."""
        if self.grid_image is None:
            return img_rgb

        grid = self.grid_image.convert("RGBA")
        base = img_rgb.convert("RGBA")
        mask = grid.convert("L").point(lambda p: 255 if p < 200 else 0)
        base.paste(grid, (0, 0), mask)
        return base.convert("RGB")

    def create_annotated_image(
        self,
        img: Image.Image,
        show_full_grid: bool = False,
        bgcolor=(255, 255, 255)
    ) -> Image.Image:
        """Full pipeline: recompute grid, paste image, overlay lattice."""
        self.update_grid_for_image(img, show_full_grid)
        canvas = self.place_image_on_canvas(img, bgcolor)
        return self.overlay_grid(canvas)
