import os
import httpx
from typing import List

# Free serverless inference API
MODEL_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

async def summarize_news(articles: List[dict]) -> str:
    """
    Takes a list of article dicts, extracts headlines, 
    and returns an AI-generated summary.
    """
    token = os.getenv("HF_TOKEN")
    if not token:
        return "AI Briefing unavailable: HF_TOKEN not set in environment."

    # Extract top 15-20 headlines to avoid context window limits
    headlines = [a["title"] for a in articles[:20]]
    text_to_summarize = " Summarize these news headlines into a single cohesive paragraph: " + " | ".join(headlines)

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": text_to_summarize,
        "parameters": {"max_length": 150, "min_length": 50, "do_sample": False}
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(MODEL_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and "summary_text" in result[0]:
                    return result[0]["summary_text"]
                return "Could not parse AI response."
            elif response.status_code == 503:
                return "AI model is currently loading... please try again in a minute."
            else:
                return f"AI Briefing Error: {response.status_code} - {response.text[:100]}"
    except Exception as e:
        return f"AI Briefing Error: {str(e)}"
