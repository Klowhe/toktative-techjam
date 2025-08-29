import os
import requests
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import google.generativeai as genai
import json
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

TERMINOLOGY_DICT = """
Terminology Dictionary:
- NR = Not recommended
- PF = Personalized feed
- GH = Geo-handler; a module responsible for routing features based on user region
- CDS = Compliance Detection System
- DRT = Data retention threshold; duration for which logs can be stored
- LCP = Local compliance policy
- Redline = Flag for legal review (different from its traditional business use for 'financial loss')
- Softblock = A user-level limitation applied silently without notifications
- Spanner = A synthetic name for a rule engine (not to be confused with Google Spanner)
- ShadowMode = Deploy feature in non-user-impact way to collect analytics only
- T5 = Tier 5 sensitivity data; more critical than T1‚ÄìT4 in this internal taxonomy
- ASL = Age-sensitive logic
- Glow = A compliance-flagging status, internally used to indicate geo-based alerts
- NSP = Non-shareable policy (content should not be shared externally)
- Jellybean = Feature name for internal parental control system
- EchoTrace = Log tracing mode to verify compliance routing
- BB = Baseline Behavior; standard user behavior used for anomaly detection
- Snowcap = A synthetic codename for the child safety policy framework
- FR = Feature rollout status
- IMT = Internal monitoring trigger
"""


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

    Here is a terminology dictionary:
    {TERMINOLOGY_DICT}

    Based on this information:
    1. Reference the terminology dictionary for technical terminologies and abbreviations.
    2. Answer "Yes" if feature required by law/regulation in specific regions, "No" if it's only a business decision, or "Maybe" if does not state clearly intention to develop this feature and need more human information.
    3. Provide a short reasoning (1-2 sentences) to whether this feature is required to comply with legal regulations of specific regions.
    4. If any related regulation/article is relevant, mention it concisely, otherwise use "None".

    Based on all input, respond strictly in JSON **with exactly these keys**:
    "classification": "Yes" | "No" | "Maybe",
    "reasoning": "1-2 sentence reasoning",
    "related_regulation": "main law or article name"

    Rules:
    - Do not create lists or nested objects. Combine all reasoning into one string.
    - Do not infer regulatory requirements if none are explicitly mentioned in the feature description or extracted entities.
    """
    messages = [
        {"role": "system", "content": "You are a compliance classifier."},
        {"role": "user", "content": prompt}
    ]
    return chat_with_ollama(messages)

def classify_stage_gemini(entities: str, regulation_context: str):
    """
    Use Gemini to classify feature as legal obligation/business-only/unclear.
    Output JSON with keys: classification, reasoning, related_regulation.
    The output should be a single JSON object.
    """
    genai.configure(api_key=GEMINI_KEY)
    try:
        model_name = "models/gemini-2.0-flash-exp"
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Entities extracted:
        {entities}

        Relevant regulation text:
        {regulation_context}

        Here is a terminology dictionary:
        {TERMINOLOGY_DICT}

        Based on this information:
        1. Reference the terminology dictionary for technical terminologies and abbreviations.
        2. Answer "Yes" if feature required by law/regulation in specific regions, "No" if it's only a business decision, or "Maybe" if does not state clearly intention to develop this feature and need more human information.
        3. Provide a short reasoning (1-2 sentences) to whether this feature is required to comply with legal regulations of specific regions.
        4. If any related regulation/article is relevant, mention it concisely, otherwise use "None".

        Respond strictly in JSON format with keys: classification ("Yes", "No", "Maybe"), reasoning, related_regulation.
        """
        response = model.generate_content(prompt)
        # --- Clean Gemini output before parsing ---
        text = response.text.strip()
        # Remove code block markers if present
        if text.startswith("```"):
            # Remove first line (e.g., ```json) and last line (```)
            lines = text.splitlines()
            # Remove lines starting/ending with ```
            lines = [line for line in lines if not line.strip().startswith("```") and not line.strip().endswith("```")]
            text = "\n".join(lines).strip()
        try:
            return json.loads(text)
        except Exception:
            return {"classification": "Maybe", "reasoning": "Gemini output not valid JSON", "related_regulation": ""}
    except Exception as e:
        print("Gemini model error:", e)
        return {"classification": "Maybe", "reasoning": "Gemini model error", "related_regulation": ""}

def compute_reward(ollama_result, gemini_result):
    """
    Compare Ollama and Gemini classification and assign reward.
    """
    ollama_cls = ollama_result.get("classification", "").strip().lower()
    gemini_cls = gemini_result.get("classification", "").strip().lower()
    print(f"DEBUG: ollama_cls='{ollama_cls}', gemini_cls='{gemini_cls}'")  # <--- Add this line
    if ollama_cls == gemini_cls:
        return 5  # positive reward
    elif ollama_cls == "maybe" and gemini_cls in ("yes", "no"):
        return -1  # unsure, less penalty
    elif gemini_cls == "maybe" and ollama_cls in ("yes", "no"):
        return -1
    else:
        return -5  

# ---------------------- Example Usage ----------------------
if __name__ == "__main__":
    # Read features from Excel file
    input_path = "/Users/caophuong/Documents/features.xlsx"
    output_path = "/Users/caophuong/Documents/features_analysis.csv"
    df = pd.read_excel(input_path)
    results = []

    for idx, row in df.iterrows():
        feature_name = row["feature_name"]
        feature_description = row["feature_description"]

        try:
            # Step 1: Extract entities
            entities = extract_entities(feature_name, feature_description)

            # Step 2: Search all laws for best match
            regulation_results = retrieve_best_regulation_text(feature_description, top_k=3)
            if not regulation_results:
                regulation_context = ""
                related_regulation = ""
            else:
                best = regulation_results[0]
                regulation_context = "\n\n".join(best["texts"])
                related_regulation = best["source_file"]

            # Step 3: Classification (Ollama)
            import json
            classification = classify_stage(entities, regulation_context)
            try:
                ollama_result = json.loads(classification)
                ollama_cls = ollama_result.get("classification", "")
            except Exception:
                ollama_result = {"classification": "Maybe", "reasoning": "Ollama output not valid JSON", "related_regulation": ""}
                ollama_cls = "Maybe"

            # Step 4: Classification (Gemini)
            gemini_result = classify_stage_gemini(entities, regulation_context)
            gemini_cls = gemini_result.get("classification", "")
            if gemini_cls == "":
                print(f"Gemini classification is empty for feature '{feature_name}'. Reasoning: {gemini_result.get('reasoning', '')}")

            # Step 5: Reward calculation
            reward = compute_reward(ollama_result, gemini_result)

            # Store result
            results.append({
                "feature_name": feature_name,
                "feature_description": feature_description,
                "ollama_classification": ollama_cls,
                "gemini_classification": gemini_cls,
                "reward": reward
            })
        except Exception as e:
            results.append({
                "feature_name": feature_name,
                "feature_description": feature_description,
                "ollama_classification": "Error",
                "gemini_classification": "Error",
                "reward": "Error"
            })

    # Save results to CSV
    out_df = pd.DataFrame(results)
    out_df.to_csv(output_path, index=False)
    print(f"Analysis complete. Results saved to {output_path}")