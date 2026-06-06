"""광고 시안 (이미지/텍스트=베이스라인, 영상/URL=P2)."""

import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.enums import AdInputType, AdStatus
from app.db.models.base import Base, TimestampMixin, UUIDMixin


class Ad(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ads"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    input_type: Mapped[AdInputType] = mapped_column(
        SAEnum(AdInputType, name="ad_input_type"), nullable=False
    )
    # 이미지/영상: S3 경로
    storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 텍스트 광고: 직접 입력
    text_content: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # URL 광고
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 분석 결과
    analysis_status: Mapped[AdStatus] = mapped_column(
        SAEnum(AdStatus, name="ad_status"), nullable=False, default=AdStatus.pending
    )
    analysis_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    analysis_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    analysis_error: Mapped[str | None] = mapped_column(Text, nullable=True)
