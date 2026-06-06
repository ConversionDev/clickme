"""admin API 스키마."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole


class AdminUserOut(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    role: UserRole
    organization_id: UUID
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime


class CreateAdminUserRequest(BaseModel):
    organization_id: UUID
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)
    role: UserRole = UserRole.user


class PatchAdminUserRequest(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    role: UserRole | None = None
    is_active: bool | None = None


class AdminChatSessionOut(BaseModel):
    id: UUID
    user_id: UUID
    user_email: str
    project_id: UUID | None
    title: str
    message_count: int
    updated_at: datetime


class AdminUsageOut(BaseModel):
    user_count: int
    organization_count: int
    simulation_count: int
    completed_simulations: int
    chat_session_count: int
