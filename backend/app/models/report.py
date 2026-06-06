"""리포트 + Calibration 데이터(P2, 예측↔실측 보정)."""
import uuid

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, UUIDMixin

_DISCLAIMER = "본 결과는 AI 시뮬레이션 기반 예측입니다. 실제 광고 성과와 ±20~30% 오차가 있을 수 있습니다."


class Report(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "reports"

    simulation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    report_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False, default=_DISCLAIMER)


class CalibrationData(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "calibration_data"

    simulation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("simulations.id", ondelete="SET NULL"), nullable=True
    )
    predicted_ctr_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_ctr_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(50), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ad_format: Mapped[str | None] = mapped_column(String(30), nullable=True)
    submitted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
