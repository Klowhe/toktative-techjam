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
def formulate_response(top_results):
    """
    Combine the text chunks and optionally summarize for user response.
    """
    text_chunks = extract_text_from_results(top_results)
    if not text_chunks:
        return "No relevant text found."

    # Simple concatenation for now
    combined_text = "\n\n".join(text_chunks)

    # Optional: You could run summarization here with LLM if desired
    # e.g., call Ollama model to summarize combined_text

    return combined_text

# ---------------------- Example Usage ----------------------
if __name__ == "__main__":
    query_text = "Name 3 regulations brought forth by the EU Digital Services Act."
    source_file = "eu_dsa.pdf"

    try:
        top_results = retrieve_top_documents(query_text, source_file, top_k=5)
        for i, res in enumerate(top_results, 1):
            print(f"\n--- Result {i} ---")
            print("Score:", res["score"])
            print("Metadata:", res["metadata"])
            print(res)
    except Exception as e:
        print("Error:", e)
