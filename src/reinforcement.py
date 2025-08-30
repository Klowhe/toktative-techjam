import os
import requests
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# ---------------------- Load Environment ----------------------
load_dotenv()
QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# ---------------------- Ollama Settings ----------------------
OLLAMA_URL = "http://127.0.0.1:11434"  # Base Ollama local endpoint
OLLAMA_EMBED_MODEL = "mxbai-embed-large"           # Replace with your embedding model
OLLAMA_CHAT_MODEL = "llama3.1:8b"                       # Your chat model for generating responses
OPENAPI_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")


# ---------------------- Initialize Qdrant ----------------------
qdrant_client = QdrantClient(
    url=QDRANT_ENDPOINT,
    api_key=QDRANT_API_KEY
)

# ---------------------- Helper Functions ----------------------

def get_embedding(text: str):
    """Get embedding from Ollama server for semantic search."""
    payload = {"model": OLLAMA_EMBED_MODEL, "prompt": text}
    response = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload)
    response.raise_for_status()
    return response.json()["embedding"]

def query_qdrant(embedding: list, collection_name: str, top_k: int = 5):
    """Search Qdrant collection for top-k similar documents."""
    results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=embedding,
        limit=top_k
    )
    return results

def chat_with_ollama(messages: list) -> str:
    """Send messages to Ollama chat model and return response."""
    payload = {"model": OLLAMA_CHAT_MODEL, "messages": messages, "stream": False}
    response = requests.post(f"{OLLAMA_URL}/api/chat", json=payload)
    response.raise_for_status()
    return response.json()["message"]["content"]

# ---------------------- Source Mapping ----------------------
SOURCE_COLLECTION_MAP = {
    "eu_dsa.pdf": "eu_regulation",
    "fl_bill.pdf": "fl_regulation",
    "utah_regulation_act.pdf": "ut_regulation",
    "ncmec.pdf": "ncmec_regulation",
    "ca_poksmaa.pdf": "ca_regulation"
}

# ---------------------- Pipeline Steps ----------------------

def extract_entities(feature_name: str, feature_description: str):
    """Extract structured entities from feature using LLM."""
    prompt = f"""
    Extract the following entities from this feature:
    - location (jurisdiction, state, or region)
    - age (any mentioned age group or restriction)
    - keywords (important technical / policy terms)
    - related_regulations (if any obvious law/regulation is mentioned)

    Respond strictly in JSON format.

    Feature Name: {feature_name}
    Feature Description: {feature_description}
    """
    messages = [{"role": "system", "content": "You are an expert compliance entity extractor."},
                {"role": "user", "content": prompt}]
    return chat_with_ollama(messages)

def retrieve_regulation_text(feature_description: str, source_file: str, top_k: int = 3):
    """Retrieve relevant law/regulation text from Qdrant."""
    collection_name = SOURCE_COLLECTION_MAP.get(source_file.lower())
    if not collection_name:
        raise ValueError(f"No Qdrant collection mapped for source file: {source_file}")
    
    embedding = get_embedding(feature_description)
    top_docs = query_qdrant(embedding, collection_name, top_k=top_k)

    return [doc.payload.get("text", "") for doc in top_docs if "text" in doc.payload]

def retrieve_best_regulation_text(feature_description: str, top_k: int = 3):
    """
    Search all collections in SOURCE_COLLECTION_MAP and return the best matching law(s) and relevant text.
    Returns a list of dicts: [{"collection": ..., "source_file": ..., "texts": [...]}]
    """
    results = []
    for source_file, collection_name in SOURCE_COLLECTION_MAP.items():
        embedding = get_embedding(feature_description)
        top_docs = query_qdrant(embedding, collection_name, top_k=top_k)
        texts = [doc.payload.get("text", "") for doc in top_docs if "text" in doc.payload]
        if texts:
            results.append({
                "collection": collection_name,
                "source_file": source_file,
                "texts": texts,
                "score": top_docs[0].score if top_docs else 0
            })
    # Sort by score descending, keep only those with non-empty texts
    results = sorted([r for r in results if r["texts"]], key=lambda x: x["score"], reverse=True)
    return results

def classify_stage(entities: str, regulation_context: str):
    """
    Classify feature as:
    - Yes: legal obligation
    - No: business-only decision
    - Maybe: unclear, did not specify the intention when creating feature, needs human review

    Output JSON with keys: classification, reasoning, related_regulation.
    """
    prompt = f"""
    Entities extracted:
    {entities}

    Relevant regulation text:
    {regulation_context}

    Based on this information:
    1. Is there a clear legal obligation for this feature? Answer "Yes" if required by law/regulation, "No" if it's only a business decision, or "Maybe" if unclear and needs human review.
    2. Provide a short reasoning (1-2 sentences).
    3. If any related regulation/article is relevant, mention it concisely.

    Respond strictly in JSON format with keys: classification ("Yes", "No", "Maybe"), reasoning, related_regulation.
    """
    messages = [
        {"role": "system", "content": "You are a compliance classifier."},
        {"role": "user", "content": prompt}
    ]
    return chat_with_ollama(messages)

# ---------------------- Example Usage ----------------------
if __name__ == "__main__":
    feature = {
        "feature_name": "Creator fund payout tracking in CDS",
        "feature_description": """Monetization events will be tracked through CDS to detect anomalies in creator payouts. DRT rules apply for log trimming."""

    }

    try:
        # Step 1: Extract entities
        entities = extract_entities(feature["feature_name"], feature["feature_description"])
        print("\n--- Extracted Entities ---")
        print(entities)

        # Step 2: Search all laws for best match
        regulation_results = retrieve_best_regulation_text(feature["feature_description"], top_k=3)
        if not regulation_results:
            print("\n--- Regulation Context ---")
            print("No relevant regulation found.")
            regulation_context = ""
            related_regulation = ""
        else:
            best = regulation_results[0]
            regulation_context = "\n\n".join(best["texts"])
            related_regulation = best["source_file"]
            print("\n--- Regulation Context ---")
            print(f"Matched Law: {related_regulation}")
            print(regulation_context[:1000], "...")  # print preview

        # Step 3: Classification
        classification = classify_stage(entities, regulation_context)
        print("\n--- Classification ---")
        print(classification)

    except Exception as e:
        print("Error:", e)
