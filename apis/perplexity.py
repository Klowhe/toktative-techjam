import requests

def query_perplexity_api(api_key, question):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",  # You can choose other models based on your needs
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses

    return response.json()


