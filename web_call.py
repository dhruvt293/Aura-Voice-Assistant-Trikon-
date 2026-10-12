import os
import time
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from stt import SpeechToText
from llm import LanguageModel
from tts import TextToSpeech

app = FastAPI(title="Aura Live Voice Call Assistant")

# Create static & temp audio directory
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "static_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Mount static audio
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

print("Initializing AI models for Live Voice Call...")
stt_model = SpeechToText()
llm_model = LanguageModel()
tts_model = TextToSpeech()
print("All AI models loaded and ready for continuous conversation.")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aura - Live Voice AI Call</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090d16;
            --surface: rgba(255, 255, 255, 0.04);
            --surface-border: rgba(255, 255, 255, 0.09);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-cyan: #38bdf8;
            --accent-purple: #a855f7;
            --accent-green: #22c55e;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Plus Jakarta Sans', sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--bg);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.12) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.08) 0%, transparent 40%);
        }

        header {
            padding: 20px 36px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--surface-border);
            backdrop-filter: blur(12px);
            background: rgba(9, 13, 22, 0.7);
            position: sticky;
            top: 0;
            z-index: 50;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            box-shadow: 0 4px 14px rgba(56, 189, 248, 0.3);
        }

        .brand-title {
            font-size: 19px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .brand-badge {
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 20px;
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-cyan);
            border: 1px solid rgba(56, 189, 248, 0.3);
        }

        .header-meta {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .pill {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 500;
            background: var(--surface);
            border: 1px solid var(--surface-border);
        }

        .pill-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--text-secondary);
        }

        .pill-dot.active {
            background: var(--accent-green);
            box-shadow: 0 0 10px var(--accent-green);
            animation: pulse-dot 1.8s infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.85); }
        }

        .main-container {
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 1.1fr;
            max-width: 1300px;
            width: 100%;
            margin: 0 auto;
            padding: 28px;
            gap: 32px;
        }

        @media (max-width: 900px) {
            .main-container {
                grid-template-columns: 1fr;
            }
        }

        /* Left Stage: Live Call Orb */
        .call-stage {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: 24px;
            padding: 40px 24px;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(16px);
        }

        .orb-wrapper {
            position: relative;
            width: 220px;
            height: 220px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 30px 0;
        }

        .orb {
            width: 140px;
            height: 140px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, #60a5fa, #2563eb 50%, #1e1b4b);
            box-shadow: 0 0 45px rgba(59, 130, 246, 0.45), inset 0 0 25px rgba(255, 255, 255, 0.3);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            z-index: 2;
        }

        .orb-halo {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 1px dashed rgba(56, 189, 248, 0.3);
            animation: spin-halo 24s linear infinite;
        }

        @keyframes spin-halo {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        /* Orb States */
        .orb.idle {
            background: radial-gradient(circle at 35% 35%, #475569, #1e293b);
            box-shadow: 0 0 20px rgba(71, 85, 105, 0.25);
            transform: scale(0.92);
        }

        .orb.listening {
            background: radial-gradient(circle at 35% 35%, #38bdf8, #0284c7 60%, #0369a1);
            box-shadow: 0 0 65px rgba(56, 189, 248, 0.65), inset 0 0 35px rgba(255, 255, 255, 0.6);
            animation: orb-breathe 1.8s infinite ease-in-out;
        }

        .orb.thinking {
            background: radial-gradient(circle at 35% 35%, #fbbf24, #d97706 60%, #78350f);
            box-shadow: 0 0 60px rgba(245, 158, 11, 0.6);
            animation: orb-pulse-fast 0.8s infinite alternate ease-in-out;
        }

        .orb.speaking {
            background: radial-gradient(circle at 35% 35%, #c084fc, #9333ea 55%, #4c1d95);
            box-shadow: 0 0 75px rgba(168, 85, 247, 0.7), inset 0 0 35px rgba(255, 255, 255, 0.5);
            animation: orb-speaking-wave 1.1s infinite alternate cubic-bezier(0.45, 0.05, 0.55, 0.95);
        }

        @keyframes orb-breathe {
            0%, 100% { transform: scale(1); filter: brightness(1); }
            50% { transform: scale(1.08); filter: brightness(1.2); }
        }

        @keyframes orb-pulse-fast {
            0% { transform: scale(0.95) rotate(0deg); }
            100% { transform: scale(1.05) rotate(180deg); }
        }

        @keyframes orb-speaking-wave {
            0% { transform: scale(1) scaleY(0.96); }
            50% { transform: scale(1.12) scaleX(1.04); }
            100% { transform: scale(1.04) scaleY(1.06); }
        }

        .status-heading {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 6px;
            letter-spacing: -0.02em;
        }

        .status-sub {
            font-size: 14px;
            color: var(--text-secondary);
            text-align: center;
            max-width: 320px;
            line-height: 1.5;
            min-height: 42px;
        }

        /* Controls */
        .call-controls {
            display: flex;
            gap: 16px;
            margin-top: 32px;
            align-items: center;
        }

        .btn-call {
            padding: 14px 34px;
            border-radius: 40px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.25s ease;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
        }

        .btn-start {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            box-shadow: 0 6px 22px rgba(16, 185, 129, 0.35);
        }

        .btn-start:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 28px rgba(16, 185, 129, 0.5);
        }

        .btn-end {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            box-shadow: 0 6px 22px rgba(239, 68, 68, 0.35);
        }

        .btn-end:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 28px rgba(239, 68, 68, 0.5);
        }

        .btn-secondary {
            background: var(--surface);
            border: 1px solid var(--surface-border);
            color: var(--text-secondary);
            padding: 14px 20px;
            border-radius: 40px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-secondary:hover {
            color: var(--text-primary);
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* Right Stage: Live Transcript */
        .transcript-stage {
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: 24px;
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(16px);
            height: 600px;
            overflow: hidden;
        }

        .stage-header {
            padding: 18px 24px;
            border-bottom: 1px solid var(--surface-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .stage-title {
            font-size: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .clear-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 12px;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 6px;
        }

        .clear-btn:hover {
            color: var(--text-primary);
        }

        .messages-container {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
            scroll-behavior: smooth;
        }

        .message-bubble {
            max-width: 85%;
            padding: 14px 18px;
            border-radius: 18px;
            font-size: 14.5px;
            line-height: 1.5;
            animation: message-pop 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes message-pop {
            from { opacity: 0; transform: translateY(8px) scale(0.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        .user-bubble {
            align-self: flex-end;
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(37, 99, 235, 0.25));
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-bottom-right-radius: 4px;
            color: #e0f2fe;
        }

        .assistant-bubble {
            align-self: flex-start;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--surface-border);
            border-bottom-left-radius: 4px;
            color: var(--text-primary);
        }

        .msg-meta {
            font-size: 11px;
            margin-bottom: 5px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .user-bubble .msg-meta { color: var(--accent-cyan); }
        .assistant-bubble .msg-meta { color: var(--accent-purple); }

        .latency-badge {
            margin-top: 8px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 12px;
            background: rgba(34, 197, 94, 0.12);
            color: #4ade80;
            border: 1px solid rgba(34, 197, 94, 0.25);
            font-weight: 500;
        }

        .lang-tag {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.1);
            text-transform: uppercase;
        }

        /* Benchmark Footer Bar */
        .metrics-bar {
            padding: 14px 24px;
            background: rgba(0, 0, 0, 0.25);
            border-top: 1px solid var(--surface-border);
            display: flex;
            justify-content: space-around;
            align-items: center;
            font-size: 12px;
            color: var(--text-secondary);
        }

        .metric-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
        .lang-toggle-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 12px;
            font-weight: 600;
            padding: 5px 12px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .lang-toggle-btn:hover {
            color: var(--text-primary);
        }
        .lang-toggle-btn.active {
            background: rgba(56, 189, 248, 0.25);
            color: var(--accent-cyan);
            border: 1px solid rgba(56, 189, 248, 0.4);
        }
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-icon">🎙️</div>
            <div>
                <span class="brand-title">Aura</span>
                <span class="brand-badge">LIVE VOICE AI</span>
            </div>
        </div>
        <div class="header-meta">
            <div class="pill">
                <span class="pill-dot" id="callStatusDot"></span>
                <span id="callStatusText">Standby</span>
            </div>
            <div class="pill" style="padding: 4px 6px; gap: 4px;">
                <button class="lang-toggle-btn active" id="btnAuto" onclick="setLanguage('auto')">🌐 Auto</button>
                <button class="lang-toggle-btn" id="btnEn" onclick="setLanguage('en')">🇬🇧 English</button>
                <button class="lang-toggle-btn" id="btnHi" onclick="setLanguage('hi')">🇮🇳 Hindi</button>
            </div>
        </div>
    </header>

    <div class="main-container">
        <!-- Left: Interactive Voice Call Stage -->
        <div class="call-stage">
            <div class="orb-wrapper">
                <div class="orb-halo"></div>
                <div class="orb idle" id="voiceOrb"></div>
            </div>

            <h2 class="status-heading" id="mainStatusHeading">Start Conversation</h2>
            <p class="status-sub" id="mainStatusSub">Click below to connect the live call. You can speak naturally in English or Hindi without pressing any buttons.</p>

            <div class="call-controls">
                <button class="btn-call btn-start" id="callToggleBtn" onclick="toggleCall()">
                    <span id="callBtnIcon">📞</span>
                    <span id="callBtnText">Start Live Call</span>
                </button>
                <button class="btn-secondary" id="doneBtn" style="display: none; background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.5); font-weight: 600;" onclick="triggerTurnSubmission()">
                    <span>Done Speaking ➔</span>
                </button>
            </div>
        </div>

        <!-- Right: Real-time Transcript Feed -->
        <div class="transcript-stage">
            <div class="stage-header">
                <div class="stage-title">
                    <span>💬 Live Call Transcript</span>
                </div>
                <button class="clear-btn" onclick="clearTranscript()">Clear</button>
            </div>

            <div class="messages-container" id="messagesContainer">
                <div class="message-bubble assistant-bubble">
                    <div class="msg-meta">🤖 Aura</div>
                    <div>Hello! Click <strong>Start Live Call</strong> to begin talking with me hands-free. I support both English and Hindi seamlessly.</div>
                </div>
            </div>

            <div class="metrics-bar">
                <div class="metric-item">
                    <span>STT Latency</span>
                    <span class="metric-val" id="metricSTT">-- ms</span>
                </div>
                <div class="metric-item">
                    <span>LLM Latency</span>
                    <span class="metric-val" id="metricLLM">-- ms</span>
                </div>
                <div class="metric-item">
                    <span>TTS Latency</span>
                    <span class="metric-val" id="metricTTS">-- ms</span>
                </div>
                <div class="metric-item">
                    <span>Total Turnaround</span>
                    <span class="metric-val" id="metricTotal" style="color: var(--accent-green);">-- ms</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        let isCallActive = false;
        let audioContext = null;
        let mediaStream = null;
        let analyser = null;
        let mediaRecorder = null;
        let audioChunks = [];
        let isUserSpeaking = false;
        let silenceTimer = null;
        let speechStartTimestamp = 0;
        let checkAudioInterval = null;
        let currentAudioPlayer = null;
        let currentLanguageMode = 'auto';

        const orb = document.getElementById('voiceOrb');
        const mainHeading = document.getElementById('mainStatusHeading');
        const mainSub = document.getElementById('mainStatusSub');
        const callBtn = document.getElementById('callToggleBtn');
        const callBtnText = document.getElementById('callBtnText');
        const callBtnIcon = document.getElementById('callBtnIcon');
        const statusDot = document.getElementById('callStatusDot');
        const statusText = document.getElementById('callStatusText');
        const doneBtn = document.getElementById('doneBtn');
        const messagesContainer = document.getElementById('messagesContainer');

        function setLanguage(lang) {
            currentLanguageMode = lang;
            document.querySelectorAll('.lang-toggle-btn').forEach(b => b.classList.remove('active'));
            if (lang === 'auto') document.getElementById('btnAuto').classList.add('active');
            if (lang === 'en') document.getElementById('btnEn').classList.add('active');
            if (lang === 'hi') document.getElementById('btnHi').classList.add('active');
        }

        async function toggleCall() {
            if (!isCallActive) {
                await startLiveCall();
            } else {
                stopLiveCall();
            }
        }

        async function startLiveCall() {
            try {
                mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioContext.createMediaStreamSource(mediaStream);
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 512;
                source.connect(analyser);

                isCallActive = true;
                callBtn.classList.remove('btn-start');
                callBtn.classList.add('btn-end');
                callBtnText.innerText = 'End Call';
                callBtnIcon.innerText = '🛑';
                statusDot.classList.add('active');
                statusText.innerText = 'Live Call Active';

                setOrbState('listening', 'Listening...', 'Speak naturally in English or Hindi. I am listening.');
                startListeningLoop();

            } catch (err) {
                alert('Microphone access denied: ' + err.message);
                console.error(err);
            }
        }

        function stopLiveCall() {
            isCallActive = false;
            if (silenceTimer) clearTimeout(silenceTimer);
            if (checkAudioInterval) clearInterval(checkAudioInterval);
            if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
            if (mediaStream) mediaStream.getTracks().forEach(track => track.stop());
            if (audioContext) audioContext.close();
            if (currentAudioPlayer) currentAudioPlayer.pause();

            callBtn.classList.remove('btn-end');
            callBtn.classList.add('btn-start');
            callBtnText.innerText = 'Start Live Call';
            callBtnIcon.innerText = '📞';
            statusDot.classList.remove('active');
            statusText.innerText = 'Standby';
            if (doneBtn) doneBtn.style.display = 'none';

            setOrbState('idle', 'Call Ended', 'Click Start Live Call to reconnect.');
        }

        function setOrbState(state, heading, sub) {
            orb.className = 'orb ' + state;
            mainHeading.innerText = heading;
            mainSub.innerText = sub;
        }

        async function startListeningLoop() {
            if (!isCallActive) return;

            // Ensure AudioContext is actively running
            try {
                if (audioContext && audioContext.state === 'suspended') {
                    await audioContext.resume();
                }
            } catch (e) {
                console.warn('AudioContext resume error:', e);
            }

            audioChunks = [];
            isUserSpeaking = false;
            if (silenceTimer) clearTimeout(silenceTimer);
            silenceTimer = null;
            speechStartTimestamp = 0;

            const mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/wav';
            try {
                if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                    mediaRecorder.stop();
                }
                mediaRecorder = new MediaRecorder(mediaStream, { mimeType: mimeType });
            } catch (e) {
                console.error('MediaRecorder error:', e);
            }

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    audioChunks.push(e.data);
                }
            };

            mediaRecorder.onstop = async () => {
                if (audioChunks.length > 0 && isCallActive) {
                    const audioBlob = new Blob(audioChunks, { type: mimeType });
                    await processUserSpeech(audioBlob);
                } else if (isCallActive) {
                    startListeningLoop();
                }
            };

            mediaRecorder.start(100);
            setOrbState('listening', 'Listening...', 'Aura is listening. Speak your question anytime.');
            if (doneBtn) doneBtn.style.display = 'none';

            // Real-time Voice Activity Detection (VAD)
            const dataArray = new Uint8Array(analyser.frequencyBinCount);
            if (checkAudioInterval) clearInterval(checkAudioInterval);

            let baselineNoise = 0.015;

            checkAudioInterval = setInterval(() => {
                if (!isCallActive || orb.classList.contains('speaking') || orb.classList.contains('thinking')) return;

                analyser.getByteTimeDomainData(dataArray);
                let sumSquares = 0.0;
                for (let i = 0; i < dataArray.length; i++) {
                    let norm = (dataArray[i] - 128) / 128;
                    sumSquares += norm * norm;
                }
                let rms = Math.sqrt(sumSquares / dataArray.length);

                // Pulse the orb with real-time volume
                if (orb.classList.contains('listening')) {
                    const scale = 1.0 + Math.min(rms * 4.0, 0.45);
                    orb.style.transform = `scale(${scale.toFixed(3)})`;
                }

                const now = Date.now();

                // If user is not yet speaking, update the background noise floor
                if (!isUserSpeaking) {
                    baselineNoise = baselineNoise * 0.95 + rms * 0.05;
                }

                const voiceThreshold = Math.max(baselineNoise * 1.8 + 0.015, 0.028);

                // Detect when user speaks
                if (rms > voiceThreshold) {
                    if (!isUserSpeaking) {
                        isUserSpeaking = true;
                        speechStartTimestamp = now;
                        setOrbState('listening', 'Hearing You...', 'Listening to your question...');
                        if (doneBtn) doneBtn.style.display = 'inline-flex';
                    }
                    // Reset silence timer while voice is active
                    if (silenceTimer) {
                        clearTimeout(silenceTimer);
                        silenceTimer = null;
                    }
                } else if (isUserSpeaking) {
                    // Start silence timer once user stops talking
                    if (!silenceTimer) {
                        silenceTimer = setTimeout(() => {
                            // User paused for 500ms after speaking - finish turn!
                            triggerTurnSubmission();
                        }, 500);
                    }
                }

                // Hard safety limit: max 6 seconds per utterance so it NEVER freezes
                if (isUserSpeaking && (now - speechStartTimestamp > 6000)) {
                    triggerTurnSubmission();
                }
            }, 35);
        }

        function triggerTurnSubmission() {
            if (!isCallActive || !isUserSpeaking) return;
            isUserSpeaking = false;
            if (silenceTimer) clearTimeout(silenceTimer);
            if (checkAudioInterval) clearInterval(checkAudioInterval);
            if (doneBtn) doneBtn.style.display = 'none';
            orb.style.transform = 'scale(1)';
            setOrbState('thinking', 'Thinking...', 'Aura is generating your answer...');
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
        }

        // Tap the orb or press Spacebar to force turn submission instantly
        orb.onclick = () => {
            if (isCallActive && isUserSpeaking) {
                triggerTurnSubmission();
            }
        };

        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && isCallActive && isUserSpeaking) {
                e.preventDefault();
                triggerTurnSubmission();
            }
        });

        async function processUserSpeech(audioBlob) {
            try {
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.webm');
                formData.append('language_hint', currentLanguageMode);

                const response = await fetch('/api/interact', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error('Server error');
                const data = await response.json();

                if (data.status === 'success') {
                    // Append User Message
                    appendMessage('user', data.user_text, data.language);

                    // Update Metrics
                    document.getElementById('metricSTT').innerText = Math.round(data.metrics.stt * 1000) + ' ms';
                    document.getElementById('metricLLM').innerText = Math.round(data.metrics.llm * 1000) + ' ms';
                    document.getElementById('metricTTS').innerText = Math.round(data.metrics.tts * 1000) + ' ms';
                    document.getElementById('metricTotal').innerText = Math.round(data.metrics.total * 1000) + ' ms';

                    // Append Assistant Message
                    appendMessage('assistant', data.ai_reply, data.language, data.metrics.total);

                    // Play Assistant Voice Response
                    await playAssistantVoice(data.audio_url);
                } else {
                    // Empty speech / unrecognized
                    startListeningLoop();
                }

            } catch (err) {
                console.error(err);
                if (isCallActive) startListeningLoop();
            }
        }

        async function playAssistantVoice(audioUrl) {
            if (!isCallActive) return;

            setOrbState('speaking', 'Speaking...', 'Aura is answering out loud.');
            if (currentAudioPlayer) {
                currentAudioPlayer.pause();
                currentAudioPlayer = null;
            }

            currentAudioPlayer = new Audio(audioUrl + '?t=' + Date.now());
            
            try {
                await currentAudioPlayer.play();
            } catch (e) {
                console.warn('Playback error:', e);
                startListeningLoop();
                return;
            }

            // Continuous transition: when voice ends, resume listening!
            currentAudioPlayer.onended = async () => {
                if (isCallActive) {
                    if (audioContext && audioContext.state === 'suspended') {
                        await audioContext.resume();
                    }
                    setTimeout(() => {
                        if (isCallActive) startListeningLoop();
                    }, 150);
                }
            };

            currentAudioPlayer.onerror = () => {
                if (isCallActive) startListeningLoop();
            };
        }

        function appendMessage(sender, text, lang, latencyTotal = null) {
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble ' + (sender === 'user' ? 'user-bubble' : 'assistant-bubble');

            const meta = document.createElement('div');
            meta.className = 'msg-meta';
            const langLabel = lang ? `<span class="lang-tag">${lang.toUpperCase()}</span>` : '';
            meta.innerHTML = sender === 'user' ? `👤 You ${langLabel}` : `🤖 Aura ${langLabel}`;
            bubble.appendChild(meta);

            const content = document.createElement('div');
            content.innerText = text;
            bubble.appendChild(content);

            if (latencyTotal !== null) {
                const latencyBadge = document.createElement('div');
                latencyBadge.className = 'latency-badge';
                latencyBadge.innerHTML = `⚡ Turn Latency: ${(latencyTotal).toFixed(2)}s`;
                bubble.appendChild(latencyBadge);
            }

            messagesContainer.appendChild(bubble);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function clearTranscript() {
            messagesContainer.innerHTML = '';
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    return HTMLResponse(content=HTML_CONTENT)

@app.post("/api/interact")
async def interact(
    audio_file: UploadFile = File(...),
    language_hint: str = Form("auto")
):
    """
    Continuous Live Call Endpoint:
    Processes user audio chunk through Faster-Whisper STT -> Qwen LLM -> Piper TTS.
    Returns transcript, AI reply, detected language, output audio URL, and granular latency metrics.
    """
    t_start_total = time.time()
    
    # Save uploaded audio chunk to temporary file
    temp_input = os.path.join(AUDIO_DIR, f"input_{uuid.uuid4().hex[:8]}.webm")
    try:
        content = await audio_file.read()
        with open(temp_input, "wb") as f:
            f.write(content)
            
        # 1. Speech-to-Text (STT) with language hint (Auto / English / Hindi)
        user_text, detected_lang, stt_latency = stt_model.transcribe(temp_input, language_hint=language_hint)
        
        if not user_text.strip():
            return JSONResponse({"status": "no_speech"})
            
        # 2. Language Model (LLM)
        ai_reply, llm_latency = llm_model.chat(user_text, language=detected_lang)
        
        # 3. Text-to-Speech (TTS)
        output_filename = f"response_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join(AUDIO_DIR, output_filename)
        _, tts_latency = tts_model.speak(ai_reply, language=detected_lang, output_file=output_path)
        
        total_latency = round(time.time() - t_start_total, 3)
        
        return JSONResponse({
            "status": "success",
            "user_text": user_text,
            "ai_reply": ai_reply,
            "language": detected_lang,
            "audio_url": f"/audio/{output_filename}",
            "metrics": {
                "stt": stt_latency,
                "llm": llm_latency,
                "tts": tts_latency,
                "total": total_latency
            }
        })
        
    except Exception as e:
        print(f"Error in live interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup input audio
        if os.path.exists(temp_input):
            try:
                os.remove(temp_input)
            except Exception:
                pass

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
