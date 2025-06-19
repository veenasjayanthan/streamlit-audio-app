import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import speech_recognition as sr
import av
from googletrans import Translator

# Basic app settings
st.set_page_config(page_title="Voice Translator", layout="centered")
st.title("🎤 Speak to Translate")
st.markdown("Use your microphone to speak and see real-time translation.")

# Language selection
lang = st.selectbox("Select translation language", ["English", "Malayalam", "Hindi", "French", "German"])
lang_codes = {
    "English": "en",
    "Malayalam": "ml",
    "Hindi": "hi",
    "French": "fr",
    "German": "de"
}

# Setup recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Clear file upload section (nothing related to file handling)
# Mic audio processor
class AudioProcessor:
    def __init__(self) -> None:
        self.text = ""
    
    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio_data = sr.AudioData(frame.to_ndarray().flatten().tobytes(), frame.sample_rate, 2)
        try:
            text = recognizer.recognize_google(audio_data)
            st.session_state['text'] = text
        except sr.UnknownValueError:
            st.session_state['text'] = "[Could not understand]"
        except sr.RequestError as e:
            st.session_state['text'] = f"[Error: {e}]"
        return frame

# WebRTC mic stream
webrtc_streamer(
    key="listen",
    mode=WebRtcMode.SENDONLY,
    in_audio=True,
    audio_processor_factory=AudioProcessor,
    client_settings=ClientSettings(
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
)

# Display text and translation
if 'text' in st.session_state:
    original = st.session_state['text']
    translated = translator.translate(original, dest=lang_codes[lang]).text
    st.markdown(f"**🗣️ You said:** `{original}`")
    st.markdown(f"**🌐 Translated ({lang}):** `{translated}`")


  
