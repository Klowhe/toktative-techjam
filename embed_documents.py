import json
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
import os
from dotenv import load_dotenv
import uuid

# ---------------------- Load Environment ----------------------
load_dotenv()
QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# ---------------------- Ollama Settings ----------------------
OLLAMA_URL = "http://127.0.0.1:11434/api/embeddings"  # default serve URL
OLLAMA_MODEL = "mxbai-embed-large"     # replace with your model name

def get_embedding(text):
    """Get embedding from local Ollama server via HTTP."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": text
    }
    response = requests.post(f"{OLLAMA_URL}", json=payload)
    response.raise_for_status()
    return response.json()["embedding"]

# ---------------------- Load Chunks ----------------------
with open("chunks_output.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# ---------------------- Initialize Qdrant ----------------------
qdrant_client = QdrantClient(
    url=QDRANT_ENDPOINT,
    api_key=QDRANT_API_KEY
)

# ---------------------- Upload Chunks ----------------------
SOURCE_COLLECTION_MAP = {
    "eu_dsa.pdf": "eu_regulation",
    "fl_bill.pdf": "fl_regulation",
    "utah_regulation_act.pdf": "ut_regulation",
    "ncmec.pdf": "ncmec_regulation",
    "ca_poksmaa.pdf": "ca_regulation"
}

for chunk_text, meta in chunks:
    source_file = meta.get("source_file", "").lower()
    collection_name = SOURCE_COLLECTION_MAP.get(source_file)

    if collection_name:
        try:
            # 1. Get embedding
            embedding = get_embedding(chunk_text)

            # 2. Prepare point
            point = PointStruct(id=str(uuid.uuid4()), vector=embedding, payload=meta)

            # 3. Upsert to Qdrant
            qdrant_client.upsert(collection_name=collection_name, points=[point])
            print(f"Uploaded chunk to {collection_name}: {meta.get('section_heading', '')}")

        except Exception as e:
            print(f"Error uploading chunk from {source_file}: {e}")