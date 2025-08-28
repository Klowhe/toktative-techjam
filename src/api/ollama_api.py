import requests
# ---------------------- Ollama Settings ----------------------
OLLAMA_URL = "http://127.0.0.1:11434/api/embeddings"  # Ollama local embed endpoint
OLLAMA_MODEL = "mxbai-embed-large"                     # Replace with your embedding model
OLLAMA_CHAT_MODEL = "llama3.1:8b"                       # Your chat model for generating responses

# ---------------------- Helper Functions ----------------------

def get_embedding(text: str) -> list:
    """Get embedding from local Ollama server via HTTP."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": text
    }
    response = requests.post(f"{OLLAMA_URL}", json=payload)
    response.raise_for_status()
    return response.json()["embedding"]

def generate_response(context_text: str, question: str) -> str:
    payload = {
        "model": OLLAMA_CHAT_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"}
        ],
        "stream": False
    }
    response = requests.post("http://127.0.0.1:11434/api/chat", json=payload)
    response.raise_for_status()
    return response.json()["message"]["content"]