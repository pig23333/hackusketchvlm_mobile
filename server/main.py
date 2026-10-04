"""
SketchVLM Video REST API Server for Mobile Backend.
Provides RESTful endpoints for video submission, asynchronous job processing,
real-time status polling, video streaming, and an interactive English Web Dashboard.
All comments and documentation are in English.
"""

import os
import sys
import uuid
import threading
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load local environment variables
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SERVER_DIR, ".env"))

# Import core video engine
from core.video_engine import VideoSketchEngine

app = FastAPI(
    title="SketchVLM Mobile Backend",
    description="High-performance VLM video tracking and annotation service for mobile apps",
    version="2.0.0"
)

# Enable CORS for mobile and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(SERVER_DIR, "uploads")
OUTPUT_DIR = os.path.join(SERVER_DIR, "results")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory job repository
JOBS: Dict[str, Dict[str, Any]] = {}


def _run_video_job(
    job_id: str,
    video_path: str,
    prompt: str,
    model: str,
    sample_fps: float,
    start_ms: Optional[float],
    end_ms: Optional[float]
):
    """Background worker for video annotation pipeline."""
    out_path = os.path.join(OUTPUT_DIR, f"{job_id}_annotated.mp4")

    def on_progress(pct: float, msg: str):
        if job_id in JOBS:
            JOBS[job_id]["progress"] = round(pct, 2)
            JOBS[job_id]["message"] = msg

    try:
        engine = VideoSketchEngine(
            llm_provider="openrouter",
            model=model,
            max_workers=2
        )
        JOBS[job_id]["status"] = "processing"
        result = engine.process_video(
            video_path=video_path,
            prompt=prompt,
            output_path=out_path,
            sample_fps=sample_fps,
            start_ms=start_ms,
            end_ms=end_ms,
            use_optical_flow=True,
            progress_callback=on_progress
        )
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["progress"] = 1.0
        JOBS[job_id]["message"] = "Processing completed."
        JOBS[job_id]["result_video_path"] = out_path
        JOBS[job_id]["meta"] = result
    except Exception as e:
        import traceback
        traceback.print_exc()
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        JOBS[job_id]["message"] = f"Failed: {e}"


@app.get("/health")
def health():
    """Service health and capability check."""
    return {
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


@app.post("/api/video/process")
async def process_video(
    video: UploadFile = File(...),
    prompt: str = Form("Label and track salient targets"),
    model: str = Form("qwen/qwen3.8-27b:free"),
    sample_fps: float = Form(1.0),
    start_ms: Optional[float] = Form(None),
    end_ms: Optional[float] = Form(None),
):
    """
    Submit a video for annotation.
    Accepts multipart/form-data:
      - video: Video file (.mp4, .mov, .webm)
      - prompt: Instruction describing targets to track
      - model: Target VLM model ID
      - sample_fps: Keyframe sampling rate (default: 1.0)
      - start_ms: Optional clip start timestamp in milliseconds
      - end_ms: Optional clip end timestamp in milliseconds
    """
    if not video.filename:
        raise HTTPException(status_code=400, detail="Empty filename provided")

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    filename = f"{job_id}_{video.filename}"
    save_path = os.path.join(UPLOAD_DIR, filename)

    contents = await video.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    JOBS[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0.0,
        "message": "Job queued for processing",
        "prompt": prompt,
        "model": model,
        "sample_fps": sample_fps,
        "result_video_path": None,
        "error": None
    }

    thread = threading.Thread(
        target=_run_video_job,
        args=(job_id, save_path, prompt, model, sample_fps, start_ms, end_ms),
        daemon=True
    )
    thread.start()

    return JSONResponse(
        status_code=202,
        content={
            "ok": True,
            "job_id": job_id,
            "status": "queued",
            "poll_url": f"/api/video/status/{job_id}",
            "result_url": f"/api/video/result/{job_id}"
        }
    )


@app.get("/api/video/status/{job_id}")
def get_status(job_id: str):
    """Query current status and progress of a video job."""
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "ok": True,
        "job_id": job["job_id"],
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "error": job["error"]
    }


