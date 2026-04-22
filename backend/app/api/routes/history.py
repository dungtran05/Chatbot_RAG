from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.mongo import get_database
from app.models.collections import CONVERSATIONS_COLLECTION
from app.schemas.history import ConversationResponse, MessageItem

router = APIRouter()


@router.get("", response_model=list[ConversationResponse])
async def list_history(current_user=Depends(get_current_user)):
    db = get_database()
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

