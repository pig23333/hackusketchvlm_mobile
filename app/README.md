# SketchVLM Mobile — Android Frontend

AI-powered video annotation app for elderly and visually impaired users.
Built as an Android WebView shell that hosts a lightweight HTML/CSS/JS UI,
with all native capabilities (camera, gallery, speech, HTTP) handled in Kotlin.

---

## Overview

SketchVLM Mobile lets a user:

1. Pick or record a short video
2. Trim the segment to process
3. Choose an annotation task (object finding, appliance guidance, OCR, etc.)
4. Send the clip to a backend running SketchVLM
5. Receive and save the annotated video

The UI is intentionally minimal — large buttons, high contrast, voice input,
and a dedicated visual-impairment mode — so that elderly and low-vision users
can operate it without assistance.

---

## Tech Stack

| Layer | Technology |
|:---|:---|
| Shell | Android (Kotlin, AppCompat) |
| UI | HTML + CSS + vanilla JavaScript inside `WebView` |
| Networking | OkHttp 4.12 |
| Video metadata | `MediaMetadataRetriever` |
| Speech input | `RecognizerIntent` (system speech recognizer) |
| Save to gallery | `DownloadManager` |

No third-party UI frameworks. No JavaScript bundler. No npm. Everything lives
in `app/src/main/assets/` and is loaded from `file:///android_asset/`.

---

## Project Structure

```
app/
├── build.gradle.kts
├── proguard-rules.pro
└── src/main/
    ├── AndroidManifest.xml
    ├── assets/
    │   ├── index.html          # All screens (onboarding, home, trim, input, thinking, success, result)
    │   ├── style.css           # Design tokens, layout, dark/high-contrast mode
    │   └── script.js           # i18n, screen routing, native bridge calls
    ├── java/com/example/videoannotator/
    │   └── MainActivity.kt     # WebView host + JavaScript bridge
    └── res/
        └── values/
            ├── strings.xml
            └── themes.xml
```

---

## Requirements

- **JDK 17**
- **Android SDK** with:
  - `platforms;android-34`
  - `build-tools;34.0.0`
  - `platform-tools`
- A physical Android device (Android 7.0+ / API 24+) for testing
- Network access from the phone to the backend server (same LAN or VPN)

---

## Configuration

Before building, open:

```
app/src/main/java/com/example/videoannotator/MainActivity.kt
```

and set the backend URL:

```kotlin
const val BASE_URL = "http://<your-server-ip>:8000"
```

Notes:

- Do **not** use `localhost` — the phone cannot reach your PC's loopback.
- The server must listen on `0.0.0.0`, not `127.0.0.1`.
- For HTTPS-free local testing, `usesCleartextTraffic="true"` is already set
  in `AndroidManifest.xml`. Remove this for production builds.

---

## Build & Run

```bash
# From the app/ directory
./gradlew assembleDebug
```

The APK is produced at:

```
app/build/outputs/apk/debug/app-debug.apk
```

Install onto a connected device:

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

Launch:

```bash
adb shell monkey -p com.example.videoannotator \
  -c android.intent.category.LAUNCHER 1
```

---

## Features

### User-facing

- **Two entry points**: choose an existing video or record a new one
- **Trim page**: preview the clip, drag two handles to select a segment
- **Task picker**: three categories — Daily Life, Guidance, Accessibility —
  each with preset prompts; some require a short text or voice input
- **Voice input**: hold the round button to speak (uses the system recognizer)
- **Manual input**: type a custom prompt directly
- **Progress view**: shows upload percentage, then backend processing status
- **Success animation**: pure CSS + SVG circle-to-check animation
- **Result page**: plays the annotated video, offers save and retry

### Accessibility & i18n

- **Traditional Chinese** and **English**, switchable from every screen,
  persisted in `localStorage`
- **Three user modes**:
  - `normal` — default
  - `visual` — black background, yellow outlines, larger tap targets,
    full ARIA labelling for TalkBack
  - `voice` — same layout as normal, but every button press can trigger TTS
    (TTS hook is stubbed and ready for a future `TextToSpeech` bridge)
- **ARIA**: every interactive element has `aria-label`; progress bar exposes
  `aria-valuenow`; error modal uses `role="alertdialog"`; live regions use
  `aria-live`
- **Mode can be changed any time** from the gear button on the home screen

### Error handling

- Network failure, timeout, HTTP 5xx, missing `job_id`, backend processing
  failure, oversized video, unsupported voice or camera — all mapped to
  user-friendly bilingual dialogs

---

## Native Bridge

`MainActivity.kt` exposes a `AndroidBridge` object to JavaScript. Available
methods:

| Method | Purpose |
|:---|:---|
| `setLanguage(lang)` | Update the language used for speech recognition |
| `pickVideo()` | Open gallery picker for a video |
| `recordVideo()` | Open camera to record a new video |
| `startVoiceInput()` | Open the system speech recognizer |
| `getVideoUri()` | Return the selected video URI (as a string) |
| `getVideoInfo()` | Return JSON: duration, width, height, size, thumbnail (base64) |
| `submit(prompt, startMs, endMs)` | POST the video and prompt to the backend |
| `saveResult()` | Use `DownloadManager` to save the result video |
| `reset()` | Clear the selected video and job ID |

