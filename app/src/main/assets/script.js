// ===================== 国际化 =====================
const i18n = {
    zh: {
        onboarding_title: "歡迎使用",
        onboarding_desc: "請選擇最適合您的模式",
        onboarding_confirm: "開始使用",
        mode_normal: "一般模式",
        mode_normal_desc: "標準介面，適合大多數使用者",
        mode_visual: "視障模式",
        mode_visual_desc: "高對比度、大字體，支援螢幕閱讀器",
        mode_voice: "語音增強模式",
        mode_voice_desc: "按鈕語音播報，適合長者",

        settings_title: "使用模式",
        settings_close: "關閉",

        home_title: "SketchVLM Mobile",
        home_subtitle: "AI 智慧視覺，讓溝通更簡單",
        choose_video: "選擇影片",
        record_video: "拍攝影片",
        trim_title: "選擇要處理的片段",
        trim_hint: "拖動滑桿選擇範圍，點擊下方播放按鈕預覽",
        next_step: "下一步",
        input_header: "您需要什麼幫助？",
        prompt_placeholder: "點擊上方功能，或按住下方按鈕說話",
        input_placeholder: "或在這裡自己打字…",
        hold_speak: "按住 說話",
        hold_release: "鬆開 結束",
        back: "返回",
        confirm: "確認",

        thinking: "正在思考...",
        thinking_hint: "請稍等，AI 正在處理您的影片",
        uploading_pct: "正在上傳 {pct}%",
        uploading_hint: "請稍等，影片正在上傳",
        processing: "正在處理...",
        almost_done: "即將完成...",

        success_title: "處理完成",
        success_hint: "馬上就好，正在準備您的影片…",

        result_done: "處理完成",
        save: "儲存到相簿",
        try_again: "再來一次",

        input_modal_cancel: "取消",
        input_modal_confirm: "確定",

        err_ok: "確定",
        err_title_network: "連線失敗",
        err_msg_network: "無法連線到伺服器，請檢查網路後再試。",
        err_title_timeout: "請求逾時",
        err_msg_timeout: "伺服器回應太慢，請稍後再試。",
        err_title_server: "伺服器錯誤",
        err_msg_server: "伺服器暫時無法處理請求（錯誤碼：{code}）。",
        err_title_no_job: "伺服器回應異常",
        err_msg_no_job: "伺服器未返回任務 ID，請稍後再試。",
        err_title_process: "處理失敗",
        err_msg_process: "影片處理失敗。{msg}",
        err_title_video_large: "影片過大",
        err_msg_video_large: "請選擇 50MB 以下的影片。",
        err_title_no_video: "尚未選擇影片",
        err_msg_no_video: "請先選擇或拍攝一段影片。",
        err_title_no_prompt: "尚未輸入需求",
        err_msg_no_prompt: "請輸入或說出您的需求。",
        err_title_voice: "語音無法使用",
        err_msg_voice: "您的裝置不支援語音輸入，請改用打字。",
        err_title_camera: "相機無法使用",
        err_msg_camera: "無法開啟相機，請改用選擇影片。",
        err_title_unknown: "發生錯誤",
        err_msg_unknown: "發生未知錯誤，請稍後再試。"
    },
    en: {
        onboarding_title: "Welcome",
        onboarding_desc: "Please choose the mode that suits you best",
        onboarding_confirm: "Get Started",
        mode_normal: "Standard Mode",
        mode_normal_desc: "Standard interface for most users",
        mode_visual: "Visual Impairment Mode",
        mode_visual_desc: "High contrast, large text, screen reader support",
        mode_voice: "Voice Enhanced Mode",
        mode_voice_desc: "Button voice feedback, ideal for seniors",

        settings_title: "Display Mode",
        settings_close: "Close",

        home_title: "SketchVLM Mobile",
        home_subtitle: "AI Vision, Made Simple.",
        choose_video: "Choose Video",
        record_video: "Record Video",
        trim_title: "Select segment to process",
        trim_hint: "Drag the sliders to select a range, tap play to preview",
        next_step: "Next",
        input_header: "What do you need help with?",
        prompt_placeholder: "Tap a function above, or hold the button below to speak",
        input_placeholder: "Or type your own here…",
        hold_speak: "Hold to Speak",
        hold_release: "Release to Stop",
        back: "Back",
        confirm: "Confirm",

        thinking: "Thinking...",
        thinking_hint: "Please wait, AI is processing your video",
        uploading_pct: "Uploading {pct}%",
        uploading_hint: "Please wait, uploading video",
        processing: "Processing...",
        almost_done: "Almost done...",

        success_title: "Complete",
        success_hint: "Almost there, preparing your video…",

        result_done: "Complete",
        save: "Save to Album",
        try_again: "Try Again",

        input_modal_cancel: "Cancel",
        input_modal_confirm: "Confirm",

        err_ok: "OK",
        err_title_network: "Connection Failed",
        err_msg_network: "Cannot reach the server. Please check your network.",
        err_title_timeout: "Request Timeout",
        err_msg_timeout: "The server is taking too long. Please try again later.",
        err_title_server: "Server Error",
        err_msg_server: "Server is temporarily unavailable (code: {code}).",
        err_title_no_job: "Invalid Response",
        err_msg_no_job: "Server did not return a job ID. Please try again.",
        err_title_process: "Processing Failed",
        err_msg_process: "Failed to process the video. {msg}",
        err_title_video_large: "Video Too Large",
        err_msg_video_large: "Please choose a video under 50 MB.",
        err_title_no_video: "No Video Selected",
        err_msg_no_video: "Please choose or record a video first.",
        err_title_no_prompt: "No Request Entered",
        err_msg_no_prompt: "Please enter or speak your request.",
        err_title_voice: "Voice Unavailable",
        err_msg_voice: "Voice input is not supported on this device. Please type.",
        err_title_camera: "Camera Unavailable",
        err_msg_camera: "Cannot open camera. Please choose a video instead.",
        err_title_unknown: "Error",
        err_msg_unknown: "An unknown error occurred. Please try again."
    }
};

