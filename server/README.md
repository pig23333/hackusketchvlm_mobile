# SketchVLM Mobile Video Processing Server

High-performance multimodal video annotation and object tracking backend powered by Vision-Language Models (VLM) and dense Lucas-Kanade optical flow. Designed specifically as the inference backend for the `hackusketchvlm_mobile` Android client.

---

## 1. System Architecture

```
 Mobile App (Android)                  SketchVLM Server (FastAPI)
┌───────────────────────┐             ┌────────────────────────────────────────────────────────┐
│ 1. Select Video Clip  │             │ 1. Keyframe Sampling & Probing                         │
│ 2. Set Prompt & FPS   │──HTTP POST──►    - Dynamic sample rate (0.5 ~ 2.0 FPS)               │
│ 3. Send /api/process  │             │    - Optional clip trimming (start_ms, end_ms)         │
└───────────────────────┘             └──────────────────────────┬─────────────────────────────┘
                                                                 │
                                                                 ▼
                                      ┌────────────────────────────────────────────────────────┐
                                      │ 2. Visual Cartesian Grid Canvas Overlay                │
                                      │    - Bottom-left origin (x1y1) standard                │
                                      │    - High-contrast coordinate lattice                  │
                                      └──────────────────────────┬─────────────────────────────┘
                                                                 │
                                                                 ▼
                                      ┌────────────────────────────────────────────────────────┐
                                      │ 3. Parallel VLM Spatial Reasoning                      │
                                      │    - Qwen 2.5-VL / Qwen 3.8 / GPT-4o                   │
                                      │    - Rate-limit backoff & keyframe error recovery      │
                                      │    - Direct native frame pixel mapping                 │
                                      └──────────────────────────┬─────────────────────────────┘
                                                                 │
                                                                 ▼
                                      ┌────────────────────────────────────────────────────────┐
                                      │ 4. Spatial Matching & Dense Optical Flow Tracking      │
                                      │    - Euclidean nearest-neighbor tracking               │
                                      │    - Lucas-Kanade flow + linear drift compensation     │
                                      │    - Sub-pixel locked tracking across all frames       │
                                      └──────────────────────────┬─────────────────────────────┘
                                                                 │
                                                                 ▼
┌───────────────────────┐             ┌────────────────────────────────────────────────────────┐
│ 4. Poll /status/{id}  │◄──HTTP GET──┤ 5. Vector Rendering & Video Assembly                   │
│ 5. Stream /result/{id}│             │    - Anti-aliased high-contrast marker badges          │
│ 6. Play & Save Video  │             │    - H.264 MP4 muxing with original audio              │
└───────────────────────┘             └────────────────────────────────────────────────────────┘
```

---

## 2. Key Features

- **Cartesian Coordinate Mapping**: Unified bottom-left origin ($x$ increasing left-to-right, $y$ increasing bottom-to-top) eliminating vertical offsets between VLM grid tokens and raw video pixels.
- **Dense Optical Flow Tracking**: Lucas-Kanade feature tracker (`cv2.calcOpticalFlowPyrLK`) follows non-linear movements (e.g., head tilts, rapid motion) with linear residual drift compensation at keyframe boundaries.
- **Spatial Identity Matching**: Minimum Euclidean distance association guarantees that tracked identities (e.g. left eye vs. right eye) do not swap or cross over intermediate frames.
- **Resilient Concurrency & Error Recovery**: Automatic exponential backoff retries on VLM rate limits (HTTP 429) and donor-keyframe recovery to prevent disappearing annotations.
- **Mobile-Optimized Output**: High-quality H.264 YUV420p video encoding compatible with Android MediaCodec and iOS AVFoundation, retaining the original audio track.

---

## 3. REST API Specification

### `POST /api/video/process`
Submit a video file for processing.

**Request format**: `multipart/form-data`
- `video` (file, required): Video file (`.mp4`, `.mov`, `.webm`).
- `prompt` (string, optional): Target description (e.g., `Cat eyes`, `Moving red ball`, `Pedestrians`).
- `model` (string, optional): Vision model ID (default: `qwen/qwen3.8-27b:free`).
- `sample_fps` (float, optional): Keyframe sampling rate (default: `1.0`).
- `start_ms` (float, optional): Sub-clip start offset in milliseconds.
- `end_ms` (float, optional): Sub-clip end offset in milliseconds.

**Response** (`202 Accepted`):
```json
{
  "ok": true,
  "job_id": "job_a1b2c3d4e5f6",
  "status": "queued",
  "poll_url": "/api/video/status/job_a1b2c3d4e5f6",
  "result_url": "/api/video/result/job_a1b2c3d4e5f6"
}
```

---

### `GET /api/video/status/{job_id}`
Query current job execution progress.

**Response** (`200 OK`):
```json
{
  "ok": true,
  "job_id": "job_a1b2c3d4e5f6",
  "status": "processing",
  "progress": 0.65,
  "message": "Dense optical flow tracking & motion compensation...",
  "error": null
}
```

Possible statuses: `queued`, `processing`, `completed`, `failed`.

---

### `GET /api/video/result/{job_id}`
Stream or download the final annotated H.264 MP4 video.

**Response**: `video/mp4` binary stream with `Content-Disposition: inline`.

---

### `GET /health`
Service health check and supported model discovery.

**Response** (`200 OK`):
```json
{
  "status": "healthy",
  "service": "SketchVLM Mobile Video Annotation Backend",
  "version": "2.0.0",
  "supported_models": [
    "qwen/qwen3.8-27b:free",
    "qwen/qwen2.5-vl-72b-instruct",
    "openai/gpt-4o",
    "anthropic/claude-3.5-sonnet"
  ]
}
```

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.10+
- FFmpeg (bundled automatically via `imageio-ffmpeg`)

### Installation

1. Navigate to the `server` directory:
   ```bash
   cd server
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Add your `OPENROUTER_API_KEY` (or `OPENAI_API_KEY`) in `.env`:
   ```ini
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
   ```

### Running the Server

Start the FastAPI application with Uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Once running:
- **Mobile REST API**: `http://<your-ip>:8000/api/video/process`
- **Interactive Web Dashboard**: `http://localhost:8000/`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
