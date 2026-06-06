"""chat 영속 계층."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatSession


class ChatRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_sessions(self, user_id: uuid.UUID) -> list[ChatSession]:
        res = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
        )
        return list(res.scalars().all())

    async def get_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession | None:
        res = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
        )
        return res.scalar_one_or_none()

    def add_session(self, session: ChatSession) -> None:
        self.db.add(session)

    async def list_messages(self, session_id: uuid.UUID) -> list[ChatMessage]:
        res = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(res.scalars().all())

    def add_message(self, message: ChatMessage) -> None:
        self.db.add(message)
