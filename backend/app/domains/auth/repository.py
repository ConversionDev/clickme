"""auth 영속 계층 (SQLAlchemy Async)."""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.models.user import User


class AuthRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        res = await self.db.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> User | None:
        return await self.db.get(User, uuid.UUID(user_id))

    def add_refresh_token(self, user_id: uuid.UUID, token_hash: str, expires_at: datetime) -> None:
        self.db.add(RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at))

    async def get_refresh_token(self, token_hash: str) -> RefreshToken | None:
        res = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return res.scalar_one_or_none()
