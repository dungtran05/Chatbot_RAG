from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.mongo import connect_to_mongo, disconnect_mongo
from app.services.vector_store import ensure_qdrant_collection


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Khi backend khởi động: kết nối MongoDB và chuẩn bị collection vector trong Qdrant.
    await connect_to_mongo()
    ensure_qdrant_collection()
    yield
    # Khi backend tắt: đóng kết nối MongoDB.
    await disconnect_mongo()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # Cho phép frontend gọi API từ domain/port khác trong lúc phát triển.
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn toàn bộ API version 1 vào prefix /api/v1.
app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

