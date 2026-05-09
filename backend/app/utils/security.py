from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    # Hash mật khẩu trước khi lưu vào database.
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    # So sánh mật khẩu người dùng nhập với mật khẩu đã hash.
    return pwd_context.verify(password, hashed_password)


def create_access_token(subject: str) -> str:
    # Tạo JWT token, subject là user_id của người dùng.
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    # Giải mã token để lấy lại user_id khi request cần xác thực.
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
