import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import io

st.set_page_config(page_title="Multilingual Voice + Image Chat", layout="centered")

st.title("🌍 Multilingual AI Chat Assistant")

# Language selector
language = st.selectbox("Choose a language", ["English", "Spanish", "Hindi", "Malayalam", "Tamil", "French"])

# Toggle: Use Voice Input or Type
use_voice = st.toggle("🎙️ Use Voice Input")

if use_voice:
    st.markdown("### 🎤 Record Your Voice")

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
                form.action = "/upload-audio";  // You need to handle this endpoint in your backend
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

else:
    st.markdown("### 💬 Type Your Message")
    typed_input = st.text_input("Enter your message here...")
    if typed_input:
        st.success(f"Typed: {typed_input} ({language})")

# --- Image Upload Section ---
st.markdown("### 🖼️ Image to Multilingual Text")

uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Placeholder for OCR logic
    st.info(f"Extracting text from image in {language}...")

    # Just for simulation
    st.write("👉 Extracted text: *'This is a placeholder for OCR output.'*")
