# ============================================================
#  AI Voice Studio — Advanced v2.0
# ============================================================
#  Features
#  ─────────────────────────────────────────────────────────
#  🔊  TTS Studio        — 50+ languages, speed control,
#                          waveform preview, AI text-enhance
#  🎤  Speech-to-Text    — file upload, language select,
#                          post-process (translate/summarize)
#  🌐  Translation Hub   — 20 language pairs, auto-detect,
#                          instant TTS of translation
#  📄  Document Studio   — PDF/DOCX/TXT → speech pipeline
#                          with optional AI summarisation
#  🤖  AI Script Writer  — quick-gen templates + live chat
#                          (Claude claude-sonnet-4-20250514)
#  📚  Audio Library     — per-session history, replay,
#                          download, and re-send to TTS
# ============================================================

import streamlit as st
import os, io, time, base64, tempfile
from pathlib import Path
from datetime import datetime

# ── TTS / Audio ─────────────────────────────────────────────
from gtts import gTTS
from gtts.lang import tts_langs
from pydub import AudioSegment
from pydub.effects import speedup

# ── STT ─────────────────────────────────────────────────────
import speech_recognition as sr

# ── Language / Translation ───────────────────────────────────
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 42

# ── Document Parsing ─────────────────────────────────────────
import pypdf
from docx import Document as DocxDocument

# ── AI (Anthropic Claude) ────────────────────────────────────
import anthropic

# ── Viz ──────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Voice Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS — deep-space glassmorphism
# ─────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:          #07091a;
  --bg2:         #0d1030;
  --glass:       rgba(255,255,255,0.055);
  --glass-hi:    rgba(255,255,255,0.10);
  --border:      rgba(255,255,255,0.11);
  --accent:      #6c47ff;
  --accent2:     #bc5cf7;
  --accent3:     #3dd6f5;
  --text:        #eef0ff;
  --muted:       #7a80a8;
  --success:     #22d3a2;
  --warn:        #fbbf24;
  --error:       #f87171;
  --radius:      14px;
  --glow:        0 0 40px rgba(108,71,255,0.25);
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text) !important;
}

[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed; inset: 0; z-index: -1;
  background:
    radial-gradient(ellipse 80% 60% at 20% -10%, rgba(108,71,255,0.18) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 85% 90%,  rgba(61,214,245,0.10) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 50% 50%,  rgba(188,92,247,0.07) 0%, transparent 70%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: rgba(7,9,26,0.97) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarContent"] { padding: 1.5rem 1rem !important; }

/* ── Typography ── */
h1, h2, h3, .big-title {
  font-family: 'Syne', sans-serif !important;
}
h1 {
  background: linear-gradient(120deg, #fff 30%, var(--accent2) 70%, var(--accent3) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.4rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.04em !important;
  line-height: 1.1 !important;
}
h2 { font-size: 1.35rem !important; font-weight: 700 !important; color: var(--text) !important; }
h3 { font-size: 1.1rem  !important; font-weight: 600 !important; color: var(--text) !important; }

/* ── Glass Card ── */
.glass-card {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  margin-bottom: .9rem;
  transition: background .2s, box-shadow .2s;
}
.glass-card:hover { background: var(--glass-hi); box-shadow: var(--glow); }

/* ── Pill badge ── */
.pill {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 99px;
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .03em;
}
.pill-accent  { background: rgba(108,71,255,.2); color: #b8a8ff; border: 1px solid rgba(108,71,255,.3); }
.pill-success { background: rgba(34,211,162,.15); color: #6effd8; border: 1px solid rgba(34,211,162,.25); }
.pill-warn    { background: rgba(251,191,36,.12); color: #fdd97c; border: 1px solid rgba(251,191,36,.2); }

/* ── Section header ── */
.section-header {
  display: flex; align-items: center; gap: .5rem;
  font-family: 'Syne', sans-serif;
  font-size: 1.15rem; font-weight: 700;
  margin-bottom: 1rem;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 600 !important;
  font-size: .9rem !important;
  padding: .55rem 1.3rem !important;
  transition: all .2s !important;
  letter-spacing: .01em !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 28px rgba(108,71,255,.5) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Inputs ── */
.stTextArea textarea,
.stTextInput input,
.stNumberInput input {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: border-color .2s !important;
}
.stTextArea textarea:focus,
.stTextInput input:focus { border-color: var(--accent) !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}

/* ── Slider ── */
.stSlider [data-baseweb="slider"] [role="slider"] {
  background: var(--accent) !important;
  border-color: var(--accent2) !important;
}
.stSlider [data-baseweb="slider"] [data-testid="stSliderTrack"] > div:first-child {
  background: rgba(255,255,255,.1) !important;
}
.stSlider [data-baseweb="slider"] [data-testid="stSliderTrack"] > div:last-child {
  background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.04) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  gap: 3px !important;
  border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 9px !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 600 !important;
  font-size: .85rem !important;
  color: var(--muted) !important;
  padding: .45rem 1rem !important;
  transition: all .15s !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(108,71,255,.4) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: .9rem 1rem !important;
}
[data-testid="metric-container"] label {
  color: var(--muted) !important;
  font-size: .78rem !important;
  font-weight: 500 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: var(--text) !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
}

/* ── Alerts ── */
.stAlert {
  background: var(--glass) !important;
  border-radius: 10px !important;
  border-left: 3px solid var(--accent) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 600 !important;
}
.streamlit-expanderContent {
  background: rgba(255,255,255,0.02) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 10px 10px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] > div {
  background: var(--glass) !important;
  border: 2px dashed var(--border) !important;
  border-radius: 12px !important;
  transition: border-color .2s !important;
}
[data-testid="stFileUploader"] > div:hover {
  border-color: var(--accent) !important;
}

/* ── Audio player ── */
audio {
  width: 100%;
  border-radius: 10px;
  margin-top: 6px;
  filter: invert(1) hue-rotate(180deg) brightness(.85);
}

/* ── Progress ── */
.stProgress > div > div { background: var(--accent) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(108,71,255,.4); border-radius: 99px; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }

/* ── Waveform container ── */
.waveform-container {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: .5rem;
  margin-top: .5rem;
}
</style>
"""


# ─────────────────────────────────────────────────────────────
#  LANGUAGE DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def get_tts_language_map() -> dict[str, str]:
    """Returns {display_name: gtts_code}."""
    raw = tts_langs()                      # {code: name}
    return {v: k for k, v in raw.items()}


TRANS_LANGS: dict[str, str] = {
    "English": "en",       "Urdu": "ur",         "Arabic": "ar",
    "French": "fr",        "German": "de",        "Spanish": "es",
    "Chinese (Simplified)": "zh-CN",              "Hindi": "hi",
    "Turkish": "tr",       "Russian": "ru",       "Japanese": "ja",
    "Korean": "ko",        "Italian": "it",       "Portuguese": "pt",
    "Dutch": "nl",         "Polish": "pl",        "Swedish": "sv",
    "Norwegian": "no",     "Danish": "da",        "Finnish": "fi",
}

STT_LANGS: dict[str, str] = {
    "English (US)": "en-US",     "English (UK)": "en-GB",
    "Urdu": "ur-PK",             "Arabic": "ar-SA",
    "French": "fr-FR",           "German": "de-DE",
    "Spanish": "es-ES",          "Hindi": "hi-IN",
    "Chinese": "zh-CN",          "Japanese": "ja-JP",
    "Korean": "ko-KR",           "Portuguese": "pt-BR",
    "Russian": "ru-RU",          "Turkish": "tr-TR",
    "Italian": "it-IT",          "Dutch": "nl-NL",
}


# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
def init_session():
    defaults: dict = {
        "audio_history":      [],   # [{name,text,lang,b64,ts}]
        "transcript_history": [],   # [{name,text,ts}]
        "last_audio_b64":     None,
        "last_transcript":    "",
        "ai_chat":            [],   # [{role,content}]
        "quick_script":       "",
        "anthropic_key":      os.getenv("ANTHROPIC_API_KEY", ""),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────
#  CORE UTILITIES
# ─────────────────────────────────────────────────────────────
def audio_to_b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode()

def b64_to_bytes(b64: str) -> bytes:
    return base64.b64decode(b64)

def audio_player_html(b64: str, autoplay: bool = True) -> str:
    ap = "autoplay" if autoplay else ""
    return (
        f'<audio controls {ap} style="width:100%;border-radius:10px;margin-top:8px;">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    )

def save_audio_history(text: str, b64: str, lang: str, filename: str):
    st.session_state.audio_history.insert(0, {
        "name":  filename,
        "text":  (text[:80] + "…") if len(text) > 80 else text,
        "lang":  lang,
        "b64":   b64,
        "ts":    datetime.now().strftime("%H:%M:%S"),
    })
    st.session_state.audio_history = st.session_state.audio_history[:25]

def chunk_text(text: str, max_chars: int = 490) -> list[str]:
    """Split at sentence boundaries for gTTS chunking."""
    sentences = text.replace("\n", " ").split(". ")
    chunks, cur = [], ""
    for s in sentences:
        if len(cur) + len(s) + 2 < max_chars:
            cur += s + ". "
        else:
            if cur.strip():
                chunks.append(cur.strip())
            cur = s + ". "
    if cur.strip():
        chunks.append(cur.strip())
    return chunks or [text]

def synthesize_speech(text: str, lang_code: str, speed: float = 1.0) -> bytes:
    """gTTS → pydub speed-change → MP3 bytes."""
    chunks   = chunk_text(text)
    combined = AudioSegment.empty()
    for chunk in chunks:
        buf = io.BytesIO()
        gTTS(text=chunk, lang=lang_code, slow=(speed <= 0.75)).write_to_fp(buf)
        buf.seek(0)
        seg = AudioSegment.from_mp3(buf)
        if speed > 1.05:
            seg = speedup(seg, playback_speed=speed)
        combined += seg
    out = io.BytesIO()
    combined.export(out, format="mp3")
    return out.getvalue()

def transcribe_audio(audio_file, lang_code: str = "en-US") -> str:
    recognizer = sr.Recognizer()
    suffix = Path(audio_file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_file.read())
        tmp_path = tmp.name
    wav_path = tmp_path.replace(suffix, ".wav")
    try:
        AudioSegment.from_file(tmp_path).export(wav_path, format="wav")
        with sr.AudioFile(wav_path) as src:
            audio = recognizer.record(src)
        return recognizer.recognize_google(audio, language=lang_code)
    finally:
        for p in [tmp_path, wav_path]:
            try:
                os.remove(p)
            except OSError:
                pass

def pdf_to_text(f) -> str:
    reader = pypdf.PdfReader(f)
    return "\n".join(p.extract_text() or "" for p in reader.pages)

def docx_to_text(f) -> str:
    doc = DocxDocument(f)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def draw_waveform(audio_bytes: bytes) -> plt.Figure:
    buf = io.BytesIO(audio_bytes)
    seg = AudioSegment.from_mp3(buf).set_channels(1)
    samples = np.array(seg.get_array_of_samples(), dtype=np.float32)
    mx = np.abs(samples).max()
    if mx > 0:
        samples /= mx
    n = min(len(samples), 5000)
    idx = np.linspace(0, len(samples) - 1, n, dtype=int)
    s   = samples[idx]
    t   = np.linspace(0, len(s) / seg.frame_rate, len(s))

    fig, ax = plt.subplots(figsize=(9, 1.8))
    fig.patch.set_facecolor("#07091a")
    ax.set_facecolor("#07091a")

    # Gradient fill via multiple alpha layers
    ax.fill_between(t,  s,  0, alpha=0.65,
                    color="#6c47ff", linewidth=0)
    ax.fill_between(t, -s,  0, alpha=0.45,
                    color="#bc5cf7", linewidth=0)
    ax.plot(t, s,  linewidth=0.6, color="#b8a8ff", alpha=0.8)
    ax.plot(t, -s, linewidth=0.6, color="#e0b8ff", alpha=0.5)

    ax.axhline(0, color="rgba(255,255,255,0.08)", linewidth=0.5)
    ax.set_xlim(0, t[-1])
    ax.set_ylim(-1.15, 1.15)
    ax.axis("off")
    plt.tight_layout(pad=0)
    return fig

def get_claude_client() -> "anthropic.Anthropic | None":
    key = st.session_state.get("anthropic_key", "").strip()
    return anthropic.Anthropic(api_key=key) if key else None

def claude_run(client, user_prompt: str, system: str, max_tokens: int = 1500) -> str:
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return resp.content[0].text


# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(
            "<div style='font-family:Syne,sans-serif;font-size:1.3rem;"
            "font-weight:800;background:linear-gradient(120deg,#fff,#bc5cf7);"
            "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
            "margin-bottom:.25rem'>🎙️ AI Voice Studio</div>"
            "<div style='color:#7a80a8;font-size:.78rem;margin-bottom:1.2rem'>"
            "v2.0 · Advanced Edition</div>",
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown(
            "<div style='font-family:Syne;font-weight:700;font-size:.85rem;"
            "color:#b8a8ff;text-transform:uppercase;letter-spacing:.07em;"
            "margin-bottom:.5rem'>🔑 AI Settings</div>",
            unsafe_allow_html=True
        )
        key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=st.session_state.anthropic_key,
            help="Required for AI Enhance, Script Writer, and AI Summarize features.",
            placeholder="sk-ant-…",
        )
        if key:
            st.session_state.anthropic_key = key
        if key:
            st.markdown(
                "<span class='pill pill-success'>✓ Key saved</span>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<span class='pill pill-warn'>⚠ No key — AI features off</span>",
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown(
            "<div style='font-family:Syne;font-weight:700;font-size:.85rem;"
            "color:#b8a8ff;text-transform:uppercase;letter-spacing:.07em;"
            "margin-bottom:.7rem'>📊 Session Stats</div>",
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        c1.metric("🔊 Audios",      len(st.session_state.audio_history))
        c2.metric("📝 Transcripts", len(st.session_state.transcript_history))

        total_chars = sum(len(i["text"]) for i in st.session_state.audio_history)
        st.caption(f"~{total_chars:,} total characters synthesised")

        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.audio_history      = []
            st.session_state.transcript_history = []
            st.session_state.ai_chat            = []
            st.success("History cleared!")

        st.markdown("---")
        st.markdown(
            "<div style='color:#3d4060;font-size:.72rem;text-align:center'>"
            "Powered by Claude, gTTS & Google Translate"
            "</div>",
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────────────────────
#  TAB 1 — TTS STUDIO
# ─────────────────────────────────────────────────────────────
def tab_tts():
    st.markdown("### 🔊 Text-to-Speech Studio")
    st.caption("Transform any text into lifelike speech across 50+ languages.")

    col_left, col_right = st.columns([3, 1], gap="medium")

    # ── Right panel: options ───────────────────────────────
    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**🎛️ Voice Options**")

        lang_map  = get_tts_language_map()
        lang_keys = list(lang_map.keys())
        default   = lang_keys.index("English") if "English" in lang_keys else 0
        lang_name = st.selectbox("Language", lang_keys, index=default, key="tts_lang")
        lang_code = lang_map[lang_name]

        speed = st.slider("Speed ×", 0.5, 2.0, 1.0, 0.05,
                          help="< 1 = slower (uses gTTS slow mode), > 1 = faster (pydub speedup)")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**🌐 Pre-translate**")
        do_translate = st.checkbox("Translate text first")
        if do_translate:
            pre_tgt = st.selectbox("Target language", list(TRANS_LANGS.keys()), key="pretgt")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**✨ AI Enhance**")
        enhance_mode = st.selectbox("Mode", [
            "— None —",
            "Improve Clarity",
            "Make Formal",
            "Make Casual",
            "Add Emotion / Expressiveness",
            "Simplify Language",
            "Summarize into Key Points",
        ], key="enhance_mode")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Left panel: input & actions ───────────────────────
    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        text_input = st.text_area(
            "Enter text to synthesize",
            height=210,
            placeholder=(
                "Type or paste your text here…\n"
                "Tip: Use the Document Studio tab to load PDF / DOCX files."
            ),
            key="tts_main_text",
        )
        wc = len(text_input.split()) if text_input.strip() else 0
        cc = len(text_input)
        est_min = max(1, wc // 130)
        st.caption(f"📊 {cc:,} chars · {wc:,} words · ~{est_min} min audio")

        btn1, btn2, btn3 = st.columns(3)
        gen_btn    = btn1.button("🎙️ Generate Speech",  use_container_width=True, type="primary")
        enhance_btn= btn2.button("✨ AI Enhance Text",   use_container_width=True)
        detect_btn = btn3.button("🌐 Detect Language",   use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Detect language ────────────────────────────────
        if detect_btn and text_input.strip():
            try:
                code = detect(text_input)
                st.info(f"🌐 Detected language code: **`{code}`**")
            except Exception as e:
                st.warning(f"Detection failed: {e}")

        # ── AI Enhance ─────────────────────────────────────
        if enhance_btn and text_input.strip():
            client = get_claude_client()
            if not client:
                st.warning("⚠️ Add your Anthropic API Key in the sidebar to use AI features.")
            elif enhance_mode == "— None —":
                st.info("Select an enhancement mode first.")
            else:
                prompts = {
                    "Improve Clarity":                "Rewrite the following text to be clearer and more natural when read aloud. Return only the improved text.",
                    "Make Formal":                    "Rewrite in a formal, professional tone suitable for TTS. Return only the text.",
                    "Make Casual":                    "Rewrite in a warm, conversational tone suitable for TTS. Return only the text.",
                    "Add Emotion / Expressiveness":   "Rewrite to be more emotionally engaging and expressive when spoken. Return only the text.",
                    "Simplify Language":              "Rewrite using simple, plain language accessible to all audiences. Return only the text.",
                    "Summarize into Key Points":      "Summarize the following into 3–5 concise key points suitable for audio. Return only the summary.",
                }
                with st.spinner(f"✨ {enhance_mode}…"):
                    try:
                        enhanced = claude_run(client, text_input, prompts[enhance_mode])
                        st.session_state.tts_main_text = enhanced
                        st.rerun()
                    except Exception as e:
                        st.error(f"AI error: {e}")

        # ── Translate (optional) ───────────────────────────
        final_text = text_input
        if do_translate and text_input.strip():
            with st.spinner("🌐 Translating…"):
                try:
                    tgt_code = TRANS_LANGS[pre_tgt]
                    final_text = GoogleTranslator(source="auto", target=tgt_code).translate(text_input)
                    with st.expander("📋 Translated text preview"):
                        st.write(final_text)
                    lang_code = tgt_code.split("-")[0]
                except Exception as e:
                    st.error(f"Translation error: {e}")

        # ── Generate speech ────────────────────────────────
        if gen_btn and final_text.strip():
            with st.spinner("🎙️ Synthesizing speech…"):
                try:
                    audio_bytes = synthesize_speech(final_text, lang_code, speed)
                    b64         = audio_to_b64(audio_bytes)
                    st.session_state.last_audio_b64 = b64

                    fname = f"voice_{lang_code}_{int(time.time())}.mp3"
                    save_audio_history(final_text, b64, lang_name, fname)

                    st.success("✅ Speech generated successfully!")
                    st.markdown(audio_player_html(b64, autoplay=True), unsafe_allow_html=True)

                    # Waveform
                    with st.spinner("📊 Rendering waveform…"):
                        fig = draw_waveform(audio_bytes)
                        st.markdown('<div class="waveform-container">', unsafe_allow_html=True)
                        st.pyplot(fig, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        plt.close(fig)

                    st.download_button(
                        "⬇️ Download MP3", data=audio_bytes,
                        file_name=fname, mime="audio/mp3",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"❌ TTS Error: {e}")


# ─────────────────────────────────────────────────────────────
#  TAB 2 — SPEECH-TO-TEXT
# ─────────────────────────────────────────────────────────────
def tab_stt():
    st.markdown("### 🎤 Speech-to-Text Studio")
    st.caption("Upload audio and get an editable transcript with optional AI post-processing.")

    col_left, col_right = st.columns([2, 1], gap="medium")

    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**⚙️ Recognition Options**")
        stt_lang  = st.selectbox("Audio Language", list(STT_LANGS.keys()), key="stt_lang")
        stt_code  = STT_LANGS[stt_lang]
        post_act  = st.selectbox("Post-Process", [
            "— None —",
            "Translate to English",
            "Summarize (AI)",
            "Extract Key Points (AI)",
            "Generate Meeting Notes (AI)",
        ])
        speak_back = st.checkbox("🔊 Read transcript aloud after")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        audio_file  = st.file_uploader(
            "Upload Audio File",
            type=["wav", "mp3", "ogg", "flac", "m4a"],
            help="WAV, MP3, OGG, FLAC, or M4A",
        )
        trans_btn   = st.button("📝 Transcribe", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

        if trans_btn and audio_file:
            with st.spinner("🎧 Transcribing audio…"):
                try:
                    text = transcribe_audio(audio_file, stt_code)
                    st.session_state.last_transcript = text
                    st.session_state.transcript_history.insert(0, {
                        "name": audio_file.name,
                        "text": text,
                        "ts":   datetime.now().strftime("%H:%M:%S"),
                    })
                    st.success(f"✅ Transcribed {len(text.split()):,} words")
                except sr.UnknownValueError:
                    st.error("❌ Could not understand the audio. Try a clearer recording.")
                except sr.RequestError as e:
                    st.error(f"❌ Google STT API error: {e}")
                except Exception as e:
                    st.error(f"❌ {e}")
        elif trans_btn:
            st.warning("Please upload an audio file first.")

        # ── Transcript output ──────────────────────────────
        if st.session_state.last_transcript:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("**📝 Transcript**")
            transcript = st.text_area(
                "", value=st.session_state.last_transcript,
                height=180, key="transcript_box",
            )
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🔊 Read Aloud", use_container_width=True):
                    with st.spinner("Generating TTS…"):
                        try:
                            ab = synthesize_speech(transcript, "en")
                            st.markdown(audio_player_html(audio_to_b64(ab)), unsafe_allow_html=True)
                        except Exception as e:
                            st.error(str(e))
            with c2:
                st.download_button(
                    "⬇️ TXT", data=transcript,
                    file_name="transcript.txt", mime="text/plain",
                    use_container_width=True,
                )
            with c3:
                if st.button("📤 Send to TTS", use_container_width=True):
                    st.session_state.tts_main_text = transcript
                    st.success("Sent! Switch to TTS Studio.")

            # Post-processing
            if post_act != "— None —":
                client = get_claude_client()
                if st.button(f"▶ Apply: {post_act}", use_container_width=True):
                    if post_act == "Translate to English" and not client:
                        # Translation works without API key
                        with st.spinner("Translating…"):
                            result = GoogleTranslator(source="auto", target="en").translate(transcript)
                        st.markdown("**Result:**")
                        st.write(result)
                    elif client:
                        sys_map = {
                            "Translate to English":        "Translate the following text to English. Return only the translation.",
                            "Summarize (AI)":              "Summarize the following transcript concisely in 3–5 sentences.",
                            "Extract Key Points (AI)":     "Extract the key points from this transcript as a bulleted list.",
                            "Generate Meeting Notes (AI)": "Convert this transcript into professional meeting notes with: Summary, Key Decisions, Action Items, and Next Steps.",
                        }
                        with st.spinner("🤖 Processing…"):
                            result = claude_run(client, transcript, sys_map.get(post_act, ""))
                        st.markdown("**Result:**")
                        st.write(result)
                        if speak_back:
                            with st.spinner("🔊 Speaking result…"):
                                try:
                                    ab = synthesize_speech(result, "en")
                                    st.markdown(audio_player_html(audio_to_b64(ab)), unsafe_allow_html=True)
                                except Exception:
                                    pass
                    else:
                        st.warning("Add API key for AI post-processing.")
            st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  TAB 3 — TRANSLATION HUB
# ─────────────────────────────────────────────────────────────
def tab_translation():
    st.markdown("### 🌐 Translation Hub")
    st.caption("Translate across 20+ language pairs with instant audio playback.")

    col_opts, col_main = st.columns([1, 3], gap="medium")

    with col_opts:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        src_lang  = st.selectbox("Source", ["Auto-detect"] + list(TRANS_LANGS.keys()))
        tgt_lang  = st.selectbox("Target", list(TRANS_LANGS.keys()), index=1)
        speak_trl = st.checkbox("🔊 Speak translation")
        bulk_mode = st.checkbox("📋 Bulk mode (line by line)")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        src_text = st.text_area("Source Text", height=160,
                                 placeholder="Paste or type text to translate…")
        b1, b2 = st.columns(2)
        trl_btn  = b1.button("🌐 Translate",       use_container_width=True, type="primary")
        det_btn2 = b2.button("🔍 Detect Language", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if det_btn2 and src_text.strip():
            try:
                code = detect(src_text)
                matches = [n for n, c in TRANS_LANGS.items() if c.startswith(code)]
                name = matches[0] if matches else code
                st.info(f"🌐 Detected: **{name}** (`{code}`)")
            except Exception as e:
                st.warning(f"Detection failed: {e}")

        if trl_btn and src_text.strip():
            src_code = ("auto" if src_lang == "Auto-detect" else TRANS_LANGS[src_lang])
            tgt_code = TRANS_LANGS[tgt_lang]
            with st.spinner("🌐 Translating…"):
                try:
                    if bulk_mode:
                        lines  = [l for l in src_text.splitlines() if l.strip()]
                        result = "\n".join(
                            GoogleTranslator(source=src_code, target=tgt_code).translate(l)
                            for l in lines
                        )
                    else:
                        result = GoogleTranslator(source=src_code, target=tgt_code).translate(src_text)

                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown(f"**📋 {tgt_lang} Translation**")
                    trl_box = st.text_area("", value=result, height=150, key="trl_out")
                    dl1, dl2 = st.columns(2)
                    dl1.download_button("⬇️ Download TXT", data=result,
                                         file_name=f"translation_{tgt_code}.txt",
                                         mime="text/plain", use_container_width=True)
                    if dl2.button("📤 Send to TTS", use_container_width=True):
                        st.session_state.tts_main_text = result
                        st.success("Sent to TTS Studio!")

                    if speak_trl:
                        tts_code = tgt_code.split("-")[0]
                        with st.spinner("🔊 Synthesizing…"):
                            try:
                                ab = synthesize_speech(result, tts_code)
                                b64 = audio_to_b64(ab)
                                save_audio_history(result, b64, tgt_lang, f"trl_{tts_code}_{int(time.time())}.mp3")
                                st.markdown(audio_player_html(b64), unsafe_allow_html=True)
                                st.download_button("⬇️ Download Audio", data=ab,
                                                    file_name=f"trl_{tts_code}.mp3",
                                                    mime="audio/mp3", use_container_width=True)
                            except Exception as e:
                                st.warning(f"TTS unavailable for {tgt_lang}: {e}")
                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Translation error: {e}")


# ─────────────────────────────────────────────────────────────
#  TAB 4 — DOCUMENT STUDIO
# ─────────────────────────────────────────────────────────────
def tab_documents():
    st.markdown("### 📄 Document-to-Speech Studio")
    st.caption("Convert PDF, DOCX, or TXT files into spoken audio — optionally summarized.")

    col_main, col_opts = st.columns([3, 1], gap="medium")

    with col_opts:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**🎛️ Options**")
        read_lang   = st.selectbox("Read in", list(TRANS_LANGS.keys()), key="doc_lang")
        read_code   = TRANS_LANGS[read_lang].split("-")[0]
        do_ai_sum   = st.checkbox("✨ AI Summarize first")
        do_trl_doc  = st.checkbox("🌐 Translate before reading")
        if do_trl_doc:
            doc_trl_lang = st.selectbox("Translate to", list(TRANS_LANGS.keys()), index=1, key="doc_trl")
        doc_speed    = st.slider("Speed ×", 0.5, 1.8, 1.0, 0.05, key="doc_speed")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        doc_file = st.file_uploader(
            "Upload Document (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if doc_file:
            with st.spinner("📖 Extracting text…"):
                try:
                    ext = Path(doc_file.name).suffix.lower()
                    if ext == ".pdf":
                        raw_text = pdf_to_text(doc_file)
                    elif ext == ".docx":
                        raw_text = docx_to_text(doc_file)
                    else:
                        raw_text = doc_file.read().decode("utf-8", errors="ignore")

                    wc = len(raw_text.split())
                    st.success(f"✅ Extracted **{wc:,} words** from `{doc_file.name}`")
                except Exception as e:
                    st.error(f"❌ Could not read document: {e}")
                    return

            with st.expander("📋 Preview extracted text (first 1,500 chars)"):
                st.write(raw_text[:1500] + ("…" if len(raw_text) > 1500 else ""))

            speak_text = raw_text
            final_code = read_code

            # AI Summarize
            if do_ai_sum:
                client = get_claude_client()
                if not client:
                    st.warning("Add API key for AI summarization.")
                else:
                    with st.spinner("✨ Summarizing with AI…"):
                        try:
                            speak_text = claude_run(
                                client,
                                raw_text[:8000],
                                "Summarize the following document in 4–6 clear paragraphs. Return only the summary.",
                                max_tokens=800,
                            )
                            with st.expander("📝 AI Summary"):
                                st.write(speak_text)
                        except Exception as e:
                            st.error(f"AI error: {e}")

            # Translate
            if do_trl_doc:
                with st.spinner("🌐 Translating document…"):
                    try:
                        tgt_code = TRANS_LANGS[doc_trl_lang]
                        chunks   = chunk_text(speak_text, 4000)
                        speak_text = " ".join(
                            GoogleTranslator(source="auto", target=tgt_code).translate(c)
                            for c in chunks
                        )
                        final_code = tgt_code.split("-")[0]
                    except Exception as e:
                        st.error(f"Translation error: {e}")

            # Read aloud
            read_btn = st.button("🔊 Read Document Aloud", use_container_width=True, type="primary")
            if read_btn:
                limit = 3000   # chars – avoids very long wait in demo
                preview = speak_text[:limit]
                if len(speak_text) > limit:
                    st.info(f"ℹ️ Reading first {limit:,} characters (full doc has {len(speak_text):,}).")
                with st.spinner("🎙️ Generating audio…"):
                    try:
                        ab  = synthesize_speech(preview, final_code, doc_speed)
                        b64 = audio_to_b64(ab)
                        fname = doc_file.name.rsplit(".", 1)[0] + ".mp3"
                        save_audio_history(preview, b64, read_lang, fname)

                        st.markdown(audio_player_html(b64), unsafe_allow_html=True)

                        with st.spinner("📊 Waveform…"):
                            fig = draw_waveform(ab)
                            st.markdown('<div class="waveform-container">', unsafe_allow_html=True)
                            st.pyplot(fig, use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            plt.close(fig)

                        st.download_button("⬇️ Download Audio", data=ab,
                                            file_name=fname, mime="audio/mp3",
                                            use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ TTS error: {e}")


# ─────────────────────────────────────────────────────────────
#  TAB 5 — AI SCRIPT WRITER
# ─────────────────────────────────────────────────────────────
def tab_ai_script():
    st.markdown("### 🤖 AI Script Writer & Assistant")
    st.caption("Generate polished voice scripts in seconds or chat with the AI assistant.")

    client = get_claude_client()
    if not client:
        st.warning("⚠️ Add your Anthropic API Key in the sidebar to unlock this tab.")
        return

    col_gen, col_chat = st.columns([1, 2], gap="medium")

    # ── Quick generator ────────────────────────────────────
    with col_gen:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**⚡ Quick Script Generator**")

        content_type = st.selectbox("Content Type", [
            "Podcast Intro", "YouTube Video Script", "Product Advertisement",
            "Explainer Video",  "News Bulletin",     "Story Narration",
            "Educational Lecture", "Meditation Guide", "Sales Pitch",
            "Audiobook Chapter",   "Interview Intro",  "Promo Announcement",
        ])
        topic     = st.text_input("Topic / Subject", placeholder="e.g. AI in healthcare")
        duration  = st.selectbox("Target Duration", ["30 sec", "1 min", "2 min", "3 min", "5 min"])
        tone      = st.selectbox("Tone", ["Professional", "Casual & Friendly", "Energetic",
                                           "Calm & Soothing", "Authoritative", "Humorous"])
        audience  = st.text_input("Target Audience", placeholder="e.g. tech professionals")
        tts_after = st.checkbox("🔊 Auto-generate audio after")

        if st.button("⚡ Generate Script", use_container_width=True, type="primary"):
            if not topic.strip():
                st.warning("Enter a topic first.")
            else:
                prompt = (
                    f"Write a {duration} {content_type} about '{topic}'.\n"
                    f"Tone: {tone}.\n"
                    f"Target audience: {audience or 'general public'}.\n"
                    "Format it naturally for text-to-speech with no stage directions, "
                    "no markdown, no speaker labels — just the spoken words."
                )
                with st.spinner("✍️ Writing script…"):
                    try:
                        script = claude_run(
                            client, prompt,
                            "You are an expert scriptwriter specialising in voice content "
                            "for podcasts, videos, and audio production.",
                            max_tokens=1200,
                        )
                        st.session_state.quick_script = script
                        if tts_after:
                            ab  = synthesize_speech(script, "en")
                            b64 = audio_to_b64(ab)
                            fname = f"script_{int(time.time())}.mp3"
                            save_audio_history(script, b64, "English", fname)
                            st.session_state.last_audio_b64 = b64
                    except Exception as e:
                        st.error(f"AI error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Generated script output
        if st.session_state.quick_script:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("**📜 Generated Script**")
            script_box = st.text_area("", value=st.session_state.quick_script,
                                       height=200, key="script_display")
            sc1, sc2 = st.columns(2)
            if sc1.button("🔊 Speak It", use_container_width=True):
                with st.spinner("Generating audio…"):
                    try:
                        ab  = synthesize_speech(script_box, "en")
                        b64 = audio_to_b64(ab)
                        st.markdown(audio_player_html(b64), unsafe_allow_html=True)
                        st.download_button("⬇️ Download", data=ab,
                                            file_name="script.mp3", mime="audio/mp3",
                                            use_container_width=True)
                    except Exception as e:
                        st.error(str(e))
            if sc2.button("📤 Send to TTS", use_container_width=True):
                st.session_state.tts_main_text = script_box
                st.success("Sent to TTS Studio!")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── AI Chat ────────────────────────────────────────────
    with col_chat:
        st.markdown('<div class="glass-card" style="min-height:480px">', unsafe_allow_html=True)
        st.markdown("**💬 AI Voice Assistant Chat**")

        # Chat history display
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.ai_chat:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        # Input
        user_msg = st.chat_input("Ask anything about voice, scripts, TTS, languages…")
        if user_msg:
            st.session_state.ai_chat.append({"role": "user", "content": user_msg})
            with st.spinner("🤖 Thinking…"):
                try:
                    resp = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=900,
                        system=(
                            "You are an expert AI voice studio assistant. You help users "
                            "write scripts, improve text for TTS, explain voice technology, "
                            "suggest language/tone choices, and generate audio content ideas. "
                            "Keep responses concise, actionable, and friendly."
                        ),
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.ai_chat
                        ],
                    ).content[0].text
                    st.session_state.ai_chat.append({"role": "assistant", "content": resp})
                except Exception as e:
                    st.error(f"AI error: {e}")
            st.rerun()

        if st.session_state.ai_chat:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.ai_chat = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  TAB 6 — AUDIO LIBRARY
# ─────────────────────────────────────────────────────────────
def tab_library():
    st.markdown("### 📚 Audio Library")
    st.caption("All audio generated this session — replay, download, or re-send to TTS Studio.")

    if not st.session_state.audio_history and not st.session_state.transcript_history:
        st.info("🎵 Nothing here yet. Head to TTS Studio or Speech-to-Text to get started!")
        return

    # ── Audio history ──────────────────────────────────────
    if st.session_state.audio_history:
        st.markdown(f"#### 🔊 Generated Audio ({len(st.session_state.audio_history)} items)")
        for i, item in enumerate(st.session_state.audio_history):
            label = f"🔊  {item['name']}  ·  {item['ts']}  ·  {item['lang']}"
            with st.expander(label):
                st.markdown(
                    f"<div style='color:#7a80a8;font-size:.85rem;margin-bottom:.5rem'>"
                    f"📝 {item['text']}</div>",
                    unsafe_allow_html=True
                )
                st.markdown(audio_player_html(item["b64"], autoplay=False), unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.download_button(
                    "⬇️ Download MP3",
                    data=b64_to_bytes(item["b64"]),
                    file_name=item["name"],
                    mime="audio/mp3",
                    key=f"lib_dl_{i}",
                    use_container_width=True,
                )
                if c2.button("📤 Re-send to TTS", key=f"lib_rs_{i}", use_container_width=True):
                    st.session_state.tts_main_text = item["text"]
                    st.success("Sent to TTS Studio!")

    # ── Transcript history ─────────────────────────────────
    if st.session_state.transcript_history:
        st.markdown("---")
        st.markdown(f"#### 📝 Transcripts ({len(st.session_state.transcript_history)} items)")
        for j, item in enumerate(st.session_state.transcript_history):
            with st.expander(f"📝  {item['name']}  ·  {item['ts']}"):
                st.write(item["text"])
                t1, t2 = st.columns(2)
                t1.download_button(
                    "⬇️ Download TXT",
                    data=item["text"],
                    file_name=item["name"] + ".txt",
                    mime="text/plain",
                    key=f"lib_tdl_{j}",
                    use_container_width=True,
                )
                if t2.button("📤 Send to TTS", key=f"lib_tts_{j}", use_container_width=True):
                    st.session_state.tts_main_text = item["text"]
                    st.success("Sent to TTS Studio!")


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
def main():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    init_session()
    render_sidebar()

    # Hero header
    st.markdown("# 🎙️ AI Voice Studio")
    st.markdown(
        "<p style='color:#7a80a8;font-size:1.05rem;margin-top:-.4rem;margin-bottom:1.4rem'>"
        "Professional voice synthesis · Speech recognition · Translation · AI scriptwriting"
        "</p>",
        unsafe_allow_html=True
    )

    tabs = st.tabs([
        "🔊 TTS Studio",
        "🎤 Speech-to-Text",
        "🌐 Translation Hub",
        "📄 Document Studio",
        "🤖 AI Script Writer",
        "📚 Audio Library",
    ])

    with tabs[0]: tab_tts()
    with tabs[1]: tab_stt()
    with tabs[2]: tab_translation()
    with tabs[3]: tab_documents()
    with tabs[4]: tab_ai_script()
    with tabs[5]: tab_library()


if __name__ == "__main__":
    main()