// ===================== 提示词分类 =====================
const promptCategories = {
    zh: [
        {
            key: "life",
            label: "生活",
            items: [
                {
                    label: "物品尋找",
                    needsInput: true,
                    inputTitle: "想找什麼？",
                    inputPlaceholder: "例如：眼鏡、鑰匙、手機、錢包",
                    prompt: "幫我在影片中尋找{input}，並用標註框框出來"
                },
                {
                    label: "寵物追蹤",
                    prompt: "追蹤影片中的寵物，並用標註框持續標示牠的位置"
                },
                {
                    label: "安全檢查",
                    prompt: "標示畫面中可能造成危險的位置，例如電線、尖銳物、濕滑地面"
                }
            ]
        },
        {
            key: "guidance",
            label: "教學指引",
            items: [
                {
                    label: "家電使用",
                    needsInput: true,
                    inputTitle: "這是什麼家電？遇到什麼問題？",
                    inputPlaceholder: "例如：洗衣機不會脫水、冷氣不冷",
                    prompt: "這是{input}，請標示操作按鈕的位置，並用標註框指出問題所在"
                },
                {
                    label: "維修指引",
                    needsInput: true,
                    inputTitle: "什麼設備？出了什麼問題？",
                    inputPlaceholder: "例如：水龍頭漏水、燈不亮",
                    prompt: "設備是{input}，請標示可能故障的位置與檢查步驟"
                },
                {
                    label: "操作步驟",
                    prompt: "逐步標示畫面中物品的操作步驟，用數字標明先後順序"
                },
                {
                    label: "組裝指引",
                    prompt: "標示畫面中零件的組裝位置與順序"
                }
            ]
        },
        {
            key: "accessibility",
            label: "無障礙",
            items: [
                { label: "文字辨識", prompt: "辨識畫面中的所有文字（OCR），並用標註框框出每段文字" },
                { label: "障礙物提示", prompt: "標示畫面中可能造成危險的障礙物，並用醒目的框標記" },
                { label: "顏色辨識", prompt: "辨識畫面中的主要顏色，並在對應區域標示顏色名稱" },
                { label: "場景描述", prompt: "描述畫面中的場景內容，並用標註框標出主要物件" }
            ]
        }
    ],
    en: [
        {
            key: "life",
            label: "Daily Life",
            items: [
                {
                    label: "Find Object",
                    needsInput: true,
                    inputTitle: "What are you looking for?",
                    inputPlaceholder: "e.g. glasses, keys, phone, wallet",
                    prompt: "Find {input} in the video and label it with a box"
                },
                {
                    label: "Track Pet",
                    prompt: "Track my pet in the video with a bounding box"
                },
                {
                    label: "Safety Check",
                    prompt: "Label potential hazards such as wires, sharp objects, wet floor"
                }
            ]
        },
        {
            key: "guidance",
            label: "Guidance",
            items: [
                {
                    label: "Appliance Use",
                    needsInput: true,
                    inputTitle: "What appliance? What's the issue?",
                    inputPlaceholder: "e.g. washer won't spin, AC not cold",
                    prompt: "This is {input}. Label the controls and highlight the issue area"
                },
                {
                    label: "Repair Guide",
                    needsInput: true,
                    inputTitle: "What device? What's wrong?",
                    inputPlaceholder: "e.g. leaking faucet, broken light",
                    prompt: "The device is {input}. Label the likely fault and inspection steps"
                },
                {
                    label: "Operation Steps",
                    prompt: "Label the operation steps with numbers showing the correct order"
                },
                {
                    label: "Assembly Guide",
                    prompt: "Label the assembly positions and order of the parts shown"
                }
            ]
        },
        {
            key: "accessibility",
            label: "Accessibility",
            items: [
                { label: "Read Text", prompt: "Read all text in the frame (OCR) and label each block" },
                { label: "Obstacle Alert", prompt: "Highlight obstacles that may cause danger with prominent boxes" },
                { label: "Color Name", prompt: "Identify the main colors and label each region with its color name" },
                { label: "Describe Scene", prompt: "Describe the scene and label the main objects with boxes" }
            ]
        }
    ]
};

