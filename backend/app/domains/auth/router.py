"""auth 라우터 (얇게) — 검증·DI만, 로직은 service."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
)
from app.domains.auth.service import AuthService
from app.shared.db import get_db
from app.shared.deps import CurrentUser, get_current_user
from app.shared.schemas import ApiResponse, ok

router = APIRouter(prefix="/api/auth", tags=["auth"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(body: LoginRequest, db: DbDep) -> ApiResponse[TokenResponse]:
    return ok(await AuthService(db).login(body.email, body.password))


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh(body: RefreshRequest, db: DbDep) -> ApiResponse[TokenResponse]:
    return ok(await AuthService(db).refresh(body.refresh_token))


@router.post("/logout", response_model=ApiResponse[None])
async def logout(body: LogoutRequest, db: DbDep) -> ApiResponse[None]:
    await AuthService(db).logout(body.refresh_token)
    return ok(message="로그아웃 완료")


@router.post("/change-password", response_model=ApiResponse[None])
async def change_password(
    body: ChangePasswordRequest, user: UserDep, db: DbDep
) -> ApiResponse[None]:
    await AuthService(db).change_password(user.id, body.current_password, body.new_password)
    return ok(message="비밀번호 변경 완료")


@router.get("/me", response_model=ApiResponse[CurrentUser])
async def me(user: UserDep) -> ApiResponse[CurrentUser]:
    return ok(user)
