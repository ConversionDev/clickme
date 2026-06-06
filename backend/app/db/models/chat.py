"""채팅 세션 + 메시지. (metadata는 SQLAlchemy 예약어 → 속성명 meta로 매핑)"""
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, CreatedAtMixin, TimestampMixin, UUIDMixin
from app.db.enums import ChatRole


class ChatSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="새 채팅")


class ChatMessage(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[ChatRole] = mapped_column(SAEnum(ChatRole, name="chat_role"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 컬럼명은 metadata, 속성명은 meta (SQLAlchemy 예약어 회피)
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