let currentLang = "zh";
let currentCategoryIndex = 0;
let userMode = "normal";

let pendingInputItem = null;
let modalVoiceHolding = false;

function t(key) {
    return (i18n[currentLang] && i18n[currentLang][key]) || key;
}

function setLang(lang) {
    currentLang = lang;
    localStorage.setItem("lang", lang);

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
        el.textContent = t(el.getAttribute("data-i18n"));
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
        el.placeholder = t(el.getAttribute("data-i18n-placeholder"));
    });
    document.querySelectorAll(".lang-btn").forEach(function (btn) {
        btn.classList.toggle("active", btn.getAttribute("data-lang") === lang);
    });
    document.documentElement.lang = lang === "zh" ? "zh-Hant" : "en";

    if (window.AndroidBridge && window.AndroidBridge.setLanguage) {
        window.AndroidBridge.setLanguage(lang === "zh" ? "zh-HK" : "en-US");
    }

    updatePromptDisplay();
    renderCategories();
    renderSettingsOptions();

    var cancelBtn = document.getElementById("inputModalCancel");
    var confirmBtn = document.getElementById("inputModalConfirm");
    if (cancelBtn) cancelBtn.textContent = t("input_modal_cancel");
    if (confirmBtn) confirmBtn.textContent = t("input_modal_confirm");
}

// ===================== 无障碍 =====================
function announce(text) {
    if (!text) return;
    if (userMode !== "voice" && userMode !== "visual") return;
    if (window.AndroidBridge && window.AndroidBridge.speak) {
        var lang = currentLang === "zh" ? "zh-HK" : "en-US";
        window.AndroidBridge.speak(text, lang);
    }
}

function applyUserMode(mode) {
    userMode = mode;
    localStorage.setItem("userMode", mode);
    document.body.classList.remove("mode-normal", "mode-visual", "mode-voice");
    document.body.classList.add("mode-" + mode);

    // 更新设置弹窗里的高亮
    renderSettingsOptions();
}

// ===================== 引导页 =====================
let selectedOnboardingMode = null;

function selectMode(mode) {
    selectedOnboardingMode = mode;
    document.querySelectorAll(".mode-card").forEach(function (card) {
        card.classList.toggle("selected", card.getAttribute("data-mode") === mode);
    });
    var btn = document.getElementById("onboardingConfirm");
    if (btn) btn.disabled = false;

    if (mode === "voice" || mode === "visual") {
        var key = mode === "voice" ? "mode_voice" : "mode_visual";
        announce(t(key));
    }
}

