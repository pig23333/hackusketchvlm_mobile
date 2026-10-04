package com.example.videoannotator

import android.app.Activity
import android.app.DownloadManager
import android.content.ContentResolver
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.media.MediaMetadataRetriever
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.provider.MediaStore
import android.speech.RecognizerIntent
import android.util.Base64
import android.util.Log
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okio.BufferedSink
import okio.ForwardingSink
import okio.buffer
import okio.source
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {

    companion object {
        const val BASE_URL = "http://100.112.76.36:8000"
        const val MAX_VIDEO_SIZE = 50L * 1024 * 1024
        private const val TAG = "VideoAnnotator"
    }

    private lateinit var webView: WebView
    private var selectedVideoUri: Uri? = null
    private var lastJobId: String? = null
    private var currentVoiceLang: String = "zh-HK"

    private val handler = Handler(Looper.getMainLooper())

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(180, TimeUnit.SECONDS)
        .writeTimeout(300, TimeUnit.SECONDS)
        .build()

    private val pickVideoLauncher =
        registerForActivityResult(ActivityResultContracts.GetContent()) { uri ->
            if (uri != null) {
                selectedVideoUri = uri
                callJs("onVideoSelected")
            } else {
                callJs("onVideoCancelled")
            }
        }

    private val recordVideoLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (result.resultCode == Activity.RESULT_OK) {
                selectedVideoUri = result.data?.data
                callJs("onVideoSelected")
            } else {
                callJs("onVideoCancelled")
            }
        }

    private val voiceLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (result.resultCode == Activity.RESULT_OK) {
                val text = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull()
                callJs("onVoiceResult", text ?: "")
            } else {
                callJs("onVoiceResult", "")
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        webView = WebView(this)
        setContentView(webView)

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            mediaPlaybackRequiresUserGesture = false
        }
        webView.webViewClient = WebViewClient()
        webView.webChromeClient = WebChromeClient()
        webView.addJavascriptInterface(Bridge(), "AndroidBridge")
        webView.loadUrl("file:///android_asset/index.html")
    }

    private fun callJs(function: String, vararg args: Any?) {
        val argsJson = args.joinToString(",") { arg ->
            when (arg) {
                null -> "null"
                is Number, is Boolean -> arg.toString()
                else -> {
                    val escaped = arg.toString()
                        .replace("\\", "\\\\")
                        .replace("\"", "\\\"")
                        .replace("\n", "\\n")
                        .replace("\r", "\\r")
                    "\"$escaped\""
                }
            }
        }
        val js = "javascript:try{window.$function($argsJson)}catch(e){console.error(e)}"
        runOnUiThread { webView.evaluateJavascript(js, null) }
    }

    private fun getVideoSize(uri: Uri): Long {
        return try {
            contentResolver.openAssetFileDescriptor(uri, "r")?.use { it.length } ?: 0L
        } catch (e: Exception) { 0L }
    }

    private fun networkCodeFor(e: IOException): String = when (e) {
        is SocketTimeoutException -> "timeout"
        is UnknownHostException -> "network"
        is ConnectException -> "network"
        else -> "network"
    }

    inner class Bridge {

        @JavascriptInterface
        fun setLanguage(lang: String) { currentVoiceLang = lang }

        @JavascriptInterface
        fun pickVideo() {
            runOnUiThread {
                try { pickVideoLauncher.launch("video/*") }
                catch (e: Exception) { callJs("onError", "unknown") }
            }
        }

        @JavascriptInterface
        fun recordVideo() {
            runOnUiThread {
                try {
                    val intent = Intent(MediaStore.ACTION_VIDEO_CAPTURE)
                    if (intent.resolveActivity(packageManager) == null) {
                        callJs("onError", "camera"); return@runOnUiThread
                    }
                    recordVideoLauncher.launch(intent)
                } catch (e: Exception) { callJs("onError", "camera") }
            }
        }

        @JavascriptInterface
        fun startVoiceInput() {
            runOnUiThread {
                try {
                    val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                        putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                        putExtra(RecognizerIntent.EXTRA_PROMPT, "請說出您的需求 / Please speak")
                        putExtra(RecognizerIntent.EXTRA_LANGUAGE, currentVoiceLang)
                    }
                    if (intent.resolveActivity(packageManager) == null) {
                        callJs("onError", "voice"); callJs("onVoiceResult", ""); return@runOnUiThread
                    }
                    voiceLauncher.launch(intent)
                } catch (e: Exception) {
                    callJs("onError", "voice"); callJs("onVoiceResult", "")
                }
            }
        }

        @JavascriptInterface
        fun getVideoUri(): String {
            return selectedVideoUri?.toString() ?: ""
        }

        @JavascriptInterface
        fun getVideoInfo(): String {
            val uri = selectedVideoUri ?: return "{}"
            val retriever = MediaMetadataRetriever()
            var durationMs = 0L; var w = 0; var h = 0; var thumb = ""
            try {
                retriever.setDataSource(this@MainActivity, uri)
                durationMs = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLongOrNull() ?: 0L
                w = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH)?.toIntOrNull() ?: 0
                h = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT)?.toIntOrNull() ?: 0
                val bmp = retriever.getFrameAtTime(0, MediaMetadataRetriever.OPTION_CLOSEST_SYNC)
                if (bmp != null) {
                    val maxW = 480
                    val scale = if (bmp.width > maxW) maxW.toFloat() / bmp.width else 1f
                    val scaled = Bitmap.createScaledBitmap(
                        bmp,
                        (bmp.width * scale).toInt().coerceAtLeast(1),
                        (bmp.height * scale).toInt().coerceAtLeast(1),
                        true
                    )
                    val baos = ByteArrayOutputStream()
                    scaled.compress(Bitmap.CompressFormat.JPEG, 80, baos)
                    thumb = "data:image/jpeg;base64," + Base64.encodeToString(baos.toByteArray(), Base64.NO_WRAP)
                    if (scaled !== bmp) scaled.recycle()
                    bmp.recycle()
                }
            } catch (e: Exception) { Log.e(TAG, "getVideoInfo", e) }
            finally { try { retriever.release() } catch (_: Exception) {} }

            return JSONObject().apply {
                put("duration", durationMs)
                put("width", w)
                put("height", h)
                put("size", getVideoSize(uri))
                put("thumbnail", thumb)
            }.toString()
        }

        /** 一次性提交：上传视频 + prompt */
        @JavascriptInterface
        fun submit(prompt: String, startMs: Long, endMs: Long) {
            val uri = selectedVideoUri ?: run {
                callJs("onError", "no_video"); return
            }
            if (prompt.isBlank()) {
                callJs("onError", "no_prompt"); return
            }
            val size = getVideoSize(uri)
            if (size > MAX_VIDEO_SIZE) {
                callJs("onError", "video_large"); return
            }
            doSubmit(uri, prompt, startMs, endMs)
        }

        @JavascriptInterface
        fun saveResult() {
            val jobId = lastJobId ?: return
            runOnUiThread { saveVideoToGallery(jobId) }
        }

        @JavascriptInterface
        fun reset() {
            selectedVideoUri = null
            lastJobId = null
        }
    }

    // ==================== 提交处理 ====================
    private fun doSubmit(uri: Uri, prompt: String, startMs: Long, endMs: Long) {
        // 上传阶段：0.01 ~ 0.20
        callJs("onProgress", 0.01, "")

        val videoBody = ProgressRequestBody(
            contentResolver, uri, "video/mp4".toMediaTypeOrNull()
        ) { sent, total ->
            val p = if (total > 0) sent.toDouble() / total else 0.0
            val mapped = 0.01 + p * 0.19
            callJs("onProgress", mapped, "")
        }

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("video", "upload.mp4", videoBody)
            .addFormDataPart("prompt", prompt)
            .addFormDataPart("sample_fps", "1.0")
            .addFormDataPart("start_ms", startMs.toString())
            .addFormDataPart("end_ms", endMs.toString())
            .build()

        val request = Request.Builder()
            .url("$BASE_URL/api/video/process")
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callJs("onError", networkCodeFor(e))
            }

            override fun onResponse(call: Call, response: Response) {
                val body = response.body?.string()
                if (!response.isSuccessful || body == null) {
                    callJs("onError", "server", response.code.toString())
                    return
                }
                val jobId = try { JSONObject(body).optString("job_id") } catch (e: Exception) { "" }
                if (jobId.isEmpty()) {
                    callJs("onError", "no_job_id"); return
                }
                lastJobId = jobId
                // 进入处理阶段
                callJs("onProgress", 0.20, "")
                handler.postDelayed({ pollStatus(jobId) }, 400)
            }
        })
    }

    private fun pollStatus(jobId: String) {
        val request = Request.Builder()
            .url("$BASE_URL/api/video/status/$jobId").get().build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                handler.postDelayed({ pollStatus(jobId) }, 2000)
            }
            override fun onResponse(call: Call, response: Response) {
                val body = response.body?.string()
                if (!response.isSuccessful || body == null) {
                    callJs("onError", "server", response.code.toString()); return
                }
                val json = try { JSONObject(body) } catch (e: Exception) {
                    callJs("onError", "server", "parse"); return
                }
                val status = json.optString("status")
                val progress = json.optDouble("progress", 0.0)
                val message = json.optString("message", status)

                when (status) {
                    "completed" -> {
                        callJs("onProgress", 1.0, "")
                        callJs("onComplete", "$BASE_URL/api/video/result/$jobId")
                    }
                    "failed" -> callJs("onError", "process", json.optString("error", ""))
                    else -> {
                        // 处理阶段：0.20 ~ 1.0
                        val mapped = 0.20 + progress * 0.80
                        callJs("onProgress", mapped, message)
                        handler.postDelayed({ pollStatus(jobId) }, 1000)
                    }
                }
            }
        })
    }

    private fun saveVideoToGallery(jobId: String) {
        try {
            val request = DownloadManager.Request(Uri.parse("$BASE_URL/api/video/result/$jobId"))
                .setTitle("保存標註影片 / Saving")
                .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                .setDestinationInExternalPublicDir(Environment.DIRECTORY_MOVIES, "annotated_$jobId.mp4")
            (getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager).enqueue(request)
            Toast.makeText(this, "已開始儲存 / Saving...", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) { callJs("onError", "unknown") }
    }

    // ==================== 带进度的 RequestBody ====================
    private class ProgressRequestBody(
        private val cr: ContentResolver,
        private val uri: Uri,
        private val contentType: MediaType?,
        private val onProgress: (Long, Long) -> Unit
    ) : RequestBody() {
        override fun contentType(): MediaType? = contentType
        override fun contentLength(): Long = -1

        override fun writeTo(sink: BufferedSink) {
            val total = try {
                cr.openAssetFileDescriptor(uri, "r")?.use { it.length } ?: -1L
            } catch (e: Exception) { -1L }

            var written = 0L
            val forwarding = object : ForwardingSink(sink) {
                override fun write(source: okio.Buffer, byteCount: Long) {
                    super.write(source, byteCount)
                    written += byteCount
                    onProgress(written, total)
                }
            }
            val buffered = forwarding.buffer()
            cr.openInputStream(uri)?.use { input ->
                buffered.writeAll(input.source())
            } ?: throw IOException("Cannot open video stream")
            buffered.flush()
        }
    }
}