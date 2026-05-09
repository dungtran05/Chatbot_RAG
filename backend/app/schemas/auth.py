from pydantic import BaseModel, EmailStr, Field


# Dữ liệu frontend gửi lên khi đăng ký tài khoản.
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


# Dữ liệu frontend gửi lên khi đăng nhập.
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Thông tin user trả về frontend, không bao gồm password.
class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr


# Response sau khi đăng nhập/đăng ký thành công.
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

