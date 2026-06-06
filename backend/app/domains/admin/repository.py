"""admin 영속 계층."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatSession
from app.models.organization import Organization
from app.models.simulation import Simulation
from app.models.user import User
from app.models.enums import SimulationStatus


class AdminRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_users(self) -> list[User]:
        res = await self.db.execute(select(User).order_by(User.created_at.desc()))
        return list(res.scalars().all())

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        return await self.db.get(User, user_id)

    async def email_exists(self, email: str) -> bool:
        res = await self.db.execute(select(User.id).where(User.email == email))
        return res.scalar_one_or_none() is not None

    def add_user(self, user: User) -> None:
        self.db.add(user)

    async def list_chat_sessions(self, limit: int = 50) -> list[tuple[ChatSession, str, int]]:
        res = await self.db.execute(
            select(ChatSession, User.email)
            .join(User, User.id == ChatSession.user_id)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
        )
        rows: list[tuple[ChatSession, str, int]] = []
        for session, email in res.all():
            cnt = await self.db.scalar(
                select(func.count())
                .select_from(ChatMessage)
                .where(ChatMessage.session_id == session.id)
            )
            rows.append((session, email, int(cnt or 0)))
        return rows

    async def usage_stats(self) -> dict[str, int]:
        users = await self.db.scalar(select(func.count()).select_from(User)) or 0
        orgs = await self.db.scalar(select(func.count()).select_from(Organization)) or 0
        sims = await self.db.scalar(select(func.count()).select_from(Simulation)) or 0
        completed = (
            await self.db.scalar(
                select(func.count())
                .select_from(Simulation)
                .where(Simulation.status == SimulationStatus.completed)
            )
            or 0
        )
        chats = await self.db.scalar(select(func.count()).select_from(ChatSession)) or 0
        return {
            "user_count": users,
            "organization_count": orgs,
            "simulation_count": sims,
            "completed_simulations": completed,
            "chat_session_count": chats,
        }