function confirmOnboarding() {
    if (!selectedOnboardingMode) return;
    applyUserMode(selectedOnboardingMode);
    showScreen("screen-home");
    setTimeout(function () { announce(t("home_title")); }, 400);
}

// ===================== 设置弹窗 =====================
function openSettings() {
    renderSettingsOptions();
    document.getElementById("settingsOverlay").classList.add("active");
}

function closeSettings() {
    document.getElementById("settingsOverlay").classList.remove("active");
}

function renderSettingsOptions() {
    var container = document.getElementById("settingsOptions");
    if (!container) return;

    var modes = [
        { key: "normal", icon: "eye", nameKey: "mode_normal", descKey: "mode_normal_desc" },
        { key: "visual", icon: "accessibility", nameKey: "mode_visual", descKey: "mode_visual_desc" },
        { key: "voice", icon: "volume", nameKey: "mode_voice", descKey: "mode_voice_desc" }
    ];

    var iconSvg = {
        eye: '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/>',
        accessibility: '<circle cx="16" cy="4" r="1"/><path d="m18 19 1-7-6 1"/><path d="m5 8 3-3 5.5 3-2.36 3.5"/><path d="M4.24 14.5a5 5 0 0 0 6.88 6"/><path d="M13.76 17.5a5 5 0 0 0-6.88-6"/>',
        volume: '<path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z"/><path d="M16 9a5 5 0 0 1 0 6"/><path d="M19.364 18.364a9 9 0 0 0 0-12.728"/>'
    };

    container.innerHTML = "";
    modes.forEach(function (m) {
        var btn = document.createElement("button");
        btn.className = "settings-option" + (userMode === m.key ? " selected" : "");
        btn.setAttribute("data-mode", m.key);
        btn.setAttribute("aria-label", t(m.nameKey));
        btn.onclick = function () { changeMode(m.key); };

        btn.innerHTML =
            '<span class="settings-option-icon">' +
                '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
                    iconSvg[m.icon] +
                '</svg>' +
            '</span>' +
            '<span class="settings-option-text">' +
                '<span class="settings-option-name">' + t(m.nameKey) + '</span>' +
                '<span class="settings-option-desc">' + t(m.descKey) + '</span>' +
            '</span>' +
            '<span class="settings-option-check">' +
                '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
                    '<path d="M20 6 9 17l-5-5"/>' +
                '</svg>' +
            '</span>';

        container.appendChild(btn);
    });
}

function changeMode(mode) {
    if (mode === userMode) {
        // 已选中，直接关闭
        setTimeout(closeSettings, 100);
        return;
    }

    applyUserMode(mode);

    // 语音增强或视障模式，播报模式名称
    if (mode === "voice" || mode === "visual") {
        var key = mode === "voice" ? "mode_voice" : "mode_visual";
        announce(t(key));
    }

    setTimeout(closeSettings, 350);
}

// ===================== 状态 =====================
let currentPrompt = "";
let isHolding = false;
let currentVideoInfo = null;
let currentTrimStart = 0;
let currentTrimEnd = 0;
let isPlaying = false;

function showScreen(id) {
    document.querySelectorAll(".screen").forEach(function (s) { s.classList.remove("active"); });
    document.getElementById(id).classList.add("active");

    if (userMode === "visual") {
        var screenEl = document.getElementById(id);
        if (screenEl) {
            var label = screenEl.getAttribute("aria-label");
            if (label) announce(label);
        }
    }
}

// ===================== 首页 =====================
function pickVideo() {
    announce(t("choose_video"));
    if (window.AndroidBridge) window.AndroidBridge.pickVideo();
}
function recordVideo() {
    announce(t("record_video"));
    if (window.AndroidBridge) window.AndroidBridge.recordVideo();
}

// ===================== 原生回调 =====================
function onVideoSelected() {
    resetAll();
    showScreen("screen-trim");
    loadVideoIntoPlayer();
}
function onVideoCancelled() {}

