"""
Stroke Parsing, Spatial Association, Optical Flow Tracking, and Frame Rendering for SketchVLM.
All comments and documentation are in English.
"""

import re
import math
from typing import List, Dict, Tuple, Optional
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def parse_stroke_tokens(
    stroke_xml: str,
    grid_mgr,
    frame_size: Optional[Tuple[int, int]] = None
) -> List[Dict]:
    """
    Parse SketchVLM XML stroke tags (<s1>...</s1>, <polyline>, <text>, <circle>, <rect>).
    Converts grid cell tokens (e.g. 'x10y20' or '10y20') directly into native video frame pixel coordinates.

    Coordinate system:
    - Origin at bottom-left: x1y1
    - Columns 1..res_x (left to right)
    - Rows 1..res_y (bottom to top)
    """
    strokes = []
    block_pattern = re.compile(r"<s\d+>(.*?)</s\d+>", re.DOTALL | re.IGNORECASE)
    blocks = block_pattern.findall(stroke_xml)
    if not blocks:
        blocks = [stroke_xml]

    cell_size = getattr(grid_mgr, "cell_size", 15)
    res_x = getattr(grid_mgr, "res_x", 50)
    res_y = getattr(grid_mgr, "res_y", 50)

    fw = frame_size[0] if frame_size else res_x * cell_size
    fh = frame_size[1] if frame_size else res_y * cell_size

    for idx, b in enumerate(blocks):
        stroke_item = {
            "id": f"s_{idx+1}",
            "type": "point",
            "color": "#007aff",
            "size": 2.0,
            "label": str(idx + 1),
            "points_px": [],
        }

        # Extract stroke ID if specified
        id_match = re.search(r"<id>(.*?)</id>", b, re.IGNORECASE)
        if id_match:
            stroke_item["id"] = id_match.group(1).strip()

        # Extract text / label
        text_match = re.search(r"<text\b([^>]*)>(.*?)</text>", b, re.DOTALL | re.IGNORECASE)
        if text_match:
            stroke_item["type"] = "text"
            stroke_item["label"] = text_match.group(2).strip().strip("'\"")
            attrs = text_match.group(1)
            col_m = re.search(r'color=["\']([^"\']+)["\']', attrs)
            if col_m:
                stroke_item["color"] = col_m.group(1)
            sz_m = re.search(r'size=["\']([^"\']+)["\']', attrs)
            if sz_m:
                try:
                    stroke_item["size"] = float(sz_m.group(1))
                except ValueError:
                    pass

        # Extract color from stroke / color attributes
        color_match = re.search(r'stroke=["\']([^"\']+)["\']|color=["\']([^"\']+)["\']', b)
        if color_match and not text_match:
            stroke_item["color"] = color_match.group(1) or color_match.group(2)

        # Match tokens like 'x12y34', '12y34', 'x12 y34'
        pt_matches = re.findall(r"(?:x|X)?(\d+)\s*(?:y|Y)\s*(\d+)", b)
        pts_px = []
        for col_str, row_str in pt_matches:
            col, row = int(col_str), int(row_str)
            # Map grid cell center to native frame pixel coordinates
            px = (col - 0.5) * cell_size
            py = (res_y - row + 0.5) * cell_size

            # Clamp to valid frame dimensions
            px = max(0.0, min(float(fw - 1), px))
            py = max(0.0, min(float(fh - 1), py))
            pts_px.append((round(px, 1), round(py, 1)))

        if pts_px:
            stroke_item["points_px"] = pts_px
            if len(pts_px) > 1 and stroke_item["type"] != "text":
                stroke_item["type"] = "polyline"
            strokes.append(stroke_item)

    return strokes


