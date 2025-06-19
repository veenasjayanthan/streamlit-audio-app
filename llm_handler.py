import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# List available models (optional debug)
# print([m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods])

model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

def generate_llm_response(prompt):
    response = model.generate_content(prompt)
    return response.text
