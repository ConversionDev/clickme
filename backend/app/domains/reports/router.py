"""reports 라우터."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.reports.dto import DashboardOut, ReportOut
from app.domains.reports.service import ReportService
from app.db.session import get_db
from app.shared.deps import CurrentUser, get_current_user
from app.shared.envelope import ApiResponse, ok

router = APIRouter(prefix="/api", tags=["reports"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.get("/simulations/{simulation_id}/report", response_model=ApiResponse[ReportOut])
async def get_simulation_report(
    simulation_id: UUID, user: UserDep, db: DbDep
) -> ApiResponse[ReportOut]:
    return ok(await ReportService(db).get_by_simulation(simulation_id, user.id))


@router.get("/reports", response_model=ApiResponse[list[ReportOut]])
async def list_reports(user: UserDep, db: DbDep) -> ApiResponse[list[ReportOut]]:
    return ok(await ReportService(db).list_history(user.id))


@router.get("/dashboard", response_model=ApiResponse[DashboardOut])
async def dashboard(user: UserDep, db: DbDep) -> ApiResponse[DashboardOut]:
    return ok(await ReportService(db).dashboard(user.id))
