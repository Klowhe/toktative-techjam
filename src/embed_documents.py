import json
import requests
from api.qdrant_api import init_qdrant
from api.ollama_api import get_embedding
import os
from dotenv import load_dotenv
import uuid

# ---------------------- Load Chunks ----------------------
# with open("chunks_output.json", "r", encoding="utf-8") as f:
#     chunks = json.load(f)  # Expecting a list of (chunk_text, metadata) tuples
data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
chunks_file = os.path.join(data_folder, "chunks_output.json")

with open(chunks_file, "r", encoding="utf-8") as f:
    chunks = json.load(f) 

# ---------------------- Source to Collection Mapping ----------------------
SOURCE_COLLECTION_MAP = {
    "eu_dsa.pdf": "eu_regulation",
    "fl_bill.pdf": "fl_regulation",
    "utah_regulation_act.pdf": "ut_regulation",
    "ncmec.pdf": "ncmec_regulation",
    "ca_poksmaa.pdf": "ca_regulation"
}


# ---------------------- Upload Chunks ----------------------
qdrant_client = init_qdrant()
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