function onVoiceResult(text) {
    endHoldVisual();
    endModalHoldVisual();

    var modalOpen = document.getElementById("inputModalOverlay").classList.contains("active");

    if (modalOpen) {
        if (text && text.trim()) {
            var modalInput = document.getElementById("inputModalInput");
            if (modalInput) modalInput.value = text.trim();
        }
    } else {
        if (text && text.trim()) {
            currentPrompt = text.trim();
            var mainInput = document.getElementById("promptInput");
            if (mainInput) mainInput.value = currentPrompt;
            updatePromptDisplay();
            updateConfirmState();
            announce(text.trim());
        }
    }
}

function onProgress(progress, message) {
    var p = Math.max(0, Math.min(1, progress));
    document.getElementById("progressFill").style.width = (p * 100) + "%";

    var pb = document.querySelector(".progress-bar");
    if (pb) pb.setAttribute("aria-valuenow", Math.round(p * 100));

    if (userMode === "visual") {
        if (p >= 0.20 && p < 0.24) {
            announce(currentLang === "zh" ? "上傳完成" : "Upload complete");
        } else if (p >= 1.0) {
            announce(currentLang === "zh" ? "處理完成" : "Processing complete");
        }
    }

    if (p < 0.20) {
        var uploadPct = Math.round((p - 0.01) / 0.19 * 100);
        uploadPct = Math.max(0, Math.min(100, uploadPct));
        document.getElementById("thinkingText").textContent =
            t("uploading_pct").replace("{pct}", uploadPct);
        document.getElementById("thinkingHint").textContent = t("uploading_hint");
    } else {
        document.getElementById("thinkingText").textContent = message || t("processing");
        document.getElementById("thinkingHint").textContent = t("thinking_hint");
    }
    if (p >= 1.0) {
        document.getElementById("thinkingHint").textContent = t("almost_done");
    }
}

function onComplete(resultUrl) {
    showScreen("screen-success");

    if (userMode === "visual" || userMode === "voice") {
        announce(t("success_title"));
    }

    setTimeout(function () {
        var video = document.getElementById("resultVideo");
        video.src = resultUrl;
        video.load();
        showScreen("screen-result");
    }, 2000);
}

// ===================== 错误 =====================
function onError(code, extra) {
    var thinkingActive = document.getElementById("screen-thinking").classList.contains("active");
    var successActive = document.getElementById("screen-success").classList.contains("active");
    if (thinkingActive || successActive) showScreen("screen-input");
    showErrorDialog(code, extra);
}

function showErrorDialog(code, extra) {
    var titleKey, msgKey, params = {};
    switch (code) {
        case "network": titleKey = "err_title_network"; msgKey = "err_msg_network"; break;
        case "timeout": titleKey = "err_title_timeout"; msgKey = "err_msg_timeout"; break;
        case "server": titleKey = "err_title_server"; msgKey = "err_msg_server"; params.code = extra || "?"; break;
        case "no_job_id": titleKey = "err_title_no_job"; msgKey = "err_msg_no_job"; break;
        case "process": titleKey = "err_title_process"; msgKey = "err_msg_process"; params.msg = extra ? ("（" + extra + "）") : ""; break;
        case "video_large": titleKey = "err_title_video_large"; msgKey = "err_msg_video_large"; break;
        case "no_video": titleKey = "err_title_no_video"; msgKey = "err_msg_no_video"; break;
        case "no_prompt": titleKey = "err_title_no_prompt"; msgKey = "err_msg_no_prompt"; break;
        case "voice": titleKey = "err_title_voice"; msgKey = "err_msg_voice"; break;
        case "camera": titleKey = "err_title_camera"; msgKey = "err_msg_camera"; break;
        default: titleKey = "err_title_unknown"; msgKey = "err_msg_unknown";
    }
    var title = t(titleKey);
    var msg = t(msgKey);
    for (var k in params) msg = msg.replace("{" + k + "}", params[k]);

    document.getElementById("errTitle").textContent = title;
    document.getElementById("errMsg").textContent = msg;
    document.getElementById("errOkBtn").textContent = t("err_ok");
    document.getElementById("errOverlay").classList.add("active");

    if (userMode === "visual" || userMode === "voice") {
        announce(title + "。" + msg);
    }
    setTimeout(function () {
        var btn = document.getElementById("errOkBtn");
        if (btn) btn.focus();
    }, 100);
}

