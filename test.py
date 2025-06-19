import streamlit.components.v1 as components

components.html("""
<link rel="manifest" href="/.streamlit/public/manifest.json">
<meta name="theme-color" content="#1f77b4">
""", height=0)







import streamlit as st
import os
import tempfile
from datetime import datetime
import google.generativeai as genai
from langdetect import detect
from gtts import gTTS

# Optional: Try importing speech recognition
try:
    import speech_recognition as sr
    sr.Microphone()  # test if microphone is available
    HAS_MIC = True
except Exception:
    HAS_MIC = False

# ============ CONFIGURE GEMINI API ============

#YOUR_API_KEY_HERE="AIzaSyAnJhtbDRkYYP3kvIZ9i2LonZvzSG9XzAc"
genai.configure(api_key="AIzaSyAnJhtbDRkYYP3kvIZ9i2LonZvzSG9XzAc")  # Replace with your Gemini API Key

# ============ TRANSLATE TEXT USING GEMINI ============
def translate_text(text, target_lang, source_lang=None):
    prompt = f"Translate the following text from {source_lang or 'auto-detect'} to {target_lang}.\nText: {text}"
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content([prompt])  # ✅ WRAPPED IN LIST
        return response.text.strip()
    except Exception as e:
        st.error(f"❌ Gemini Translation Error: {e}")
        return "Translation failed."

# ============ GEMINI IMAGE OCR ============
def extract_text_from_image_gemini(image_path):
    model = genai.GenerativeModel("gemini-1.5-flash")
    with open(image_path, "rb") as f:
        img_data = f.read()
    try:
        response = model.generate_content([
            "Extract and return only the raw visible text from this image.",
            {"mime_type": "image/png", "data": img_data}
        ])
        return response.text.strip()
    except Exception as e:
        st.error(f"❌ OCR Error: {e}")
        return ""

# ============ AUDIO SPEAK ============
def speak_text(text, lang_code):
    path = f"audio_{datetime.now().timestamp()}.mp3"
    tts = gTTS(text, lang=lang_code)
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
st.set_page_config(page_title="🌐 AI Chat with OCR", layout="centered")
st.markdown("<h1 style='text-align:center'>🌐 Multilingual AI Chat with Voice & Image</h1>", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

languages = get_supported_languages()
lang_name = st.selectbox("Choose Target Language", list(languages.values()))
lang_code = [k for k, v in languages.items() if v == lang_name][0]

# ============ TEXT / VOICE INPUT ============
st.markdown("### 🎤 Speak or 💬 Type")
user_input = ""

if HAS_MIC:
    use_voice = st.toggle("Use Voice Input", value=False)
else:
    use_voice = False
    st.warning("⚠️ Microphone not available. Using text input only.")

if not use_voice:
    user_input = st.text_input("Enter your message")
else:
    if st.button("🎙️ Start Recording"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎙️ Listening...")
            audio = recognizer.listen(source, phrase_time_limit=6)
            try:
                user_input = recognizer.recognize_google(audio)
                st.success("You said: " + user_input)
            except Exception as e:
                st.error(f"Could not understand audio: {e}")

# ============ TEXT TRANSLATION ============
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
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
        temp.write(uploaded_file.read())
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