@app.get("/api/video/result/{job_id}")
def get_result(job_id: str):
    """Download or stream the annotated output video."""
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed" or not job["result_video_path"]:
        raise HTTPException(status_code=400, detail="Video processing has not completed yet")

    out_file = job["result_video_path"]
    if not os.path.exists(out_file):
        raise HTTPException(status_code=500, detail="Rendered video file was not found")

    return FileResponse(
        out_file,
        media_type="video/mp4",
        filename=f"sketchvlm_{job_id}.mp4"
    )


# ==============================================================================
# Interactive Web Dashboard for Debugging & Verification
# ==============================================================================
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SketchVLM Video AI Service Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --card: #121927;
      --border: #1f2c42;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --success: #10b981;
      --warning: #f59e0b;
      --text: #f3f4f6;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', -apple-system, sans-serif;
      padding: 32px 20px;
      line-height: 1.5;
    }
    .container { max-width: 1080px; margin: 0 auto; }
    header { margin-bottom: 28px; }
    h1 { font-size: 26px; font-weight: 700; margin-bottom: 8px; }
    .badge {
      display: inline-block;
      padding: 3px 8px;
      font-size: 12px;
      border-radius: 6px;
      background: rgba(59, 130, 246, 0.15);
      color: var(--primary);
      border: 1px solid rgba(59, 130, 246, 0.3);
      font-family: 'JetBrains Mono', monospace;
      margin-left: 8px;
    }
    p.sub { color: var(--text-muted); font-size: 14px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
    }
    .card h2 { font-size: 18px; margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
    .form-group { margin-bottom: 16px; }
    label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-muted); }
    input[type="text"], select {
      width: 100%;
      background: #0d1320;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: #fff;
      padding: 10px 14px;
      font-size: 14px;
      outline: none;
    }
    input[type="text"]:focus, select:focus { border-color: var(--primary); }
    .file-dropzone {
      border: 2px dashed var(--border);
      border-radius: 10px;
      padding: 24px;
      text-align: center;
      cursor: pointer;
      background: #0d1320;
      transition: all 0.2s ease;
    }
    .file-dropzone:hover { border-color: var(--primary); background: rgba(59, 130, 246, 0.05); }
    .file-dropzone input { display: none; }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 12px 20px;
      background: var(--primary);
      color: white;
      font-weight: 600;
      font-size: 14px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      width: 100%;
      transition: background 0.15s ease;
    }
    .btn:hover { background: var(--primary-hover); }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .progress-bar {
      height: 8px;
      background: #1b263b;
      border-radius: 4px;
      overflow: hidden;
      margin: 16px 0;
      display: none;
    }
    .progress-fill { height: 100%; width: 0%; background: var(--primary); transition: width 0.3s ease; }
    .status-msg { font-size: 13px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; min-height: 20px; }
    video { width: 100%; border-radius: 8px; background: #000; margin-top: 12px; }
  </style>
</head>
<body>
<div class="container">
  <header>
    <h1>SketchVLM Video AI Service <span class="badge">v2.0 Mobile REST Backend</span></h1>
    <p class="sub">Multimodal Video Tracking & Spatial Motion Compensation Engine</p>
  </header>

  <div class="grid">
    <div class="card">
      <h2>1. Input Parameters</h2>
      <div class="form-group">
        <label>Video File (.mp4, .mov)</label>
        <div class="file-dropzone" onclick="document.getElementById('videoFile').click()">
          <span id="fileLabel">Click to select or drop video file</span>
          <input type="file" id="videoFile" accept="video/mp4,video/quicktime">
        </div>
      </div>

      <div class="form-group">
        <label>Tracking Prompt</label>
        <input type="text" id="promptInput" value="Cat eyes" placeholder="e.g. Cat eyes, moving vehicles, sports ball">
      </div>

      <div class="form-group" style="display: grid; grid-template-columns: 2fr 1fr; gap: 12px;">
        <div>
          <label>Vision Model (VLM)</label>
          <select id="modelSelect">
            <option value="qwen/qwen3.8-27b:free" selected>Qwen 3.8 27B / 2.5-VL (Recommended: Fast & High Quality)</option>
            <option value="qwen/qwen2.5-vl-72b-instruct">Qwen 2.5 VL 72B (OpenRouter High Precision)</option>
            <option value="openai/gpt-4o">GPT-4o (OpenAI)</option>
            <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</option>
          </select>
        </div>
        <div>
          <label>Sample FPS</label>
          <select id="fpsSelect">
            <option value="1.0" selected>1.0 FPS (Standard)</option>
            <option value="0.5">0.5 FPS (Fast)</option>
            <option value="2.0">2.0 FPS (Ultra-smooth)</option>
          </select>
        </div>
      </div>

      <button class="btn" id="startBtn" onclick="submitVideo()">Start Processing Video</button>

      <div class="progress-bar" id="progressBar">
        <div class="progress-fill" id="progressFill"></div>
      </div>
      <div class="status-msg" id="statusMsg">Ready for submission.</div>
    </div>

    <div class="card">
      <h2>2. Live Result Stream</h2>
      <div id="videoContainer">
        <p class="sub" style="margin-bottom: 8px;">Annotated video preview will play automatically upon completion.</p>
        <video id="resultVideo" controls playsinline></video>
      </div>
    </div>
  </div>
</div>

<script>
  let selectedFile = null;
  document.getElementById('videoFile').addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      selectedFile = e.target.files[0];
      document.getElementById('fileLabel').innerText = `${selectedFile.name} (${(selectedFile.size/1024/1024).toFixed(2)} MB)`;
    }
  });

  async function submitVideo() {
    if (!selectedFile) {
      alert("Please select a video file first.");
      return;
    }

    const prompt = document.getElementById('promptInput').value;
    const model = document.getElementById('modelSelect').value;
    const sampleFps = document.getElementById('fpsSelect').value;

    const formData = new FormData();
    formData.append('video', selectedFile);
    formData.append('prompt', prompt);
    formData.append('model', model);
    formData.append('sample_fps', sampleFps);

    const btn = document.getElementById('startBtn');
    const pBar = document.getElementById('progressBar');
    const pFill = document.getElementById('progressFill');
    const statusMsg = document.getElementById('statusMsg');

    btn.disabled = true;
    pBar.style.display = 'block';
    pFill.style.width = '10%';
    statusMsg.innerText = 'Uploading video and queueing job...';

    try {
      const res = await fetch('/api/video/process', { method: 'POST', body: formData });
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || 'Failed to submit job');

      const jobId = data.job_id;
      pollStatus(jobId);
    } catch (err) {
      btn.disabled = false;
      statusMsg.innerText = 'Error: ' + err.message;
    }
  }

  async function pollStatus(jobId) {
    const pFill = document.getElementById('progressFill');
    const statusMsg = document.getElementById('statusMsg');
    const btn = document.getElementById('startBtn');

    try {
      const res = await fetch(`/api/video/status/${jobId}`);
      const data = await res.json();

      if (data.status === 'processing' || data.status === 'queued') {
        const pct = Math.max(15, Math.round((data.progress || 0) * 100));
        pFill.style.width = pct + '%';
        statusMsg.innerText = `[${pct}%] ${data.message || 'Processing frames...'}`;
        setTimeout(() => pollStatus(jobId), 1000);
      } else if (data.status === 'completed') {
        pFill.style.width = '100%';
        statusMsg.innerText = 'Annotation completed! Loading output video...';
        btn.disabled = false;

        const videoElem = document.getElementById('resultVideo');
        videoElem.src = `/api/video/result/${jobId}?t=` + Date.now();
        videoElem.play();
      } else {
        btn.disabled = false;
        statusMsg.innerText = 'Failed: ' + (data.error || 'Unknown error');
      }
    } catch (err) {
      setTimeout(() => pollStatus(jobId), 2000);
    }
  }
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    """Interactive Web Dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SketchVLM Video REST API Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    args = parser.parse_args()

    uvicorn.run("main:app", host=args.host, port=args.port, reload=False)
