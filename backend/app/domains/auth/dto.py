"""auth I/O 계약 (Pydantic). contracts SSOT — FE도 이 모양으로 타입 생성."""
from pydantic import BaseModel, EmailStr

from app.db.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: UserRole
    organization_id: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut
