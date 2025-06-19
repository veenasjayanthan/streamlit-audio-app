import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import queue
import threading
import whisper
from googletrans import Translator
import numpy as np
import av
import tempfile
import os
import wave

# Load Whisper model
model = whisper.load_model("base")  # or "tiny" for faster, "small" for better

# Translator
translator = Translator()

# Queue to store audio frames
audio_queue = queue.Queue()

# Language selection
st.set_page_config(page_title="Live Voice Translator")
st.title("🎙️ Real-Time Voice Translation")

lang = st.selectbox("Translate to", ["English", "Malayalam", "Hindi", "French", "German"])
lang_codes = {
    "English": "en",
    "Malayalam": "ml",
    "Hindi": "hi",
    "French": "fr",
    "German": "de"
}

# Audio processing class
class AudioProcessor:
    def __init__(self):
        self.buffer = b""
        self.sample_rate = 48000

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        audio = audio.mean(axis=0).astype(np.int16).tobytes()  # Mono
        audio_queue.put(audio)
        return frame

webrtc_streamer(
    key="live-voice",
    mode=WebRtcMode.SENDONLY,
    in_audio=True,
    audio_processor_factory=AudioProcessor
)

# Background thread to transcribe and translate
def process_audio():
    audio_bytes = b""
    while True:
        try:
            audio_chunk = audio_queue.get(timeout=5)
            audio_bytes += audio_chunk

            if len(audio_bytes) >= 48000 * 5 * 2:  # 5 seconds of audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                    wf = wave.open(f.name, 'wb')
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(48000)
                    wf.writeframes(audio_bytes)
                    wf.close()

                    result = model.transcribe(f.name)
                    text = result["text"]

                    if text.strip():
                        translated = translator.translate(text, dest=lang_codes[lang]).text
                        st.session_state["last_text"] = text
                        st.session_state["last_translated"] = translated

                os.unlink(f.name)
                audio_bytes = b""
        except queue.Empty:
            continue

# Start the background thread
if "audio_thread_started" not in st.session_state:
    threading.Thread(target=process_audio, daemon=True).start()
    st.session_state["audio_thread_started"] = True

# Show results
if "last_text" in st.session_state:
    st.markdown(f"**🗣️ You said:** `{st.session_state['last_text']}`")
    st.markdown(f"**🌐 Translated ({lang}):** `{st.session_state['last_translated']}`")
