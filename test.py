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

# Page config
st.set_page_config(page_title="Multilingual Voice Translator")
st.title("🌍 Multilingual AI Chat with Voice & Image")

# Language selector
lang = st.selectbox("Choose Target Language", ["English", "Malayalam", "Hindi", "French", "German"])
lang_codes = {
    "English": "en",
    "Malayalam": "ml",
    "Hindi": "hi",
    "French": "fr",
    "German": "de"
}

# Translator and Whisper model
translator = Translator()
model = whisper.load_model("base")

# Queue to handle audio frames
audio_queue = queue.Queue()

# Audio processing class
class AudioProcessor:
    def __init__(self):
        self.sample_rate = 48000

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        audio = audio.mean(axis=0).astype(np.int16).tobytes()
        audio_queue.put(audio)
        return frame

# WebRTC streamer
webrtc_streamer(
    key="stream",
    mode=WebRtcMode.SENDONLY,
    in_audio=True,
    audio_processor_factory=AudioProcessor
)

# Worker thread to process audio
def transcribe_audio():
    audio_data = b""
    while True:
        try:
            chunk = audio_queue.get(timeout=5)
            audio_data += chunk

            if len(audio_data) >= 48000 * 5 * 2:  # 5 seconds
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                    wf = wave.open(f.name, 'wb')
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(48000)
                    wf.writeframes(audio_data)
                    wf.close()

                    result = model.transcribe(f.name)
                    text = result["text"]

                    if text.strip():
                        translated = translator.translate(text, dest=lang_codes[lang]).text
                        st.session_state["last_text"] = text
                        st.session_state["last_translated"] = translated

                os.unlink(f.name)
                audio_data = b""
        except queue.Empty:
            continue

# Start thread only once
if "started" not in st.session_state:
    threading.Thread(target=transcribe_audio, daemon=True).start()
    st.session_state["started"] = True

# Show results
if "last_text" in st.session_state:
    st.markdown(f"**🗣 You said:** `{st.session_state['last_text']}`")
    st.markdown(f"**🌐 Translated ({lang}):** `{st.session_state['last_translated']}`")