function closeError() {
    document.getElementById("errOverlay").classList.remove("active");
    var confirmBtn = document.getElementById("confirmBtn");
    if (confirmBtn && confirmBtn.offsetParent !== null) confirmBtn.focus();
}

// ===================== 二次输入弹窗 =====================
function openInputModal(item) {
    pendingInputItem = item;
    var overlay = document.getElementById("inputModalOverlay");
    var titleEl = document.getElementById("inputModalTitle");
    var inputEl = document.getElementById("inputModalInput");

    titleEl.textContent = item.inputTitle || t("input_modal_confirm");
    inputEl.placeholder = item.inputPlaceholder || "";
    inputEl.value = "";

    overlay.classList.add("active");

    if (userMode === "visual" || userMode === "voice") {
        announce(titleEl.textContent);
    }
    setTimeout(function () { inputEl.focus(); }, 200);
}

function closeInputModal() {
    document.getElementById("inputModalOverlay").classList.remove("active");
    pendingInputItem = null;
    endModalHoldVisual();
}

function confirmInputModal() {
    if (!pendingInputItem) return;
    var inputEl = document.getElementById("inputModalInput");
    var val = inputEl.value.trim();
    if (!val) {
        inputEl.focus();
        return;
    }
    var fullPrompt = pendingInputItem.prompt.replace("{input}", val);
    setPromptText(fullPrompt);
    closeInputModal();
}

function startModalHold(e) {
    e.preventDefault();
    if (modalVoiceHolding) return;
    modalVoiceHolding = true;
    var btn = document.getElementById("inputModalVoice");
    if (btn) btn.classList.add("holding");
    if (window.AndroidBridge) window.AndroidBridge.startVoiceInput();
}
function endModalHold(e) {
    e.preventDefault();
    endModalHoldVisual();
}
function endModalHoldVisual() {
    modalVoiceHolding = false;
    var btn = document.getElementById("inputModalVoice");
    if (btn) btn.classList.remove("holding");
}

document.addEventListener("keydown", function (e) {
    if (e.key === "Enter" &&
        document.getElementById("inputModalOverlay").classList.contains("active")) {
        confirmInputModal();
    }
});

// ===================== 裁剪页 =====================
function loadVideoIntoPlayer() {
    var uri = window.AndroidBridge && window.AndroidBridge.getVideoUri
        ? window.AndroidBridge.getVideoUri() : "";
    if (!uri) { onError("no_video"); return; }

    var info = null;
    try { info = JSON.parse(window.AndroidBridge.getVideoInfo()); }
    catch (e) { console.error("getVideoInfo failed", e); }

    var videoEl = document.getElementById("trimVideo");
    if (info && info.thumbnail) videoEl.poster = info.thumbnail;

    videoEl.src = uri;
    videoEl.load();

    videoEl.onloadedmetadata = function () {
        if (info && info.duration > 0) {
            currentVideoInfo = info;
            initTrimSlider(info.duration);
            document.getElementById("trimInfo").textContent =
                formatSize(info.size) + "  ·  " +
                (info.width && info.height ? info.width + "×" + info.height : "-");
        }
        try {
            var seekTo = Math.min(0.05, (videoEl.duration || 1) / 2);
            videoEl.currentTime = seekTo;
        } catch (e) {}
    };

    videoEl.onloadeddata = function () {
        try {
            var seekTo = Math.min(0.05, (videoEl.duration || 1) / 2);
            videoEl.currentTime = seekTo;
        } catch (e) {}
    };

    videoEl.ontimeupdate = function () {
        if (isPlaying && currentVideoInfo) {
            var curMs = videoEl.currentTime * 1000;
            if (curMs >= currentTrimEnd) {
                videoEl.currentTime = currentTrimStart / 1000;
            }
        }
    };

    videoEl.onplay = function () { isPlaying = true; updatePlayIcon(true); };
    videoEl.onpause = function () { isPlaying = false; updatePlayIcon(false); };
    videoEl.onended = function () { isPlaying = false; updatePlayIcon(false); };
}

function updatePlayIcon(playing) {
    var btn = document.getElementById("playBtn");
    if (!btn) return;
    btn.classList.toggle("playing", playing);
}