Callbacks invoked from Kotlin into JS:

| Callback | When |
|:---|:---|
| `onVideoSelected()` | User picked or recorded a video |
| `onVideoCancelled()` | User cancelled the picker |
| `onVoiceResult(text)` | Speech recognizer returned text |
| `onProgress(progress, message)` | Upload or processing progress |
| `onComplete(resultUrl)` | Backend finished, ready to play |
| `onError(code, extra)` | Something went wrong |

---

## Backend Contract

The frontend expects these three endpoints. Field names must match exactly.

### `POST /api/video/process`

`multipart/form-data` with:

- `video` — the video file
- `prompt` — string
- `sample_fps` — float (default `1.0`)
- `start_ms`, `end_ms` — optional integers, if the backend supports trimming

Returns **202**:

```json
{
  "ok": true,
  "job_id": "job_xxxxxxxxxxxx",
  "status": "queued",
  "poll_url": "/api/video/status/job_xxxxxxxxxxxx",
  "result_url": "/api/video/result/job_xxxxxxxxxxxx"
}
```

### `GET /api/video/status/{job_id}`

Returns **200**:

```json
{
  "ok": true,
  "job_id": "job_xxxxxxxxxxxx",
  "status": "processing",
  "progress": 0.65,
  "message": "VLM processed keyframe 2/3",
  "error": null
}
```

`status` enum: `queued` → `processing` → `completed` / `failed`

### `GET /api/video/result/{job_id}`

Returns a `video/mp4` binary stream. Must support HTTP Range requests so the
player can seek and loop.

---

## Design Notes

### Why WebView instead of native UI

The team's strength was in web frontend, and the UI is mostly static
screens with form-like interactions. WebView gave us:

- Fast iteration (no rebuild between layout tweaks)
- A single source of truth for i18n and accessibility attributes
- Reusable CSS for the three display modes

The trade-off is WebView startup latency and a slightly less native feel.
For a hackathon prototype this is acceptable; for production, consider
Jetpack Compose with the same design tokens.

### Why inline SVG instead of image assets

All icons are inline `<svg>` elements inside `index.html`. This avoids:

- Extra HTTP requests over `file://` (which some WebViews block)
- Separate light/dark asset variants — `stroke="currentColor"` handles it
- Icon fonts, which need a separate font file and can flash on load

### Why a pure CSS success animation

We originally planned to use Lottie, but loading a `.json` asset from
`file:///android_asset/` is unreliable across WebView versions and often
blocked by CORS. The current animation is a two-path SVG with
`stroke-dasharray` transitions — no external file, 100% reliable.

---

## Accessibility Checklist

When adding new UI, verify:

- [ ] Every interactive element has an `aria-label` describing what it does
- [ ] Decorative SVGs have `aria-hidden="true"`
- [ ] Dynamic text regions use `role="status"` or `aria-live`
- [ ] Modals use `role="alertdialog"` or `role="dialog"` with `aria-modal="true"`
- [ ] Tap targets are at least 48×48 dp
- [ ] Text contrast meets WCAG AA (4.5:1) in the default mode
- [ ] In `mode-visual`, contrast meets WCAG AAA (7:1)
- [ ] Works with TalkBack enabled end-to-end

---

## Known Limitations

- **TTS is not wired up.** The `voice` mode toggles layout and announces
  mode changes, but does not yet speak every button press. A `TextToSpeech`
  bridge is the next step.
- **Speech recognition requires a system recognizer.** Some devices ship
  without one; the app falls back gracefully with an error dialog.
- **No offline queue.** If the network drops mid-upload the job is lost and
  the user must retry manually.
- **Trimming is metadata-only.** The `start_ms` / `end_ms` fields are sent
  to the backend, but the video itself is uploaded in full. The backend is
  expected to honor the range; if it doesn't, ignore the fields.
- **Videos are capped at 50 MB.** This is a client-side guard in
  `MainActivity.kt` (`MAX_VIDEO_SIZE`), not a server limit.

---

## Development Workflow

```bash
# Make changes to assets/ (HTML/CSS/JS) — rebuild is required because
# WebView loads from the packaged APK, not a dev server.

cd app
./gradlew assembleDebug
adb install -r build/outputs/apk/debug/app-debug.apk
adb shell monkey -p com.example.videoannotator \
  -c android.intent.category.LAUNCHER 1
```

For faster UI iteration, you can open `app/src/main/assets/index.html`
directly in a desktop browser. The `AndroidBridge` calls will fail with
`undefined`, but layout, colors, animations and i18n all work.

---

## Team

- Frontend / UI: _(add your name)_
- Backend / VLM: _(add teammate's name)_

---

## License

Prototype for HackU 2026. Not for commercial use.