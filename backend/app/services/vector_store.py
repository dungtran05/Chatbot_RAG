from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FilterSelector, PointStruct, VectorParams

from app.core.config import settings
from app.services.embeddings import get_embedding_model


qdrant_client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)


def ensure_qdrant_collection():
    collections = [item.name for item in qdrant_client.get_collections().collections]
    if settings.qdrant_collection in collections:
        return
    size = get_embedding_model().get_sentence_embedding_dimension()
    qdrant_client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=size, distance=Distance.COSINE),
    )


def upsert_chunks(points: list[PointStruct]):
    qdrant_client.upsert(collection_name=settings.qdrant_collection, points=points)


def search_vectors(query_vector: list[float], limit: int, query_filter=None):
    return qdrant_client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        limit=limit,
        query_filter=query_filter,
    )


def delete_points(query_filter):
    qdrant_client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=FilterSelector(filter=query_filter),
    )