function togglePlay() {
    var v = document.getElementById("trimVideo");
    if (v.paused) {
        var cur = v.currentTime * 1000;
        if (cur < currentTrimStart || cur >= currentTrimEnd) {
            v.currentTime = currentTrimStart / 1000;
        }
        v.play();
    } else {
        v.pause();
    }
}

function initTrimSlider(durationMs) {
    document.getElementById("trimStart").value = 0;
    document.getElementById("trimEnd").value = 1000;
    currentTrimStart = 0;
    currentTrimEnd = durationMs;
    updateTrimDisplay(0, 1000);
}

function onTrimChange(ev) {
    var startEl = document.getElementById("trimStart");
    var endEl = document.getElementById("trimEnd");
    var s = parseInt(startEl.value, 10);
    var e = parseInt(endEl.value, 10);
    var minGap = 30;

    if (e - s < minGap) {
        if (ev && ev.target === startEl) {
            s = Math.max(0, e - minGap);
            startEl.value = s;
        } else {
            e = Math.min(1000, s + minGap);
            endEl.value = e;
        }
    }
    updateTrimDisplay(s, e);

    if (currentVideoInfo && !isPlaying) {
        var v = document.getElementById("trimVideo");
        v.currentTime = currentVideoInfo.duration * s / 1000 / 1000;
    }
}

function updateTrimDisplay(s, e) {
    var hl = document.getElementById("trimHighlight");
    hl.style.left = (s / 10) + "%";
    hl.style.width = ((e - s) / 10) + "%";

    var dur = currentVideoInfo ? currentVideoInfo.duration : 0;
    if (dur > 0) {
        currentTrimStart = Math.round(dur * s / 1000);
        currentTrimEnd = Math.round(dur * e / 1000);
    }
    document.getElementById("trimStartLabel").textContent = formatDuration(currentTrimStart);
    document.getElementById("trimEndLabel").textContent = formatDuration(currentTrimEnd);
}

function confirmTrim() {
    if (currentTrimEnd <= currentTrimStart) {
        currentTrimEnd = currentVideoInfo ? currentVideoInfo.duration : 0;
    }
    showScreen("screen-input");
}

function backToTrim() {
    showScreen("screen-trim");
}

// ===================== 分类与提示词 =====================
function renderCategories() {
    var tabsEl = document.getElementById("categoryTabs");
    var itemsEl = document.getElementById("categoryItems");
    if (!tabsEl || !itemsEl) return;

    var categories = promptCategories[currentLang];
    if (!categories || categories.length === 0) return;
    if (currentCategoryIndex >= categories.length) currentCategoryIndex = 0;

    tabsEl.innerHTML = "";
    categories.forEach(function (cat, idx) {
        var tab = document.createElement("button");
        tab.className = "category-tab" + (idx === currentCategoryIndex ? " active" : "");
        tab.textContent = cat.label;
        tab.setAttribute("role", "tab");
        tab.setAttribute("aria-selected", idx === currentCategoryIndex ? "true" : "false");
        tab.onclick = function () {
            currentCategoryIndex = idx;
            renderCategories();
        };
        tabsEl.appendChild(tab);
    });

    itemsEl.innerHTML = "";
    categories[currentCategoryIndex].items.forEach(function (item) {
        var btn = document.createElement("button");
        btn.className = "category-item" + (item.needsInput ? " needs-input" : "");
        btn.textContent = item.label;
        btn.setAttribute("aria-label", item.needsInput
            ? item.label + "，" + (item.inputTitle || "")
            : item.label);
        btn.onclick = function () {
            if (item.needsInput) {
                openInputModal(item);
            } else {
                setPromptText(item.prompt);
            }
        };
        itemsEl.appendChild(btn);
    });
}

function setPromptText(text) {
    currentPrompt = text;
    var mainInput = document.getElementById("promptInput");
    if (mainInput) mainInput.value = text;
    updatePromptDisplay();
    updateConfirmState();
    announce(text);
}

