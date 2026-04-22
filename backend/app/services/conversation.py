from datetime import UTC, datetime

from bson import ObjectId

from app.db.mongo import get_database
from app.models.collections import CONVERSATIONS_COLLECTION


async def append_conversation(user_id: str, conversation_id: str | None, user_message: str, answer: str) -> str:
    db = get_database()
    now = datetime.now(UTC)
    messages = [
        {"role": "user", "content": user_message, "created_at": now},
        {"role": "assistant", "content": answer, "created_at": now},
    ]

    if conversation_id:
        await db[CONVERSATIONS_COLLECTION].update_one(
            {"_id": ObjectId(conversation_id), "user_id": user_id},
            {"$push": {"messages": {"$each": messages}}, "$set": {"updated_at": now}},
        )
        return conversation_id

    doc = {
        "user_id": user_id,
        "title": user_message[:50],
        "messages": messages,
        "updated_at": now,
        "created_at": now,
    }
    result = await db[CONVERSATIONS_COLLECTION].insert_one(doc)
    return str(result.inserted_id)

