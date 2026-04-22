from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.core.config import settings


@lru_cache
def get_rerank_model() -> CrossEncoder:
    return CrossEncoder(settings.rerank_model)


def rerank(query: str, documents: list[dict], top_k: int = 8) -> list[dict]:
    if not documents:
        return []
    pairs = [(query, doc["text"]) for doc in documents]
    scores = get_rerank_model().predict(pairs)
    reranked = []
    for doc, score in zip(documents, scores, strict=True):
        enriched = {**doc, "rerank_score": float(score)}
        reranked.append(enriched)
    reranked.sort(key=lambda item: item["rerank_score"], reverse=True)
    return reranked[:top_k]