def spatial_match_strokes(
    strokes_a: List[Dict],
    strokes_b: List[Dict],
    max_dist: float = 160.0
) -> List[Tuple[Dict, Optional[Dict]]]:
    """
    Match strokes between keyframe A and keyframe B using minimal Euclidean distance.
    Guarantees spatial consistency across keyframes.
    """
    if not strokes_a:
        return []

    unmatched_b = list(strokes_b) if strokes_b else []
    matches = []

    for sa in strokes_a:
        if not sa.get("points_px"):
            continue
        ax, ay = sa["points_px"][0]

        best_idx = -1
        best_dist = float("inf")

        for idx, sb in enumerate(unmatched_b):
            if not sb.get("points_px"):
                continue
            bx, by = sb["points_px"][0]
            dist = math.hypot(ax - bx, ay - by)
            if dist < best_dist:
                best_dist = dist
                best_idx = idx

        if best_idx >= 0 and best_dist <= max_dist:
            matches.append((sa, unmatched_b.pop(best_idx)))
        else:
            matches.append((sa, None))

    return matches


def interpolate_strokes(
    strokes_a: List[Dict],
    strokes_b: List[Dict],
    alpha: float
) -> List[Dict]:
    """
    Spatial-nearest-neighbor linear interpolation between two keyframes.
    alpha: 0.0 (exact frame A) to 1.0 (exact frame B).
    """
    alpha = max(0.0, min(1.0, alpha))
    if alpha <= 0.0:
        return strokes_a
    if alpha >= 1.0 and strokes_b:
        return strokes_b

    matches = spatial_match_strokes(strokes_a, strokes_b)
    interpolated = []

    for sa, sb in matches:
        if sb and len(sa["points_px"]) == len(sb["points_px"]):
            new_pts = []
            for (ax, ay), (bx, by) in zip(sa["points_px"], sb["points_px"]):
                ix = ax + (bx - ax) * alpha
                iy = ay + (by - ay) * alpha
                new_pts.append((round(ix, 1), round(iy, 1)))

            inter_item = dict(sa)
            inter_item["points_px"] = new_pts
            interpolated.append(inter_item)
        else:
            interpolated.append(sa)

    return interpolated


def track_dense_frames_with_flow(
    all_raw_bgr_frames: List[np.ndarray],
    keyframe_indices: List[int],
    keyframe_strokes: List[List[Dict]]
) -> List[List[Dict]]:
    """
    Dense temporal tracking across all video frames using:
    1. Keyframe VLM anchors.
    2. Lucas-Kanade optical flow forward tracking.
    3. Residual drift compensation blending to next keyframe.
    """
    total_frames = len(all_raw_bgr_frames)
    dense_strokes = [[] for _ in range(total_frames)]
    if not keyframe_indices or not keyframe_strokes:
        return dense_strokes

    fh, fw = all_raw_bgr_frames[0].shape[:2]
    lk_params = dict(
        winSize=(21, 21),
        maxLevel=3,
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01)
    )

    # Process segment by segment
    for seg_idx in range(len(keyframe_indices) - 1):
        start_f = keyframe_indices[seg_idx]
        end_f = keyframe_indices[seg_idx + 1]
        strokes_a = keyframe_strokes[seg_idx]
        strokes_b = keyframe_strokes[seg_idx + 1]

        # Propagate from neighbor if one keyframe failed
        if not strokes_a and strokes_b:
            strokes_a = strokes_b
        if not strokes_b and strokes_a:
            strokes_b = strokes_a

        if not strokes_a and not strokes_b:
            continue

        matches = spatial_match_strokes(strokes_a, strokes_b)

        tracked_pts = {}
        target_pts = {}
        stroke_meta = {}

        for sa, sb in matches:
            sid = sa["id"]
            if sa.get("points_px"):
                p_start = sa["points_px"][0]
                tracked_pts[sid] = np.array([[p_start[0], p_start[1]]], dtype=np.float32)
                stroke_meta[sid] = dict(sa)
                if sb and sb.get("points_px"):
                    target_pts[sid] = np.array([sb["points_px"][0][0], sb["points_px"][0][1]], dtype=np.float32)
                else:
                    target_pts[sid] = np.array([p_start[0], p_start[1]], dtype=np.float32)

        prev_gray = cv2.cvtColor(all_raw_bgr_frames[start_f], cv2.COLOR_BGR2GRAY)
        flow_trajectories = {sid: [tracked_pts[sid][0].copy()] for sid in tracked_pts}

        for f_idx in range(start_f + 1, end_f + 1):
            curr_gray = cv2.cvtColor(all_raw_bgr_frames[f_idx], cv2.COLOR_BGR2GRAY)
            for sid in tracked_pts:
                p0 = tracked_pts[sid].reshape(-1, 1, 2)
                p1, st, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, p0, None, **lk_params)
                if st[0][0] == 1:
                    tracked_pts[sid] = p1[0]
                flow_trajectories[sid].append(tracked_pts[sid][0].copy())
            prev_gray = curr_gray

        seg_len = end_f - start_f
        for step, f_idx in enumerate(range(start_f, end_f)):
            alpha = step / float(seg_len) if seg_len > 0 else 0.0
            frame_s = []
            for sid in tracked_pts:
                flow_pt = flow_trajectories[sid][step]
                final_flow = flow_trajectories[sid][-1]
                targ = target_pts[sid]

                # Linear residual drift compensation
                drift_correction = (targ - final_flow) * alpha
                corr_x = float(flow_pt[0] + drift_correction[0])
                corr_y = float(flow_pt[1] + drift_correction[1])

                corr_x = max(0.0, min(float(fw - 1), corr_x))
                corr_y = max(0.0, min(float(fh - 1), corr_y))

                s_item = dict(stroke_meta[sid])
                s_item["points_px"] = [(round(corr_x, 1), round(corr_y, 1))]
                frame_s.append(s_item)

            dense_strokes[f_idx] = frame_s

    # Propagate last keyframe to video end
    last_kf = keyframe_indices[-1]
    dense_strokes[last_kf] = keyframe_strokes[-1]
    for f_idx in range(last_kf + 1, total_frames):
        dense_strokes[f_idx] = keyframe_strokes[-1]

    return dense_strokes


