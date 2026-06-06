"""reports API 스키마."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReportOut(BaseModel):
    id: UUID
    simulation_id: UUID
    report_data: dict
    pdf_url: str | None
    disclaimer: str
    created_at: datetime


class DashboardOut(BaseModel):
    project_count: int
    simulation_count: int
    completed_simulations: int
    recent_reports: list[ReportOut]
