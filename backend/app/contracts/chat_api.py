"""채팅 HTTP·SSE 계약."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.enums import ChatRole


class CreateChatSessionRequest(BaseModel):
    project_id: UUID | None = None
    title: str = Field(default="새 채팅", max_length=200)


class ChatSessionOut(BaseModel):
    id: UUID
    user_id: UUID
    project_id: UUID | None
    title: str
    created_at: datetime
    updated_at: datetime


class ChatMessageOut(BaseModel):
    id: UUID
    session_id: UUID
    role: ChatRole
    content: str
    meta: dict | None = None
    tokens_used: int | None = None
    created_at: datetime


class SendChatMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    meta: dict | None = None
