"""reports 유스케이스 — 조회·대시보드."""

import uuid

from app.db.enums import SimulationStatus
from app.db.models.report import Report
from app.db.models.simulation import Simulation
from app.domains.reports.dto import DashboardOut, ReportOut
from app.shared.envelope import ErrorCode
from app.shared.exceptions import AppException
from app.shared.project_access import assert_project_member, list_member_project_ids
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ReportService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def _out(r: Report) -> ReportOut:
        return ReportOut(
            id=r.id,
            simulation_id=r.simulation_id,
            report_data=r.report_data,
            pdf_url=r.pdf_url,
            disclaimer=r.disclaimer,
            created_at=r.created_at,
        )

    async def get_by_simulation(self, simulation_id: uuid.UUID, user_id: str) -> ReportOut:
        sim = await self.db.get(Simulation, simulation_id)
        if not sim:
            raise AppException(ErrorCode.NOT_FOUND, "시뮬레이션을 찾을 수 없습니다", 404)
        await assert_project_member(self.db, sim.project_id, uuid.UUID(user_id))
        res = await self.db.execute(select(Report).where(Report.simulation_id == simulation_id))
        report = res.scalar_one_or_none()
        if not report:
            raise AppException(ErrorCode.NOT_FOUND, "리포트를 찾을 수 없습니다", 404)
        return self._out(report)

    async def list_history(self, user_id: str, limit: int = 20) -> list[ReportOut]:
        project_ids = await list_member_project_ids(self.db, uuid.UUID(user_id))
        if not project_ids:
            return []
        res = await self.db.execute(
            select(Report)
            .join(Simulation, Simulation.id == Report.simulation_id)
            .where(Simulation.project_id.in_(project_ids))
            .order_by(Report.created_at.desc())
            .limit(limit)
        )
        return [self._out(r) for r in res.scalars().all()]

    async def dashboard(self, user_id: str) -> DashboardOut:
        uid = uuid.UUID(user_id)
        project_ids = await list_member_project_ids(self.db, uid)
        if not project_ids:
            return DashboardOut(
                project_count=0,
                simulation_count=0,
                completed_simulations=0,
                recent_reports=[],
            )
        sim_count = await self.db.scalar(
            select(func.count())
            .select_from(Simulation)
            .where(Simulation.project_id.in_(project_ids))
        )
        completed = await self.db.scalar(
            select(func.count())
            .select_from(Simulation)
            .where(
                Simulation.project_id.in_(project_ids),
                Simulation.status == SimulationStatus.completed,
            )
        )
        recent = await self.list_history(user_id, limit=5)
        return DashboardOut(
            project_count=len(project_ids),
            simulation_count=sim_count or 0,
            completed_simulations=completed or 0,
            recent_reports=recent,
        )
