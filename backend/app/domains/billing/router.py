"""billing 라우터 — 플랜 UI 스텁 (결제 미연동)."""

from typing import Annotated
from uuid import UUID

from app.db.enums import PlanType
from app.db.models.organization import Organization
from app.db.session import get_db
from app.domains.billing.dto import BillingPlanOut
from app.shared.deps import CurrentUser, get_current_user
from app.shared.envelope import ApiResponse, ErrorCode, ok
from app.shared.exceptions import AppException
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/billing", tags=["billing"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[CurrentUser, Depends(get_current_user)]

_PLANS: dict[PlanType, tuple[str, int, list[str]]] = {
    PlanType.free: (
        "Free",
        0,
        ["프로젝트 1개", "시뮬 월 5회", "텍스트 광고"],
    ),
    PlanType.professional: (
        "Professional",
        49000,
        ["프로젝트 10개", "시뮬 무제한", "이미지 광고", "리포트 PDF"],
    ),
    PlanType.enterprise: (
        "Enterprise",
        0,
        ["무제한", "관리자 콘솔", "전담 지원", "맞춤 SLA"],
    ),
}


@router.get("", response_model=ApiResponse[list[BillingPlanOut]])
async def get_billing(user: UserDep, db: DbDep) -> ApiResponse[list[BillingPlanOut]]:
    org = await db.get(Organization, UUID(user.org_id))
    if not org:
        raise AppException(ErrorCode.NOT_FOUND, "조직을 찾을 수 없습니다", 404)
    plans = []
    for plan_type, (display, price, features) in _PLANS.items():
        plans.append(
            BillingPlanOut(
                organization_id=str(org.id),
                organization_name=org.name,
                plan_type=plan_type,
                display_name=display,
                price_krw=price,
                features=features,
                is_current=org.plan_type == plan_type,
            )
        )
    return ok(plans)
