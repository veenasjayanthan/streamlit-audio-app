import streamlit as st
import speech_recognition as sr
import tempfile
from datetime import datetime
from langdetect import detect
from gtts import gTTS
import os
import google.generativeai as genai

# ====== CONFIGURE GEMINI ======
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Load from Streamlit secrets

# ====== TRANSLATE TEXT ======
def translate_text(text, target_lang, source_lang=None):
    prompt = f"""
    Translate the following text from {source_lang or 'auto-detect'} to {target_lang}.
    Text: {text}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# ====== EXTRACT TEXT FROM IMAGE ======
def extract_text_from_image_gemini(image_path):
    model = genai.GenerativeModel("gemini-1.5-flash")
    with open(image_path, "rb") as f:
        img_data = f.read()
    response = model.generate_content([
        "Extract and return only the raw visible text from this image.",
        {"mime_type": "image/png", "data": img_data}
    ])
    return response.text.strip()

# ====== SPEAK TEXT ======
def speak_text(text, lang_code):
    path = f"audio_{datetime.now().timestamp()}.mp3"
    tts = gTTS(text, lang=lang_code)
    tts.save(path)
    return path

# ====== SUPPORTED LANGUAGES ======
def get_supported_languages():
    return {
        "en": "English", "hi": "Hindi", "ml": "Malayalam",
        "ta": "Tamil", "te": "Telugu", "kn": "Kannada",
        "fr": "French", "es": "Spanish", "de": "German",
        "zh": "Chinese", "ar": "Arabic"
    }

# ====== STREAMLIT UI ======
st.set_page_config(page_title="🌐 AI Chat with OCR", layout="centered")
st.markdown("<h1 style='text-align:center'>🌐 Multilingual AI Chat with Voice & Image</h1>", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

languages = get_supported_languages()
lang_name = st.selectbox("Choose Target Language", list(languages.values()))
lang_code = [k for k, v in languages.items() if v == lang_name][0]

st.markdown("### 💬 Type Your Message")
user_input = st.text_input("Enter your message")

# ====== TRANSLATE & SPEAK ======
if user_input:
    try:
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
    except Exception as e:
        st.error(f"Translation error: {e}")

# ====== IMAGE OCR ======
st.markdown("### 🖼️ Image to Multilingual Text")
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
        temp.write(uploaded_file.read())
        temp_path = temp.name

    st.image(temp_path, caption="Uploaded Image", use_container_width=True)

    with st.spinner("🔍 Extracting text using Gemini..."):
        try:
            extracted_text = extract_text_from_image_gemini(temp_path)
            st.markdown("**📜 Extracted Text:**")
            st.write(extracted_text)

            if extracted_text.strip():
                detected_lang_code = detect(extracted_text)
                detected_lang_name = languages.get(detected_lang_code, "Unknown")
                st.success(f"Detected Language: {detected_lang_name} ({detected_lang_code})")

                translated_text = translate_text(extracted_text, lang_code, detected_lang_code)
                st.markdown("**🌐 Translated Text:**")
                st.write(translated_text)

                audio_path = speak_text(translated_text, lang_code)
                st.audio(audio_path, format="audio/mp3")
        except Exception as e:
            st.error(f"Error: {e}")

# ====== HISTORY ======
if st.checkbox("📜 Show History"):
    for msg in st.session_state.history:
        st.markdown(f"🕒 {msg['timestamp']}")
        st.write("You:", msg["input"])
        st.write("Translated:", msg["translated"])

