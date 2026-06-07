# 🎙️ AI Voice Studio — Advanced v2.0

A production-grade Streamlit app for voice synthesis, speech recognition,
translation, document-to-speech, and AI script generation.

---

## ✨ What's New in v2.0

| Feature | v1 (Original) | v2 (This Version) |
|---|---|---|
| TTS languages | Basic | 50+ via gTTS |
| Speed control | ❌ | ✅ 0.5× – 2.0× (pydub) |
| Waveform visualization | ❌ | ✅ Gradient waveform |
| AI text enhancement | ❌ | ✅ 6 modes (Claude) |
| STT post-processing | ❌ | ✅ Translate/Summarize/Meeting notes |
| Translation modes | Basic | Bulk mode + auto-detect |
| Document pipeline | ❌ | ✅ PDF/DOCX/TXT → TTS with AI summary |
| AI Script Writer | ❌ | ✅ 12 templates + live AI chat |
| Audio Library | ❌ | ✅ Session history with replay & download |
| UI Design | Basic | Dark glassmorphism (Syne + DM Sans) |
| Session state | Minimal | Full per-session persistence |

---

## 🚀 Quick Start

### 1. Clone & install
```bash
git clone <your-repo>
cd ai-voice-studio
pip install -r requirements.txt
```

### 2. Set your API key
Either add it in the sidebar at runtime, **or** set an environment variable:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

For Streamlit Cloud, add it to **Secrets**:
```toml
# .streamlit/secrets.toml
ANTHROPIC_API_KEY = "sk-ant-..."
```
Then read it in `app.py` via `os.getenv("ANTHROPIC_API_KEY", "")` — already done ✅

### 3. Install FFmpeg (required for pydub)
- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/download.html and add to PATH

### 4. Run
```bash
streamlit run app.py
```

---

## 📦 Features

### 🔊 TTS Studio
- 50+ languages via gTTS
- Speed control (0.5× – 2.0×) via pydub speedup
- Optional pre-translation to any target language
- AI text enhancement (Improve Clarity, Formal, Casual, Summarize…)
- Language auto-detection
- Live waveform visualization
- One-click MP3 download

### 🎤 Speech-to-Text
- Upload WAV / MP3 / OGG / FLAC / M4A
- 16+ recognition language locales
- Post-processing: Translate to English, Summarize, Key Points, Meeting Notes
- Read transcript aloud via TTS
- Export transcript as TXT

### 🌐 Translation Hub
- 20+ language pairs via Google Translate
- Auto-detect source language
- Bulk/line-by-line mode
- Instant audio playback of translated text
- Export to TXT

### 📄 Document Studio
- Ingest PDF, DOCX, or plain TXT
- Optional AI summarization before reading
- Optional translation pipeline
- Adjustable playback speed
- Audio download

### 🤖 AI Script Writer
- 12 quick-generate templates (Podcast, YouTube, Ad, Lecture, Meditation…)
- Configurable tone, audience, and duration
- One-click "Speak It" after generation
- Full live AI chat assistant (Claude claude-sonnet-4-20250514)
- Send scripts directly to TTS Studio

### 📚 Audio Library
- Auto-saves every generated audio this session (up to 25)
- Replay without regenerating
- Download any item as MP3
- Re-send to TTS Studio for tweaks

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Optional* | Enables AI features (Script Writer, Enhance, Summarize) |

*App fully works for TTS/STT/Translation without an API key.

---

## 🗂️ Project Structure

```
ai-voice-studio/
├── app.py              ← Main Streamlit application
├── requirements.txt    ← Python dependencies
└── README.md
```

---

## 🐛 Known Issues / Notes

- **FFmpeg warning**: pydub warns if ffmpeg is not in PATH. For Streamlit Cloud, add
  `packages.txt` with `ffmpeg` to auto-install the system package.
- **Speed < 0.75**: gTTS `slow=True` mode is used; pydub slowdown is not applied to avoid
  quality degradation.
- **Long documents**: Only the first 3,000 characters are synthesized per run to keep
  response times reasonable. Increase the `limit` variable in `tab_documents()` as needed.
- **Google STT**: Requires internet access and uses Google's free speech recognition tier
  (limited to ~1 minute of audio per request).
