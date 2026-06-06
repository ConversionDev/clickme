"""헬스체크 — nginx→backend 관통 확인용."""

from fastapi import APIRouter

from app.shared.envelope import ApiResponse, ok

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=ApiResponse[dict])
async def health() -> ApiResponse[dict]:
    return ok({"status": "ok"})
