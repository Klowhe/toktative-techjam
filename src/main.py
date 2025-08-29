import os
import requests
from api.qdrant_api import init_qdrant, query_qdrant
from api.ollama_api import get_embedding, generate_response
from config.collections import SOURCE_COLLECTION_MAP
# from dotenv import load_dotenv

# ---------------------- Initialize Qdrant ----------------------
qdrant_client = init_qdrant()

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
    top_docs = query_qdrant(qdrant_client, embedding, collection_name=collection_name, top_k=top_k)

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