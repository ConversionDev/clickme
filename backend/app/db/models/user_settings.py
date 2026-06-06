"""사용자 설정 (테마·알림)."""
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class UserSettings(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    theme: Mapped[str] = mapped_column(String(10), nullable=False, default="light")
    notifications: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
