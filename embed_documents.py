import json
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams
import os
from dotenv import load_dotenv
import uuid

# ---------------------- Load Environment ----------------------
load_dotenv()
QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# ---------------------- Ollama Settings ----------------------
OLLAMA_URL = "http://127.0.0.1:11434/api/embeddings"  # Ollama local embed endpoint
OLLAMA_MODEL = "mxbai-embed-large"                     # Replace with your embedding model
EMBED_DIM = 1024  # Must match your Ollama embedding model output dimension

# ---------------------- Initialize Qdrant ----------------------
qdrant_client = QdrantClient(
    url=QDRANT_ENDPOINT,
    api_key=QDRANT_API_KEY
)

# ---------------------- Load Chunks ----------------------
with open("chunks_output.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)  # Expecting a list of (chunk_text, metadata) tuples

# ---------------------- Source to Collection Mapping ----------------------
SOURCE_COLLECTION_MAP = {
    "eu_dsa.pdf": "eu_regulation",
    "fl_bill.pdf": "fl_regulation",
    "utah_regulation_act.pdf": "ut_regulation",
    "ncmec.pdf": "ncmec_regulation",
    "ca_poksmaa.pdf": "ca_regulation"
}

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

# ---------------------- Upload Chunks ----------------------

# Keep track of collections already created in this run
created_collections = set()

for chunk_text, meta in chunks:
    source_file = meta.get("source_file", "").lower()
    collection_name = SOURCE_COLLECTION_MAP.get(source_file)

    if not collection_name:
        print(f"Skipping unknown source_file: {source_file}")
        continue

    # 1. Create collection if it doesn't exist
    if collection_name not in created_collections:
        existing_collections = [c.name for c in qdrant_client.get_collections().collections]
        if collection_name not in existing_collections:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=EMBED_DIM, distance="Cosine")
            )
            print(f"Created collection: {collection_name}")
        created_collections.add(collection_name)

    try:
        # 2. Get embedding from Ollama
        embedding = get_embedding(chunk_text)

        # 3. Prepare payload
        payload = {
            "text": chunk_text,  # actual chunk text
            "metadata": meta     # metadata dictionary
        }

        # 4. Upsert to Qdrant
        point = PointStruct(id=str(uuid.uuid4()), vector=embedding, payload=payload)
        qdrant_client.upsert(collection_name=collection_name, points=[point])

        print(f"Uploaded chunk to {collection_name}: {meta.get('section_heading', '')}")

    except Exception as e:
        print(f"Error uploading chunk from {source_file}: {e}")
