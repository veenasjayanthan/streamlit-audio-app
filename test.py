from utils.audio_emotion import detect_emotion_from_voice
import streamlit as st
import os, tempfile, base64
import speech_recognition as sr
from datetime import datetime
import google.generativeai as genai
from langdetect import detect
import streamlit.components.v1 as components

# 🔐 Gemini API Key
GEMINI_API_KEY = "AIzaSyAnJhtbDRkYYP3kvIZ9i2LonZvzSG9XzAc"
genai.configure(api_key=GEMINI_API_KEY)

# 🌐 Translate using Gemini
def translate_text(text, target_lang, source_lang=None):
    prompt = f"Translate the following text from {source_lang or 'auto-detect'} to {target_lang}:\n\n{text}"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# 🖼️ OCR
def extract_text_from_image_gemini(image_path):
    model = genai.GenerativeModel("gemini-1.5-flash")
    with open(image_path, "rb") as f:
        img_data = f.read()
    response = model.generate_content([
        "Extract and return only the raw visible text from this image.",
        {"mime_type": "image/png", "data": img_data}
    ])
    return response.text.strip()

# 🔊 Text to Speech
def speak_text(text, lang_code):
    from gtts import gTTS
    path = f"audio_{datetime.now().timestamp()}.mp3"
    tts = gTTS(text, lang=lang_code)
    tts.save(path)
    return path

# 🌍 Supported Languages
def get_supported_languages():
    return {
        "en": "English", "hi": "Hindi", "ml": "Malayalam",
        "ta": "Tamil", "te": "Telugu", "kn": "Kannada",
        "fr": "French", "es": "Spanish", "de": "German",
        "zh": "Chinese", "ar": "Arabic"
    }

# 🎨 UI Setup
st.set_page_config(page_title="🌐 AI Chat with Voice & Image", layout="centered")
st.markdown("<h1 style='text-align:center'>🌐 Multilingual AI Chat with Voice & Image</h1>", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

# 🌐 Choose Language
languages = get_supported_languages()
lang_name = st.selectbox("Choose Target Language", list(languages.values()))
lang_code = [k for k, v in languages.items() if v == lang_name][0]

# 🎤 Voice Recording using browser
st.markdown("### 🎙️ Record Your Voice")
components.html("""
<html>
  <body>
    <button onclick="startRecording()">🎤 Start Recording (6 seconds)</button>
    <p id="status"></p>
    <script>
      let mediaRecorder;
      let audioChunks = [];

      async function startRecording() {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        document.getElementById("status").innerText = "Recording...";

        mediaRecorder.ondataavailable = event => {
          audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
          const blob = new Blob(audioChunks, { type: 'audio/wav' });
          const reader = new FileReader();
          reader.onloadend = function () {
            const base64data = reader.result.split(',')[1];
            const form = document.createElement("form");
            form.method = "POST";
            form.action = "/upload-audio";
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "audio";
            input.value = base64data;
            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
          };
          reader.readAsDataURL(blob);
          document.getElementById("status").innerText = "Recording saved. Refresh page to try again.";
        };

        setTimeout(() => {
          mediaRecorder.stop();
        }, 6000);
      }
    </script>
  </body>
</html>
""", height=250)

# 🗂️ Accept base64 audio if submitted
query_params = st.experimental_get_query_params()
audio_data = st.experimental_get_query_params().get("audio", [None])[0]
user_input = ""

if audio_data:
    audio_bytes = base64.b64decode(audio_data)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        audio_path = f.name
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        user_input = recognizer.recognize_google(audio)
        st.success("🗣️ You said: " + user_input)
    except:
        st.error("Could not understand audio.")

# 🔄 Translate and Speak
if user_input:
    translated = translate_text(user_input, lang_code)
    st.markdown("#### 🌐 Translated Text")
    st.write(translated)
    audio_path = speak_text(translated, lang_code)
    st.audio(audio_path, format="audio/mp3")
    st.session_state.history.append({
        "timestamp": datetime.now().isoformat(),
        "input": user_input,
        "translated": translated,
    })

# 🖼️ OCR from Image
st.markdown("### 🖼️ Image to Multilingual Text")
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
        temp.write(uploaded_file.read())
        temp_path = temp.name
    st.image(temp_path, caption="Uploaded Image", use_container_width=True)
    with st.spinner("🔍 Extracting text..."):
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

# 🧾 Show History
if st.checkbox("📜 Show History"):
    for msg in st.session_state.history:
        st.markdown(f"🕒 {msg['timestamp']}")
        st.write("You:", msg["input"])
        st.write("Translated:", msg["translated"])



    
    
