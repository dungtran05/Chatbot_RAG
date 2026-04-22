from fastapi import APIRouter, HTTPException, status

from app.db.mongo import get_database
from app.models.collections import USERS_COLLECTION
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserResponse
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserCreate):
    db = get_database()
    existing = await db[USERS_COLLECTION].find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    user = {"name": payload.name, "email": payload.email, "password": hash_password(payload.password)}
    result = await db[USERS_COLLECTION].insert_one(user)
    user_id = str(result.inserted_id)
    token = create_access_token(user_id)
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user_id, name=payload.name, email=payload.email),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    db = get_database()
    user = await db[USERS_COLLECTION].find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user_id = str(user["_id"])
    token = create_access_token(user_id)
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user_id, name=user["name"], email=user["email"]),
    )
