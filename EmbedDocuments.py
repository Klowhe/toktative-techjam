import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams
import uuid
from dotenv import load_dotenv
import os
load_dotenv()  # load variables from .env file
QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# -------------------------------
# 1️⃣ Setup Ollama embedding call
# -------------------------------
def get_embedding(text, model="mxbai-embed-large"):
    url = "http://127.0.0.1:11434/api/embeddings"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": text   # Use 'prompt' for Ollama embeddings
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["embedding"]

# -------------------------------
# 2️⃣ Setup Qdrant client with API key
# -------------------------------
endpoint = "https://37557055-77c3-4abd-9f99-ed908b82ff44.europe-west3-0.gcp.cloud.qdrant.io"
qdrant_client = QdrantClient(url=endpoint, api_key=QDRANT_API_KEY)


collection_name = "regulations"

# Create collection if it doesn't exist
# existing_collections = [c.name for c in qdrant_client.get_collections().collections]
# if collection_name not in existing_collections:
#     qdrant_client.recreate_collection(
#         collection_name=collection_name,
#         vectors_config=VectorParams(size=1024, distance="Cosine")  # mxbai-embed-large is 1024 dims
#     )

# -------------------------------
# 3️⃣ Example documents
# -------------------------------
# documents = [
#     "Why is the sky blue?",
#     "What causes rainbows?",
#     "Explain quantum entanglement in simple terms.",
#     "Tips for baking a chocolate cake."
# ]

# -------------------------------
# 4️⃣ Generate embeddings and insert into Qdrant
# -------------------------------
# points = []
# for doc in documents:
#     embedding = get_embedding(doc)
#     points.append({
#         "id": str(uuid.uuid4()),
#         "vector": embedding,
#         "payload": {"text": doc}
#     })

# qdrant_client.upsert(
#     collection_name=collection_name,
#     points=points
# )
# print(f"Inserted {len(points)} documents into Qdrant.")

# -------------------------------
# 5️⃣ Query Qdrant for similar documents
# -------------------------------
query_text = "What comes after rain?"
query_embedding = get_embedding(query_text)

search_results = qdrant_client.search(
    collection_name=collection_name,
    query_vector=query_embedding,
    limit=3
)

print("\nTop 3 similar documents:")
for res in search_results:
    print(f"Score: {res.score:.4f}, Text: {res.payload['text']}")
