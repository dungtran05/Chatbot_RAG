from datetime import UTC, datetime
from uuid import uuid4

from bson import ObjectId
from qdrant_client.http.models import PointStruct

from app.core.config import settings
from app.db.mongo import get_database
from app.models.collections import DOCUMENTS_COLLECTION
from app.services.chunking import chunk_by_header
from app.services.embeddings import embed_texts
from app.services.file_parser import extract_text_from_upload
from app.services.vector_store import upsert_chunks


async def save_upload_and_index(user_id: str, filename: str, content_type: str, file_bytes: bytes) -> dict:
    db = get_database()
    user_upload_dir = settings.upload_path / user_id
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_upload_dir / filename
    file_path.write_bytes(file_bytes)

    extracted_text = extract_text_from_upload(filename, file_bytes)
    chunks = chunk_by_header(extracted_text)
    vectors = embed_texts([chunk["text"] for chunk in chunks]) if chunks else []

    document = {
        "user_id": user_id,
        "filename": filename,
        "content_type": content_type,
        "path": str(file_path),
        "uploaded_at": datetime.now(UTC),
        "chunk_count": len(chunks),
    }
    result = await db[DOCUMENTS_COLLECTION].insert_one(document)
    document_id = str(result.inserted_id)

    points = []
    for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "user_id": user_id,
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": index,
                    "header": chunk["header"],
                    "text": chunk["text"],
                    "source_type": "document",
                },
            )
        )
    if points:
        upsert_chunks(points)

    document["_id"] = ObjectId(document_id)
    return document
