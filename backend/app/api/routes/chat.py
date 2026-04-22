from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.config import settings
from app.services.conversation import append_conversation
from app.services.llm import answer_question
from app.services.retrieval import hybrid_search

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, current_user=Depends(get_current_user)):
    generated_queries, contexts = hybrid_search(str(current_user["_id"]), payload.message)
    answer = answer_question(payload.message, contexts)
    conversation_id = await append_conversation(
        str(current_user["_id"]), payload.conversation_id, payload.message, answer
    )
    citations = [
        {
            "index": index,
            "source": item.get("source"),
            "header": item.get("header"),
            "source_type": item.get("source_type", "document"),
        }
        for index, item in enumerate(contexts, start=1)
    ]
    return ChatResponse(
        answer=answer,
        citations=citations,
        retrieval={
            "generated_queries": generated_queries,
            "total_contexts": len(contexts),
            "used_web_fallback": any(item.get("source_type") == "web" for item in contexts),
        },
        metadata={
            "model": settings.gemini_model,
            "conversation_id": conversation_id,
        },
    )
