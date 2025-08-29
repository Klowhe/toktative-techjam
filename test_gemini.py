import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)

def test_gemini():
    model_name = "models/gemini-2.0-flash-exp"
    model = genai.GenerativeModel(model_name)
    prompt = "what is value of 1 + 1"
    try:
        response = model.generate_content(prompt)
        print("Gemini response:", response.text)
    except Exception as e:
        print("Gemini error:", e)

if __name__ == "__main__":
    test_gemini()
