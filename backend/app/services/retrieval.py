from collections import defaultdict

from qdrant_client.http.models import FieldCondition, Filter, MatchValue
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.embeddings import embed_texts
from app.services.query_expansion import generate_subqueries
from app.services.reranker import rerank
from app.services.vector_store import search_vectors
from app.services.web_search import tavily_search


def lexical_scores(query: str, docs: list[dict]) -> dict[str, float]:
    if not docs:
        return {}
    corpus = [query, *[doc["text"] for doc in docs]]
    try:
        matrix = TfidfVectorizer(stop_words="english").fit_transform(corpus)
        scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
        return {doc["id"]: float(score) for doc, score in zip(docs, scores, strict=True)}
    except ValueError:
        return {doc["id"]: 0.0 for doc in docs}


def reciprocal_rank_fusion(ranked_lists: list[list[dict]], k: int = 60) -> list[dict]:
    scored: dict[str, dict] = {}
    fused_scores = defaultdict(float)

    for docs in ranked_lists:
        for rank, doc in enumerate(docs, start=1):
            doc_id = doc["id"]
            fused_scores[doc_id] += 1.0 / (k + rank)
            scored[doc_id] = doc

    fused = []
    for doc_id, score in fused_scores.items():
        item = {**scored[doc_id], "fusion_score": score}
        fused.append(item)
    fused.sort(key=lambda item: item["fusion_score"], reverse=True)
    return fused


def hybrid_search(user_id: str, query: str, minimum_context: int = 4) -> tuple[list[str], list[dict]]:
    queries = generate_subqueries(query)
    vector_rankings: list[list[dict]] = []
    lexical_candidates: list[dict] = []

    for expanded_query in queries:
        vector = embed_texts([expanded_query])[0]
        hits = search_vectors(
            vector,
            limit=12,
            query_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            ),
        )
        ranked = []
        for hit in hits:
            payload = hit.payload or {}
            doc_id = str(hit.id)
            item = {
                "id": doc_id,
                "text": payload.get("text", ""),
                "header": payload.get("header"),
                "filename": payload.get("filename"),
                "document_id": payload.get("document_id"),
                "source": payload.get("filename"),
                "source_type": payload.get("source_type", "document"),
                "vector_score": float(hit.score),
            }
            ranked.append(item)
        vector_rankings.append(ranked)
        lexical_candidates.extend(ranked)

    lexical_map = {doc["id"]: doc for doc in lexical_candidates}
    lexical_list = list(lexical_map.values())
    lex_scores = lexical_scores(query, lexical_list)
    lexical_ranked = [{**doc, "lexical_score": lex_scores.get(doc["id"], 0.0)} for doc in lexical_list]
    lexical_ranked.sort(key=lambda item: item["lexical_score"], reverse=True)

    fused = reciprocal_rank_fusion([*vector_rankings, lexical_ranked])
    reranked = rerank(query, fused, top_k=minimum_context + 4)

    if len(reranked) < minimum_context:
        web_results = tavily_search(query)
        for index, item in enumerate(web_results):
            reranked.append(
                {
                    "id": f"web-{index}",
                    "text": item["text"],
                    "header": item.get("title"),
                    "filename": item.get("title"),
                    "document_id": None,
                    "source": item["source"],
                    "source_type": "web",
                    "vector_score": 0.0,
                    "rerank_score": 0.0,
                }
            )

    return queries, reranked[:8]
