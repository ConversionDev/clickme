"""ads 영속 계층."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad


class AdRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_project(self, project_id: uuid.UUID) -> list[Ad]:
        res = await self.db.execute(
            select(Ad).where(Ad.project_id == project_id).order_by(Ad.created_at.desc())
        )
        return list(res.scalars().all())

    async def get(self, ad_id: uuid.UUID) -> Ad | None:
        return await self.db.get(Ad, ad_id)

    def add(self, ad: Ad) -> None:
        self.db.add(ad)
