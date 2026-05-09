from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo():
    # Tạo kết nối MongoDB khi FastAPI khởi động.
    global client, database
    client = AsyncIOMotorClient(settings.mongodb_uri)
    database = client[settings.mongodb_db]


async def disconnect_mongo():
    # Đóng kết nối MongoDB khi backend tắt.
    global client
    if client:
        client.close()


def get_database() -> AsyncIOMotorDatabase:
    # Hàm dùng chung để các route/service lấy database hiện tại.
    if database is None:
        raise RuntimeError("MongoDB is not initialized")
    return database

