from openai import OpenAI
import os
from dotenv import load_dotenv

# 1. Load the .env file first
load_dotenv()

# 2. Get the API key from environment
open_ai_api_key = os.getenv("OPENAI_API_KEY")
if not open_ai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in your environment or .env file")

# 3. Initialize the client
client = OpenAI(api_key=open_ai_api_key)

# 4. Function to ask a question
def ask_openai(question):
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
    )
    return response.choices[0].message.content

# Example usage
# question = "What is the capital of France?"
# answer = ask_openai(question)
# print(answer)
