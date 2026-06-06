"""chat 라우터 — 세션·메시지·SSE 스트리밍."""
import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.chat_api import (
    ChatMessageOut,
    ChatSessionOut,
    CreateChatSessionRequest,
    SendChatMessageRequest,
)
from app.domains.chat.service import ChatService
from app.shared.db import get_db
from app.shared.deps import CurrentUser, get_current_user
from app.shared.schemas import ApiResponse, ok

router = APIRouter(prefix="/api/chat", tags=["chat"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.get("/sessions", response_model=ApiResponse[list[ChatSessionOut]])
async def list_sessions(user: UserDep, db: DbDep) -> ApiResponse[list[ChatSessionOut]]:
    return ok(await ChatService(db).list_sessions(user.id))


@router.post("/sessions", response_model=ApiResponse[ChatSessionOut])
async def create_session(
    body: CreateChatSessionRequest, user: UserDep, db: DbDep
) -> ApiResponse[ChatSessionOut]:
    return ok(await ChatService(db).create_session(user.id, body))


@router.get("/sessions/{session_id}/messages", response_model=ApiResponse[list[ChatMessageOut]])
async def list_messages(
    session_id: UUID, user: UserDep, db: DbDep
) -> ApiResponse[list[ChatMessageOut]]:
    return ok(await ChatService(db).list_messages(session_id, user.id))


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: UUID,
    body: SendChatMessageRequest,
    user: UserDep,
    db: DbDep,
) -> StreamingResponse:
    service = ChatService(db)

    async def sse():
        async for event in service.stream_reply(session_id, user.id, body):
            event_type = event.get("type", "message")
            yield f"event: {event_type}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
