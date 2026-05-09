from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.mongo import get_database
from app.models.collections import USERS_COLLECTION
from app.utils.security import decode_access_token

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Dependency dùng chung cho các API cần đăng nhập.
    # Token được gửi từ frontend qua header Authorization: Bearer <token>.
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload["sub"]
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    db = get_database()
    # Kiểm tra user trong MongoDB để đảm bảo token thuộc về user thật.
    user = await db[USERS_COLLECTION].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

