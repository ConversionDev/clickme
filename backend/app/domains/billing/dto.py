"""billing UI용 스키마 (결제 연동 없음)."""
from pydantic import BaseModel

from app.db.enums import PlanType


class BillingPlanOut(BaseModel):
    organization_id: str
    organization_name: str
    plan_type: PlanType
    display_name: str
    price_krw: int
    features: list[str]
    is_current: bool = True
