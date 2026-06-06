"""시뮬레이션 HTTP API 계약."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.contracts.simulation_pipeline import PersonaConfig, Prediction, Recommendation
from app.db.enums import CampaignObjective, SimulationStatus, SimulationType


class CreateSimulationRequest(BaseModel):
    ad_id: UUID
    simulation_type: SimulationType = SimulationType.ad_reaction
    objective: CampaignObjective = CampaignObjective.conversion
    persona_count: int = Field(default=20, ge=1, le=50)
    persona_config: PersonaConfig | None = None


class SimulationCreatedOut(BaseModel):
    id: UUID
    status: SimulationStatus


class SimulationSummaryOut(BaseModel):
    id: UUID
    project_id: UUID
    ad_id: UUID
    status: SimulationStatus
    persona_count: int
    objective: CampaignObjective
    results_summary: dict | None = None
    created_at: datetime


class SimulationDetailOut(SimulationSummaryOut):
    simulation_type: SimulationType
    persona_config: dict | None = None
    requested_count: int | None = None
    received_count: int | None = None
    sample_size: int | None = None
    prediction: Prediction | None = None
    recommendation: Recommendation | None = None
    report_id: UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
