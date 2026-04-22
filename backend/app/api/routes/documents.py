from pathlib import Path

from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from qdrant_client.http.models import FieldCondition, Filter, MatchValue

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.mongo import get_database
from app.models.collections import DOCUMENTS_COLLECTION
from app.schemas.document import DocumentResponse
from app.services.ingestion import save_upload_and_index
from app.services.vector_store import delete_points

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")

    document = await save_upload_and_index(str(current_user["_id"]), file.filename, file.content_type or "", contents)
    return DocumentResponse(
        id=str(document["_id"]),
        filename=document["filename"],
        content_type=document["content_type"],
        uploaded_at=document["uploaded_at"].isoformat(),
        chunk_count=document["chunk_count"],
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(current_user=Depends(get_current_user)):
    db = get_database()
    cursor = db[DOCUMENTS_COLLECTION].find({"user_id": str(current_user["_id"])}).sort("uploaded_at", -1)
    documents = await cursor.to_list(length=200)
    return [
        DocumentResponse(
            id=str(item["_id"]),
            filename=item["filename"],
            content_type=item["content_type"],
            uploaded_at=item["uploaded_at"].isoformat(),
            chunk_count=item.get("chunk_count", 0),
        )
        for item in documents
    ]


@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user=Depends(get_current_user)):
    db = get_database()
    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document id")
    document = await db[DOCUMENTS_COLLECTION].find_one(
        {"_id": ObjectId(document_id), "user_id": str(current_user["_id"])}
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    delete_points(
        Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=str(current_user["_id"]))),
                FieldCondition(key="document_id", match=MatchValue(value=document_id)),
            ]
        )
    )

    path = document.get("path")
    if path:
        file_path = Path(path)
        if file_path.exists():
            file_path.unlink()

    await db[DOCUMENTS_COLLECTION].delete_one({"_id": ObjectId(document_id)})
    return {"success": True, "document_id": document_id}