// ===================== 输入页 =====================
function resetAll() {
    currentPrompt = "";
    var mainInput = document.getElementById("promptInput");
    if (mainInput) mainInput.value = "";
    updatePromptDisplay();
    currentVideoInfo = null;
    currentTrimStart = 0;
    currentTrimEnd = 0;
    updateConfirmState();
}

function onPromptChange() {
    var val = document.getElementById("promptInput").value.trim();
    currentPrompt = val;
    updatePromptDisplay();
    updateConfirmState();
}

function updatePromptDisplay() {
    var el = document.getElementById("currentPrompt");
    if (!el) return;
    if (currentPrompt) {
        el.textContent = currentPrompt;
        el.classList.remove("empty");
    } else {
        el.textContent = t("prompt_placeholder");
        el.classList.add("empty");
    }
}

function updateConfirmState() {
    var btn = document.getElementById("confirmBtn");
    if (!btn) return;
    var ok = currentPrompt && currentPrompt.length > 0;
    if (ok) {
        btn.classList.remove("disabled");
        btn.disabled = false;
        btn.setAttribute("aria-disabled", "false");
    } else {
        btn.classList.add("disabled");
        btn.disabled = true;
        btn.setAttribute("aria-disabled", "true");
    }
}

// ===================== 按住说话（主输入页） =====================
function startHold(e) {
    e.preventDefault();
    if (isHolding) return;
    isHolding = true;
    var btn = document.getElementById("voiceCircle");
    if (btn) btn.classList.add("holding");
    var label = document.getElementById("voiceLabel");
    if (label) label.textContent = t("hold_release");
    if (window.AndroidBridge) window.AndroidBridge.startVoiceInput();
}
function endHold(e) { e.preventDefault(); endHoldVisual(); }
function endHoldVisual() {
    isHolding = false;
    var btn = document.getElementById("voiceCircle");
    if (btn) btn.classList.remove("holding");
    var label = document.getElementById("voiceLabel");
    if (label) label.textContent = t("hold_speak");
}

// ===================== 确认提交 =====================
function confirmAndProcess() {
    if (!currentPrompt || currentPrompt.length === 0) {
        showErrorDialog("no_prompt"); return;
    }

    document.getElementById("progressFill").style.width = "0%";
    document.getElementById("thinkingText").textContent =
        t("uploading_pct").replace("{pct}", 0);
    document.getElementById("thinkingHint").textContent = t("uploading_hint");
    showScreen("screen-thinking");

    var startMs = currentTrimStart || 0;
    var endMs = currentTrimEnd || 0;
    if (window.AndroidBridge) {
        window.AndroidBridge.submit(currentPrompt, startMs, endMs);
    }
}

// ===================== 结果 =====================
function saveResult() { if (window.AndroidBridge) window.AndroidBridge.saveResult(); }
function goHome() {
    var video = document.getElementById("resultVideo");
    video.pause(); video.removeAttribute("src"); video.load();
    var trimVideo = document.getElementById("trimVideo");
    trimVideo.pause(); trimVideo.removeAttribute("src"); trimVideo.load();
    if (window.AndroidBridge) window.AndroidBridge.reset();
    resetAll();
    showScreen("screen-home");
}

// ===================== 工具 =====================
function formatDuration(ms) {
    var totalSec = Math.floor(ms / 1000);
    var h = Math.floor(totalSec / 3600);
    var m = Math.floor((totalSec % 3600) / 60);
    var s = totalSec % 60;
    if (h > 0) return h + ":" + pad2(m) + ":" + pad2(s);
    return pad2(m) + ":" + pad2(s);
}
function pad2(n) { return n < 10 ? "0" + n : "" + n; }
function formatSize(bytes) {
    if (!bytes || bytes < 0) return "-";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1024 / 1024).toFixed(2) + " MB";
}

// ===================== 初始化 =====================
document.addEventListener("DOMContentLoaded", function () {
    var saved = localStorage.getItem("lang");
    if (saved) currentLang = saved;
    else {
        var sys = (navigator.language || "zh").toLowerCase();
        currentLang = sys.startsWith("en") ? "en" : "zh";
    }
    setLang(currentLang);

    var savedMode = localStorage.getItem("userMode");
    if (savedMode) {
        applyUserMode(savedMode);
        showScreen("screen-home");
    } else {
        showScreen("screen-onboarding");
    }
});