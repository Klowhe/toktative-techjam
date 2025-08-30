import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in your environment or .env file")

# Initialize the Gemini client
genai.configure(api_key=gemini_api_key)

def ask_gemini(question):
    # Use genai.GenerativeModel and specify the model name
    model = genai.GenerativeModel("gemini-2.5-flash")
    chat = model.start_chat(history=[])
    
    # Send the question and get the response
    response = chat.send_message(question)
    return response.text

