"""
Video Sketch Engine for SketchVLM.
Orchestrates parallel VLM inference on keyframes with bottom-left grid orientation,
spatial nearest-neighbor stroke matching, Lucas-Kanade optical flow tracking,
and high-speed reassembly into an annotated H.264 video.
All comments and documentation are in English.
"""

import os
import time
import base64
import io
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Optional, Callable
import cv2
import numpy as np
from PIL import Image

from .grid_manager import GridManager
from .llm_adapters import make_adapter
from .prompts import build_tracking_system_prompt, build_tracking_user_prompt
from .video_utils import extract_video_frames, assemble_video_from_frames, probe_video
from .stroke_tracker import (
    parse_stroke_tokens,
    interpolate_strokes,
    track_dense_frames_with_flow,
    render_strokes_on_frame
)


class VideoSketchEngine:
    """
    High-performance video inference engine for mobile clients.
    Converts incoming video into sampled keyframes, performs VLM reasoning,
    tracks features smoothly via optical flow, and reassembles annotated video.
    """

    def __init__(
        self,
        llm_provider: str = "openrouter",
        model: str = "qwen/qwen3.8-27b:free",
        max_workers: int = 2
    ):
        self.llm_provider = llm_provider
        self.model = model
        self.max_workers = max(1, min(4, max_workers))

    def _create_canvas_with_grid(self, img: Image.Image, grid_mgr: GridManager) -> Tuple[Image.Image, str]:
        """Create grid-overlaid canvas image and return base64 string."""
        canvas = grid_mgr.create_annotated_image(img, show_full_grid=False, bgcolor=(255, 255, 255))
        buf = io.BytesIO()
        canvas.save(buf, format="PNG")
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        return canvas, b64

    def _infer_single_keyframe(
        self,
        keyframe_idx: int,
        keyframe: Image.Image,
        prompt: str,
        max_retries: int = 3
    ) -> Dict:
        """Process one keyframe with SketchVLM coordinate grid and query VLM with retry logic."""
        gm = GridManager(cell_size=15, adaptive_grid=True, target_cols=50, target_rows=50)
        gm.update_grid_for_image(keyframe, False)

        canvas, canvas_b64 = self._create_canvas_with_grid(keyframe, gm)
        system_msg = build_tracking_system_prompt(gm.res_x, gm.res_y)
        user_msg = build_tracking_user_prompt(prompt)

        content = [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": canvas_b64}},
            {"type": "text", "text": user_msg}
        ]
        messages = [{"role": "user", "content": content}]

        adapter = make_adapter(self.llm_provider, self.model, cache=False, max_tokens=1024)
        last_err = None

        for attempt in range(max_retries):
            try:
                raw_resp = adapter.call(system_msg, messages, {})
                text_out = adapter.extract_text(raw_resp)
                # Parse tokens directly into native keyframe pixel coordinates
                strokes = parse_stroke_tokens(text_out, gm, frame_size=keyframe.size)
                return {
                    "keyframe_idx": keyframe_idx,
                    "strokes": strokes,
                    "raw_text": text_out,
                    "grid_size": gm.grid_size
                }
            except Exception as e:
                last_err = e
                if attempt < max_retries - 1:
                    time.sleep(2.0 * (attempt + 1))

        raise RuntimeError(f"Keyframe {keyframe_idx} failed after {max_retries} retries: {last_err}")

    def process_video(
        self,
        video_path: str,
        prompt: str,
        output_path: str,
        sample_fps: float = 1.0,
        start_ms: Optional[float] = None,
        end_ms: Optional[float] = None,
        use_optical_flow: bool = True,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict:
        """
        Full video processing pipeline:
        1. Extract sampled keyframes and metadata.
        2. Execute parallel VLM queries with retry & recovery.
        3. Perform dense Lucas-Kanade optical flow tracking with drift compensation.
        4. Render vector annotations onto dense frames.
        5. Reassemble H.264 video with original audio.
        """
        t_start = time.time()
        if progress_callback:
            progress_callback(0.05, "Extracting video frames and probing metadata...")

        # 1. Extract keyframes
        keyframes, keyframe_indices, timestamps, meta = extract_video_frames(
            video_path,
            target_sample_fps=sample_fps,
            start_ms=start_ms,
            end_ms=end_ms
        )
        total_keyframes = len(keyframes)
        if total_keyframes == 0:
            raise ValueError("No frames extracted from video.")

        fw, fh = meta["width"], meta["height"]

        if progress_callback:
            progress_callback(
                0.15,
                f"Extracted {total_keyframes} keyframes ({sample_fps} FPS). Querying VLM..."
            )

        # 2. VLM inference on all keyframes
        keyframe_results = [None] * total_keyframes
        completed_count = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_idx = {
                executor.submit(
                    self._infer_single_keyframe, idx, kf, prompt
                ): idx
                for idx, kf in enumerate(keyframes)
            }

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    res = future.result()
                    keyframe_results[idx] = res
                except Exception as e:
                    print(f"Keyframe {idx} failed: {e}")
                    keyframe_results[idx] = None

                completed_count += 1
                if progress_callback:
                    pct = 0.15 + 0.45 * (completed_count / total_keyframes)
                    progress_callback(pct, f"VLM processed keyframe {completed_count}/{total_keyframes}")

        # Recover missing keyframes from adjacent neighbors
        for idx in range(total_keyframes):
            if keyframe_results[idx] is None or not keyframe_results[idx]["strokes"]:
                prev_valid = None
                for p in range(idx - 1, -1, -1):
                    if keyframe_results[p] and keyframe_results[p]["strokes"]:
                        prev_valid = keyframe_results[p]
                        break
                next_valid = None
                if not prev_valid:
                    for n in range(idx + 1, total_keyframes):
                        if keyframe_results[n] and keyframe_results[n]["strokes"]:
                            next_valid = keyframe_results[n]
                            break
                donor = prev_valid or next_valid
                if donor:
                    keyframe_results[idx] = {
                        "keyframe_idx": idx,
                        "strokes": list(donor["strokes"]),
                        "raw_text": donor.get("raw_text", ""),
                        "grid_size": donor.get("grid_size", (fw, fh))
                    }
                else:
                    keyframe_results[idx] = {
                        "keyframe_idx": idx,
                        "strokes": [],
                        "raw_text": "",
                        "grid_size": (fw, fh)
                    }

        if progress_callback:
            progress_callback(0.65, "Dense optical flow tracking & motion compensation...")

        # 3. Read raw dense video frames
        cap = cv2.VideoCapture(video_path)
        start_frame = meta.get("clipped_start_frame", 0)
        end_frame = meta.get("clipped_end_frame", meta["total_frames"])
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        all_raw_bgr_frames = []
        cur_f = start_frame
        while cur_f < end_frame:
            ret, frame_bgr = cap.read()
            if not ret:
                break
            all_raw_bgr_frames.append(frame_bgr)
            cur_f += 1
        cap.release()

        total_frames = len(all_raw_bgr_frames)
        keyframe_strokes_list = [res["strokes"] for res in keyframe_results]

        # 4. Dense tracking across all frames
        if use_optical_flow and total_frames > 0:
            dense_strokes = track_dense_frames_with_flow(
                all_raw_bgr_frames,
                keyframe_indices,
                keyframe_strokes_list
            )
        else:
            dense_strokes = [[] for _ in range(total_frames)]
            for f_idx in range(total_frames):
                left_k_idx = 0
                right_k_idx = 0
                for i, k_idx in enumerate(keyframe_indices):
                    if k_idx <= f_idx:
                        left_k_idx = i
                    if k_idx >= f_idx:
                        right_k_idx = i
                        break
                left_f = keyframe_indices[left_k_idx]
                right_f = keyframe_indices[right_k_idx]
                alpha = 0.0 if right_f == left_f else (f_idx - left_f) / float(right_f - left_f)
                dense_strokes[f_idx] = interpolate_strokes(
                    keyframe_results[left_k_idx]["strokes"],
                    keyframe_results[right_k_idx]["strokes"],
                    alpha
                )

        if progress_callback:
            progress_callback(0.80, "Rendering vector annotations onto frames...")

        # 5. Render frames
        rendered_pil_frames: List[Image.Image] = []
        for f_idx, raw_bgr in enumerate(all_raw_bgr_frames):
            frame_rgb = cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2RGB)
            pil_frame = Image.fromarray(frame_rgb)
            rendered = render_strokes_on_frame(
                pil_frame,
                dense_strokes[f_idx],
                canvas_size=None
            )
            rendered_pil_frames.append(rendered)

        if progress_callback:
            progress_callback(0.88, "Encoding H.264 video with audio muxing...")

        # 6. Reassemble video
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        final_video_path = assemble_video_from_frames(
            rendered_pil_frames,
            output_path,
            fps=meta["fps"],
            original_video_path=video_path
        )

        elapsed = time.time() - t_start
        if progress_callback:
            progress_callback(1.0, f"Completed in {elapsed:.1f}s")

        return {
            "status": "success",
            "output_path": final_video_path,
            "duration_seconds": elapsed,
            "total_frames_processed": len(rendered_pil_frames),
            "keyframes_queried": total_keyframes,
            "fps": meta["fps"]
        }
