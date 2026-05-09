from fastapi import APIRouter

from app.api.routes import auth, chat, documents, history

api_router = APIRouter()

# Gom các nhóm route để frontend gọi theo từng chức năng.
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(history.router, prefix="/history", tags=["history"])

