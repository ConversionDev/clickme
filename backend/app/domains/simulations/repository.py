"""simulations 영속 계층."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad
from app.models.project import Project, ProjectMember
from app.models.report import Report
from app.models.simulation import PersonaResponse, Simulation


class SimulationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_project(self, project_id: uuid.UUID) -> Project | None:
        return await self.db.get(Project, project_id)

    async def is_project_member(self, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        res = await self.db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        return res.scalar_one_or_none() is not None

    async def get_ad_for_project(self, ad_id: uuid.UUID, project_id: uuid.UUID) -> Ad | None:
        res = await self.db.execute(
            select(Ad).where(Ad.id == ad_id, Ad.project_id == project_id)
        )
        return res.scalar_one_or_none()

    async def create_simulation(self, sim: Simulation) -> Simulation:
        self.db.add(sim)
        await self.db.flush()
        return sim

    async def get_simulation(self, simulation_id: uuid.UUID) -> Simulation | None:
        return await self.db.get(Simulation, simulation_id)

    async def list_by_project(self, project_id: uuid.UUID) -> list[Simulation]:
        res = await self.db.execute(
            select(Simulation)
            .where(Simulation.project_id == project_id)
            .order_by(Simulation.created_at.desc())
        )
        return list(res.scalars().all())

    def add_persona_responses(self, rows: list[PersonaResponse]) -> None:
        self.db.add_all(rows)

    def add_report(self, report: Report) -> None:
        self.db.add(report)
