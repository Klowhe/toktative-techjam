import os
import requests
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# ---------------------- Load Environment ----------------------
load_dotenv()
QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# ---------------------- Ollama Settings ----------------------
OLLAMA_URL = "http://127.0.0.1:11434/api/embeddings"  # Ollama local embed endpoint
OLLAMA_MODEL = "mxbai-embed-large"           # Replace with your embedding model
OLLAMA_CHAT_MODEL = "llama3.1:8b"                       # Your chat model for generating responses

# ---------------------- Initialize Qdrant ----------------------
qdrant_client = QdrantClient(
    url=QDRANT_ENDPOINT,
    api_key=QDRANT_API_KEY
)

# ---------------------- Helper Functions ----------------------

def get_embedding(text):
    """Get embedding from local Ollama server via HTTP."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": text
    }
    response = requests.post(f"{OLLAMA_URL}", json=payload)
    response.raise_for_status()
    return response.json()["embedding"]

def query_qdrant(embedding: list, collection_name: str, top_k: int = 5):
    """
    Query Qdrant collection for top-k most similar points using query_points.
    """
    results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=embedding,
        limit=3
    )
    return results

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

# Map source file to collection names
SOURCE_COLLECTION_MAP = {
    "eu_dsa.pdf": "eu_regulation",
    "fl_bill.pdf": "fl_regulation",
    "utah_regulation_act.pdf": "ut_regulation",
    "ncmec.pdf": "ncmec_regulation",
    "ca_poksmaa.pdf": "ca_regulation"
}

# ---------------------- Main Query Loop ----------------------

def retrieve_top_documents(query_text: str, source_file: str, top_k: int = 5):
    """
    Given a query and a source file, embed the query and retrieve top-k similar documents.
    """
    collection_name = SOURCE_COLLECTION_MAP.get(source_file.lower())
    if not collection_name:
        raise ValueError(f"No Qdrant collection mapped for source file: {source_file}")

    # 1. Generate embedding
    embedding = get_embedding(query_text)

    # 2. Query Qdrant
    top_docs = query_qdrant(embedding, collection_name=collection_name, top_k=top_k)

    # 3. Format results
    results = []
    for doc in top_docs:
        results.append({
            "score": doc.score,
            "metadata": doc.payload
        })
    return results

# ---------------------- Extract text from top-k results ----------------------
def extract_text_from_results(top_results):
    """
    Collect the text from the payload of the top-k results.
    """
    combined_text = []
    for doc in top_results:
        payload = doc["metadata"]
        text_chunk = payload.get("text")  # make sure 'text' was stored during upsert
        if text_chunk:
            combined_text.append(text_chunk)
    return combined_text



# ---------------------- Formulate response ----------------------
def formulate_response(top_results, query_text):
    """
    Combine the text chunks and optionally summarize for user response.
    """
    text_chunks = extract_text_from_results(top_results)
    if not text_chunks:
        return "No relevant text found."

    # Simple concatenation for now
    combined_text = "\n\n".join(text_chunks)

    # 4. Generate response using Ollama chat model
    response = generate_response(combined_text, query_text)
    return response

# ---------------------- Example Usage ----------------------
if __name__ == "__main__":
    query_text = "My feature will Enable users to reshare stories from others, with auto-expiry after 48 hours. This feature logs resharing attempts with EchoTrace and stores activity under BB. Is this in violation of EU regulations regarding user data and privacy?"
    source_file = "eu_dsa.pdf"

    try:
        top_results = retrieve_top_documents(query_text, source_file, top_k=3)
        
        response_text = formulate_response(top_results, query_text)
        print("\n--- Formulated Response ---")
        print(response_text)

    except Exception as e:
        print("Error:", e)