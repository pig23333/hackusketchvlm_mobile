"""
Grid generation, coordinate mapping, and vector utilities for SketchVLM.
"""

from typing import Optional, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont


def create_grid_image(
    res: int = 50,
    cell_size: int = 15,
    header_size: int = 15,
    *,
    line_w: int = 2,
    font_sz: Optional[int] = None,
    font_path: Optional[str] = None,
    full: bool = True,
    res_x: Optional[int] = None,
    res_y: Optional[int] = None
) -> Tuple[Image.Image, Dict[str, Tuple[int, int]]]:
    """
    Build a numbered grid image with axis rulers and cell coordinate map.

    Parameters:
        res: default number of cells per axis (for square grids)
        cell_size: pixel size of each grid square
        header_size: margin reserved for axis labels
        line_w: thickness of lattice lines
        font_sz: font size for axis numbers (defaults to 0.6 * cell_size)
        font_path: path to TTF font file
        full: if True draw full lattice grid; if False draw axis ticks only
        res_x: number of horizontal columns (overrides res if set)
        res_y: number of vertical rows (overrides res if set)

    Returns:
        (image, positions) where positions maps "xAyB" -> center pixel (cx, cy) on canvas
    """
    cols = res_x if res_x is not None else res
    rows = res_y if res_y is not None else res
    W = (cols + 1) * cell_size  # +1 for left header column
    H = (rows + 1) * cell_size  # +1 for bottom header row

    im = Image.new("RGB", (W, H), "white")
    drw = ImageDraw.Draw(im)

    if font_sz is None:
        font_sz = int(cell_size * 0.6)
    try:
        fnt = ImageFont.truetype(font_path or "arial.ttf", font_sz)
    except OSError:
        fnt = ImageFont.load_default()

    # 1. Axis labels along bottom (x: 1 to cols, left to right)
    for c in range(cols):
        label = str(c + 1)
        tw = drw.textlength(label, font=fnt)
        x = (c + 1) * cell_size + (cell_size - tw) / 2
        y = H - cell_size + (cell_size - font_sz) / 2
        drw.text((x, y), label, fill="black", font=fnt)

    # 2. Axis labels along left edge (y: 1 to rows, bottom to top)
    for r in range(rows):
        label = str(rows - r)
        tw = drw.textlength(label, font=fnt)
        tx = (cell_size - tw) / 2
        ty = r * cell_size + (cell_size - font_sz) / 2
        drw.text((tx, ty), label, fill="black", font=fnt)

    # 3. Draw grid lines
    if full:
        # Vertical grid lines
        for c in range(cols + 1):
            x = (c + 1) * cell_size
            drw.line([(x, 0), (x, H - cell_size)], fill="black", width=line_w)

        # Horizontal grid lines
        for r in range(rows + 1):
            y = r * cell_size
            drw.line([(cell_size, y), (W, y)], fill="black", width=line_w)
    else:
        # Compact style: main axes and edge tick marks
        drw.line([(cell_size, 0), (cell_size, H - cell_size)], fill="black", width=line_w)
        drw.line([(cell_size, H - cell_size), (W, H - cell_size)], fill="black", width=line_w)

        for r in range(rows):
            y0 = r * cell_size
            y1 = (r + 1) * cell_size
            drw.rectangle([(0, y0), (cell_size, y1)], outline="black")

        for c in range(cols):
            x0 = (c + 1) * cell_size
            x1 = (c + 2) * cell_size
            drw.rectangle([(x0, H - cell_size), (x1, H)], outline="black")

    # 4. Compute coordinate centers on canvas for each cell
    positions = {}
    for gx in range(1, cols + 1):
        for gy in range(1, rows + 1):
            cx = (gx + 0.5) * cell_size
            cy = (rows - gy + 0.5) * cell_size
            positions[f"x{gx}y{gy}"] = (int(cx), int(cy))

    return im, positions
