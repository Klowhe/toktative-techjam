from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams
import os
from dotenv import load_dotenv


# ---------------------- Load Environment ----------------------
load_dotenv()
QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# ---------------------- Initialize Qdrant ----------------------

def init_qdrant(url=QDRANT_ENDPOINT, api_key=QDRANT_API_KEY):
    qdrant_client = QdrantClient(
    url=url,
    api_key=api_key
   
)
    return(qdrant_client)
    
def query_qdrant(qdrant_client, embedding: list, collection_name: str, top_k: int = 5):
    """
    Query Qdrant collection for top-k most similar points using query_points.
    """
    results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=embedding,
        limit=3
    )
    return results