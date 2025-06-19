import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import speech_recognition as sr
import av
from googletrans import Translator

st.set_page_config(page_title="Live Voice Translator", layout="centered")

st.title("🎤 Live Voice Translator 🌐")
st.markdown("Speak into the mic and get the translation in real time.")

# Select output language
lang = st.selectbox("Choose output language", ["English", "Malayalam", "Hindi", "French", "German"])
lang_codes = {
    "English": "en",
    "Malayalam": "ml",
    "Hindi": "hi",
    "French": "fr",
    "German": "de"
}

translator = Translator()

# Recognizer setup
recognizer = sr.Recognizer()

class AudioProcessor:
    def __init__(self):
        self.recognizer = recognizer
        self.translator = translator

    def recv(self, frame):
        audio = frame.to_ndarray()
        # Not converting here because we need to handle audio differently below
        return av.AudioFrame.from_ndarray(audio, layout="mono")

    def recv_audio(self, frame: av.AudioFrame):
        pcm = frame.to_ndarray().flatten().tobytes()
        with sr.AudioData(pcm, frame.sample_rate, 2) as audio_data:
            try:
                text = self.recognizer.recognize_google(audio_data)
                st.session_state['last_text'] = text
            except sr.UnknownValueError:
                st.session_state['last_text'] = "[Unclear Speech]"
            except sr.RequestError as e:
                st.session_state['last_text'] = f"[Error: {e}]"

# WebRTC Stream
webrtc_ctx = webrtc_streamer(
    key="voice-translator",
    mode=WebRtcMode.SENDONLY,
    in_audio=True,
    audio_processor_factory=AudioProcessor,
    client_settings=ClientSettings(
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
)

if 'last_text' in st.session_state:
    st.markdown(f"🗣️ You said: **{st.session_state['last_text']}**")
    translated = translator.translate(st.session_state['last_text'], dest=lang_codes[lang])
    st.markdown(f"🌐 Translation ({lang}): **{translated.text}**")

