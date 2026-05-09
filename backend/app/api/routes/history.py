from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.db.mongo import get_database
from app.models.collections import CONVERSATIONS_COLLECTION
from app.schemas.history import ConversationResponse, MessageItem

router = APIRouter()


@router.get("", response_model=list[ConversationResponse])
async def list_history(current_user=Depends(get_current_user)):
    db = get_database()
    # Lấy lịch sử trò chuyện của user hiện tại, mới nhất lên trước.
    cursor = db[CONVERSATIONS_COLLECTION].find({"user_id": str(current_user["_id"])}).sort("updated_at", -1)
    conversations = await cursor.to_list(length=100)
    return [
        ConversationResponse(
            id=str(item["_id"]),
            title=item.get("title", "Untitled"),
            updated_at=item["updated_at"].isoformat(),
            messages=[
                MessageItem(
                    role=message["role"],
                    content=message["content"],
                    created_at=message["created_at"].isoformat(),
                )
                for message in item.get("messages", [])
            ],
        )
        for item in conversations
    ]


@router.delete("/{conversation_id}")
async def delete_history(conversation_id: str, current_user=Depends(get_current_user)):
    # Kiểm tra id hợp lệ trước khi thao tác với MongoDB.
    if not ObjectId.is_valid(conversation_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation id")

    # Chỉ xóa conversation thuộc về user đang đăng nhập.
    db = get_database()
    result = await db[CONVERSATIONS_COLLECTION].delete_one(
        {"_id": ObjectId(conversation_id), "user_id": str(current_user["_id"])}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return {"success": True, "conversation_id": conversation_id}

