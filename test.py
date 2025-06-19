import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import speech_recognition as sr
import av
from googletrans import Translator

# Setup
st.set_page_config(page_title="Live Voice Translator", layout="centered")
st.title("🎤 Speak to Translate")
st.markdown("Speak directly into the microphone and get translation instantly.")

# Language options
lang = st.selectbox("Translate to", ["English", "Malayalam", "Hindi", "French", "German"])
lang_codes = {
    "English": "en",
    "Malayalam": "ml",
    "Hindi": "hi",
    "French": "fr",
    "German": "de"
}

# Translator and recognizer
translator = Translator()
recognizer = sr.Recognizer()

# Audio processing class
class AudioProcessor:
    def __init__(self) -> None:
        self.recognizer = recognizer
        self.translator = translator

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray().flatten().tobytes()
        audio_data = sr.AudioData(pcm, frame.sample_rate, 2)
        try:
            text = self.recognizer.recognize_google(audio_data)
            st.session_state['text'] = text
        except sr.UnknownValueError:
            st.session_state['text'] = "[Unclear speech]"
        except sr.RequestError as e:
            st.session_state['text'] = f"[Error: {e}]"
        return frame

# WebRTC streaming (mic only)
webrtc_streamer(
    key="live-translate",
    mode=WebRtcMode.SENDONLY,
    in_audio=True,
    audio_processor_factory=AudioProcessor,
    client_settings=ClientSettings(
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
)

# Display translation
if 'text' in st.session_state:
    spoken = st.session_state['text']
    translated = translator.translate(spoken, dest=lang_codes[lang]).text
    st.markdown(f"🗣️ You said: **{spoken}**")
    st.markdown(f"🌐 Translation ({lang}): **{translated}**")
