"""조직 — 결제 단위. 여러 멤버가 하나의 플랜 공유."""
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import PlanType


class Organization(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    plan_type: Mapped[PlanType] = mapped_column(
        SAEnum(PlanType, name="plan_type"), nullable=False, default=PlanType.free
    )
