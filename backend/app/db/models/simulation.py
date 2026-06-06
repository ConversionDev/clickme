"""시뮬레이션 + 페르소나 응답(신호) + Debate 결과(P2)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.enums import CampaignObjective, SimulationStatus, SimulationType
from app.db.models.base import Base, CreatedAtMixin, UUIDMixin


class Simulation(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "simulations"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ad_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    simulation_type: Mapped[SimulationType] = mapped_column(
        SAEnum(SimulationType, name="simulation_type"),
        nullable=False,
        default=SimulationType.ad_reaction,
    )
    objective: Mapped[CampaignObjective] = mapped_column(
        SAEnum(CampaignObjective, name="campaign_objective"),
        nullable=False,
        default=CampaignObjective.conversion,
    )
    status: Mapped[SimulationStatus] = mapped_column(
        SAEnum(SimulationStatus, name="simulation_status"),
        nullable=False,
        default=SimulationStatus.pending,
        index=True,
    )
    persona_count: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    persona_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    requested_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    received_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sample_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    results_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    llm_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class PersonaResponse(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "persona_responses"

    simulation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    persona_id: Mapped[str] = mapped_column(String(50), nullable=False)
    producer_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    segment: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    persona_attributes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # 신호 데이터 (v1.2 계약). emotion 추가 여부는 열린 질문(팀 논의).
    signals: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_outlier: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    outlier_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)


class DebateResult(Base, UUIDMixin, CreatedAtMixin):
    """편향 제거 찬반 논쟁 결과 (P2)."""

    __tablename__ = "debate_results"

    simulation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    positive_persona_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    negative_persona_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    positive_arguments: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    counter_arguments: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    synthesis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    adjusted_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
