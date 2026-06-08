import google.generativeai as genai

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-3.5-flash")

def ask_chatbot(question):
    try:
        response = model.generate_content(question)
        return response.text

    except Exception:
        return "AI service is currently unavailable. Please try again later."