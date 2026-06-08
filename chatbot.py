import google.generativeai as genai

API_KEY = "AIzaSyDSc4qle0skmtHQ0ALHod2-A74Xlllf8os"

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-3.5-flash")

def ask_chatbot(question):
    try:
        response = model.generate_content(question)
        return response.text

    except Exception:
        return "AI service is currently unavailable. Please try again later."