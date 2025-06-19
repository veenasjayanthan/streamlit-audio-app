import streamlit as st
import os
import tempfile
from datetime import datetime
import google.generativeai as genai
from langdetect import detect
from gtts import gTTS
from pydub import AudioSegment
import base64

# ============ CONFIGURE GEMINI API ============
genai.configure(api_key="YOUR_API_KEY_HERE")  # Replace with your Gemini API key

# ============ TRANSLATE TEXT USING GEMINI ============
def translate_text(text, target_lang, source_lang=None):
    prompt = f"Translate the following text from {source_lang or 'auto-detect'} to {target_lang}.\nText: {text}"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# ============ IMAGE OCR ============
def extract_text_from_image_gemini(image_path):
    model = genai.GenerativeModel("gemini-1.5-flash")
    with open(image_path, "rb") as f:
        img_data = f.read()
    response = model.generate_content([
        "Extract and return only the raw visible text from this image.",
        {"mime_type": "image/png", "data": img_data}
    ])
    return response.text.strip()

# ============ TEXT TO SPEECH ============
def speak_text(text, lang_code):
    tts = gTTS(text, lang=lang_code)
    path = f"audio_{datetime.now().timestamp()}.mp3"
    tts.save(path)
    return path

# ============ SUPPORTED LANGUAGES ============
def get_supported_languages():
    return {
        "en": "English", "hi": "Hindi", "ml": "Malayalam", "ta": "Tamil",
        "te": "Telugu", "kn": "Kannada", "fr": "French", "es": "Spanish",
        "de": "German", "zh": "Chinese", "ar": "Arabic"
    }

# ============ STREAMLIT UI ============
st.set_page_config(page_title="🌐 Multilingual Voice/Image Translator", layout="centered")
st.markdown("<h1 style='text-align:center'>🌐 Multilingual AI Chat with Voice & Image</h1>", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

languages = get_supported_languages()
lang_name = st.selectbox("Choose Target Language", list(languages.values()))
lang_code = [k for k, v in languages.items() if v == lang_name][0]

# ============ VOICE / TEXT ============
st.markdown("### 🎤 Speak or 💬 Type")
input_mode = st.radio("Choose Input Mode:", ["Text", "Voice (Browser Upload)"], horizontal=True)

user_input = ""

if input_mode == "Text":
    user_input = st.text_input("Enter your message")

elif input_mode == "Voice (Browser Upload)":
    st.info("Record your voice using your device and upload the audio file.")
    audio_file = st.file_uploader("Upload recorded audio (.mp3 or .wav)", type=["mp3", "wav"])
    if audio_file:
        audio_path = os.path.join(tempfile.gettempdir(), audio_file.name)
        with open(audio_path, "wb") as f:
            f.write(audio_file.read())

        audio = AudioSegment.from_file(audio_path)
        audio.export("temp.wav", format="wav")  # Convert for whisper

        import whisper
        model = whisper.load_model("base")
        result = model.transcribe("temp.wav")
        user_input = result["text"]
        st.success("Recognized Text: " + user_input)

# ============ TRANSLATE ============
if user_input:
    translated = translate_text(user_input, lang_code)
    st.markdown("#### 🤖 Translated")
    st.write(translated)

    audio_path = speak_text(translated, lang_code)
    st.audio(audio_path, format="audio/mp3")

    st.session_state.history.append({
        "timestamp": datetime.now().isoformat(),
        "input": user_input,
        "translated": translated,
    })

# ============ IMAGE OCR ============
st.markdown("### 🖼️ Image to Multilingual Text")
uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
if uploaded_image:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
        temp.write(uploaded_image.read())
        temp_path = temp.name

    st.image(temp_path, caption="Uploaded Image", use_container_width=True)

    with st.spinner("🔍 Extracting text using Gemini..."):
        extracted_text = extract_text_from_image_gemini(temp_path)

    st.markdown("**📜 Extracted Text:**")
    st.write(extracted_text)

    if extracted_text.strip():
        try:
            detected_lang_code = detect(extracted_text)
            detected_lang_name = languages.get(detected_lang_code, "Unknown")
            st.success(f"Detected Language: {detected_lang_name} ({detected_lang_code})")

            translated_text = translate_text(extracted_text, lang_code, detected_lang_code)
            st.markdown("**🌐 Translated Text:**")
            st.write(translated_text)

            audio_path = speak_text(translated_text, lang_code)
            st.audio(audio_path, format="audio/mp3")
        except Exception as e:
            st.error(f"Translation Error: {e}")

# ============ HISTORY ============
if st.checkbox("📜 Show History"):
    for msg in st.session_state.history:
        st.markdown(f"🕒 {msg['timestamp']}")
        st.write("You:", msg["input"])
        st.write("Translated:", msg["translated"])



