import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)


def build_context(chunks: list[dict]) -> str:
    parts = []
    for index, chunk in enumerate(chunks, start=1):
        label = chunk.get("source") or "unknown"
        header = chunk.get("header") or "General"
        text = chunk.get("text", "")
        parts.append(f"[{index}] Source: {label}\nHeader: {header}\nContent:\n{text}")
    return "\n\n".join(parts)


def answer_question(question: str, chunks: list[dict]) -> str:
    model = genai.GenerativeModel(settings.gemini_model)
    context = build_context(chunks)
    prompt = f"""
You are a retrieval-augmented assistant.
Use only the provided context when possible.
If context is weak or incomplete, clearly say what is uncertain.
Answer in Vietnamese.

Question:
{question}

Context:
{context}
"""
    response = model.generate_content(prompt)
    return response.text.strip()

