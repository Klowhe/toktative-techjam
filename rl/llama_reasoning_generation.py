import os
import requests
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import google.generativeai as genai
import json
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import jsonschema
import numpy as np
import nltk
import pandas as pd

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


def retrieve_best_regulation_text(feature_description: str, top_k: int = 3):
    """
    Search all collections in SOURCE_COLLECTION_MAP and return the best matching law(s) and relevant text.
    Returns a list of dicts: [{"collection": ..., "source_file": ..., "texts": [...]}]
    """
    results = []
    embedding = get_embedding(feature_description)
    
    #This approach searches for top-k documents for every collection. Do we want to continue with this approach? Very time consuming
    for source_file, collection_name in SOURCE_COLLECTION_MAP.items():
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
    1. Answer "Yes" if required by law/regulation, "No" if it's only a business decision, or "Maybe" if does not state clearly intention to develop this feature and need more human information.
    2. Provide a short reasoning (1-2 sentences).
    3. If any related regulation/article is relevant, mention it concisely.

    Based on all input, respond strictly in JSON **with exactly these keys**:
    "classification": "Yes" | "No" | "Maybe",
    "reasoning": "1-2 sentence reasoning",
    "related_regulation": "main law or article name"
     
    Do not create lists or nested objects. Combine all reasoning into one string.
    """
    messages = [
        {"role": "system", "content": "You are a compliance classifier."},
        {"role": "user", "content": prompt}
    ]
    return chat_with_ollama(messages)

# --------------------------------------------
dataset_file_path = "/Users/zerongpeh/Desktop/Y4S1/hackathon_documents/tiktok_dataset.xlsx"
df = pd.read_excel(dataset_file_path)
reasoning_list = []
regulation_list = []
if __name__ == "__main__":
    for row in df.itertuples():
        feature = {
            "feature_name": row.feature_name,
            "feature_description": row.feature_description
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

            # Step 3: Classification and Reasoning(Ollama)
            classification = classify_stage(entities, regulation_context)
            print("\n--- Classification (Ollama) ---")
            print(classification)
            try:
                ollama_result = json.loads(classification)
                if isinstance(ollama_result, list):
                    final_result = ollama_result[0]  # take first item
                else:
                    final_result = ollama_result  # it's already a single object
            except Exception:
                final_result = {"classification": "Maybe", "reasoning": "Ollama output not valid JSON", "related_regulation": ""}
            reasoning_list.extend([final_result['reasoning']])
            regulation_list.extend([final_result['related_regulation']])
        except Exception as e:
            print("Error:", e)
            reasoning_list.append("Error during reasoning")
            regulation_list.append("Error during reasoning")
    
    df['ollama_reasoning'] = reasoning_list
    df['related_regulation'] = regulation_list
    output_path = "/Users/zerongpeh/Desktop/Y4S1/hackathon_documents/tiktok_dataset_with_ollama_reasoning.xlsx"
    df.to_excel(output_path, index=False)
    print(f"Saved results to {output_path}")
