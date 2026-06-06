"""채팅 유스케이스 — 세션/메시지 영속 + mock 에이전트 스트리밍."""
import uuid
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.chat.agent import ChatAgent
from app.ai.kernel.registry import registry
from app.contracts.chat_api import (
    ChatMessageOut,
    ChatSessionOut,
    CreateChatSessionRequest,
    SendChatMessageRequest,
)
from app.domains.chat.repository import ChatRepository
from app.models.chat import ChatMessage, ChatSession
from app.models.enums import ChatRole
from app.shared.exceptions import AppException
from app.shared.project_access import assert_project_member
from app.shared.schemas import ErrorCode


def _ensure_chat_agent() -> ChatAgent:
    if not registry.has("chat"):
        registry.register(ChatAgent())
    return registry.get("chat")  # type: ignore[return-value]


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ChatRepository(db)

    @staticmethod
    def _session_out(s: ChatSession) -> ChatSessionOut:
        return ChatSessionOut(
            id=s.id,
            user_id=s.user_id,
            project_id=s.project_id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )

    @staticmethod
    def _message_out(m: ChatMessage) -> ChatMessageOut:
        return ChatMessageOut(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            meta=m.meta,
            tokens_used=m.tokens_used,
            created_at=m.created_at,
        )

    async def create_session(
        self, user_id: str, body: CreateChatSessionRequest
    ) -> ChatSessionOut:
        if body.project_id:
            await assert_project_member(self.db, body.project_id, uuid.UUID(user_id))
        session = ChatSession(
            user_id=uuid.UUID(user_id),
            project_id=body.project_id,
            title=body.title,
        )
        self.repo.add_session(session)
        await self.db.commit()
        await self.db.refresh(session)
        return self._session_out(session)

    async def list_sessions(self, user_id: str) -> list[ChatSessionOut]:
        sessions = await self.repo.list_sessions(uuid.UUID(user_id))
        return [self._session_out(s) for s in sessions]

    async def list_messages(self, session_id: uuid.UUID, user_id: str) -> list[ChatMessageOut]:
        session = await self._get_owned(session_id, user_id)
        messages = await self.repo.list_messages(session.id)
        return [self._message_out(m) for m in messages]

    async def stream_reply(
        self,
        session_id: uuid.UUID,
        user_id: str,
        body: SendChatMessageRequest,
    ) -> AsyncIterator[dict]:
        session = await self._get_owned(session_id, user_id)
        user_msg = ChatMessage(
            session_id=session.id,
            role=ChatRole.user,
            content=body.content,
            meta=body.meta,
        )
        self.repo.add_message(user_msg)
        await self.db.commit()

        yield {
            "type": "user_message",
            "message": self._message_out(user_msg).model_dump(mode="json"),
        }

        agent = _ensure_chat_agent()
        full_parts: list[str] = []
        async for chunk in agent.stream(
            {"content": body.content, "meta": body.meta, "session_id": str(session.id)}
        ):
            full_parts.append(chunk)
            yield {"type": "token", "content": chunk}

        content = "".join(full_parts)
        assistant = ChatMessage(
            session_id=session.id,
            role=ChatRole.assistant,
            content=content,
            meta=body.meta,
            tokens_used=len(content.split()),
        )
        self.repo.add_message(assistant)
        await self.db.commit()
        await self.db.refresh(assistant)
        yield {
            "type": "done",
            "message": self._message_out(assistant).model_dump(mode="json"),
        }

    async def _get_owned(self, session_id: uuid.UUID, user_id: str) -> ChatSession:
        session = await self.repo.get_session(session_id, uuid.UUID(user_id))
        if not session:
            raise AppException(ErrorCode.NOT_FOUND, "채팅 세션을 찾을 수 없습니다", 404)
        return session