def render_strokes_on_frame(
    frame: Image.Image,
    strokes: List[Dict],
    canvas_size: Optional[Tuple[int, int]] = None
) -> Image.Image:
    """
    High-performance vector rendering of strokes directly onto the video frame.
    Coordinates in strokes are native frame pixel coordinates.
    """
    img = frame.copy().convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    fw, fh = img.size
    scale_w = 1.0
    scale_h = 1.0
    if canvas_size and canvas_size != (fw, fh):
        scale_w = fw / float(canvas_size[0])
        scale_h = fh / float(canvas_size[1])

    try:
        font = ImageFont.truetype("arial.ttf", size=max(12, int(15 * (fh / 300.0))))
    except OSError:
        font = ImageFont.load_default()

    for stroke in strokes:
        pts = [(x * scale_w, y * scale_h) for x, y in stroke.get("points_px", [])]
        color = stroke.get("color", "#007aff")
        label = stroke.get("label")
        stype = stroke.get("type", "point")

        if not pts:
            continue

        if stype == "polyline" and len(pts) >= 2:
            draw.line(pts, fill=color, width=max(2, int(3 * (fh / 300.0))))
            for pt in pts:
                r = max(3, int(5 * (fh / 300.0)))
                draw.ellipse([(pt[0]-r, pt[1]-r), (pt[0]+r, pt[1]+r)], fill="#ffffff", outline=color, width=2)
        else:
            # Draw point / target marker
            for pt in pts:
                r = max(4, int(7 * (fh / 300.0)))
                # Outer halo ring
                draw.ellipse([(pt[0]-r-1, pt[1]-r-1), (pt[0]+r+1, pt[1]+r+1)], outline="#ffffff", width=2)
                # Inner filled disc
                draw.ellipse([(pt[0]-r, pt[1]-r), (pt[0]+r, pt[1]+r)], fill=color)

        # Draw label badge if present
        if label and pts:
            anchor = pts[0]
            tx = anchor[0] + max(8, int(10 * (fw / 300.0)))
            ty = anchor[1] - max(8, int(10 * (fh / 300.0)))
            bbox = font.getbbox(label)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]

            pad_x = 4
            pad_y = 2
            # Dark contrast pill badge
            draw.rounded_rectangle(
                [(tx - pad_x, ty - pad_y), (tx + tw + pad_x, ty + th + pad_y)],
                radius=3,
                fill=(10, 15, 25, 220),
                outline=color,
                width=1
            )
            draw.text((tx, ty), label, fill="#ffffff", font=font)

    result = Image.alpha_composite(img, overlay)
    return result.convert("RGB")
