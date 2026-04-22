import json

import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)


def generate_subqueries(query: str) -> list[str]:
    model = genai.GenerativeModel(settings.gemini_model)
    prompt = f"""
Create up to 4 focused retrieval sub-queries for the user question below.
Return JSON with this exact shape: {{"queries": ["..."]}}
Question: {query}
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(text)
        queries = [item.strip() for item in data.get("queries", []) if item.strip()]
        deduped = []
        for item in [query, *queries]:
            if item not in deduped:
                deduped.append(item)
        return deduped[:5]
    except Exception:
        return [query]
