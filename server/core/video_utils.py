"""
Video Processing Utilities for SketchVLM.
Handles frame extraction, video metadata probing, sub-clip trimming,
and H.264 video encoding with audio track preservation.
All comments and documentation are in English.
"""

import os
import subprocess
import cv2
from PIL import Image
from typing import List, Tuple, Dict, Optional
import imageio_ffmpeg


def get_ffmpeg_exe() -> str:
    """Return absolute path to bundled static ffmpeg binary."""
    return imageio_ffmpeg.get_ffmpeg_exe()


def probe_video(video_path: str) -> Dict:
    """
    Extract video metadata: fps, total frame count, resolution, and duration.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file at: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0.0
    cap.release()

    return {
        "fps": fps,
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "duration": duration,
    }


def extract_video_frames(
    video_path: str,
    target_sample_fps: float = 1.0,
    max_duration: float = 60.0,
    start_ms: Optional[float] = None,
    end_ms: Optional[float] = None
) -> Tuple[List[Image.Image], List[int], List[float], Dict]:
    """
    Extract sampled keyframes and metadata from video.

    Parameters:
        video_path: path to input video
        target_sample_fps: frequency of sampled keyframes sent to VLM
        max_duration: maximum video duration to process in seconds
        start_ms: optional clip start offset in milliseconds
        end_ms: optional clip end offset in milliseconds

    Returns:
        keyframes: list of PIL Images (RGB)
        frame_indices: list of frame index integers relative to the clip
        timestamps: list of timestamp seconds
        meta: probed metadata dictionary
    """
    meta = probe_video(video_path)
    native_fps = meta["fps"]
    total_frames = meta["total_frames"]

    # Calculate frame range based on start_ms and end_ms
    start_frame = 0
    end_frame = total_frames
    if start_ms is not None and start_ms >= 0:
        start_frame = min(total_frames, int(round((start_ms / 1000.0) * native_fps)))
    if end_ms is not None and end_ms > 0:
        end_frame = min(total_frames, int(round((end_ms / 1000.0) * native_fps)))
    if end_frame <= start_frame:
        end_frame = total_frames

    frame_interval = max(1, int(round(native_fps / target_sample_fps)))

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    keyframes = []
    frame_indices = []
    timestamps = []

    current_idx = start_frame
    while current_idx < end_frame:
        ret, frame_bgr = cap.read()
        if not ret:
            break

        rel_idx = current_idx - start_frame
        timestamp = rel_idx / native_fps
        if timestamp > max_duration:
            break

        if rel_idx % frame_interval == 0:
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            keyframes.append(Image.fromarray(frame_rgb))
            frame_indices.append(rel_idx)
            timestamps.append(timestamp)

        current_idx += 1

    cap.release()
    meta["clipped_start_frame"] = start_frame
    meta["clipped_end_frame"] = current_idx
    meta["clipped_total_frames"] = current_idx - start_frame
    return keyframes, frame_indices, timestamps, meta


def assemble_video_from_frames(
    frames: List[Image.Image],
    output_path: str,
    fps: float,
    original_video_path: Optional[str] = None
) -> str:
    """
    Assemble a sequence of PIL Images into an H.264 MP4 video.
    Copies original audio track if available.
    """
    if not frames:
        raise ValueError("Frames list is empty")

    w, h = frames[0].size
    ffmpeg_exe = get_ffmpeg_exe()

    temp_video = output_path + ".temp.mp4"
    if os.path.exists(temp_video):
        os.remove(temp_video)
    if os.path.exists(output_path):
        os.remove(output_path)

    # Encode raw frames via ffmpeg pipe (yuv420p for mobile hardware decoding)
    cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{w}x{h}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "22",
        temp_video
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for frame in frames:
        if frame.size != (w, h):
            frame = frame.resize((w, h), Image.Resampling.LANCZOS)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()

    # Mux original audio if present
    if original_video_path and os.path.exists(original_video_path):
        mux_cmd = [
            ffmpeg_exe,
            "-y",
            "-i", temp_video,
            "-i", original_video_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0?",
            "-shortest",
            output_path
        ]
        res = subprocess.run(mux_cmd, capture_output=True)
        if os.path.exists(temp_video):
            os.remove(temp_video)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path

    if os.path.exists(temp_video):
        os.rename(temp_video, output_path)
    return output_path
