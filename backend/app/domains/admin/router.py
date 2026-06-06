"""admin 라우터 — require_role(admin)."""

from typing import Annotated
from uuid import UUID

from app.db.session import get_db
from app.domains.admin.dto import (
    AdminChatSessionOut,
    AdminUsageOut,
    AdminUserOut,
    CreateAdminUserRequest,
    PatchAdminUserRequest,
)
from app.domains.admin.service import AdminService
from app.shared.deps import CurrentUser, require_role
from app.shared.envelope import ApiResponse, ok
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/admin", tags=["admin"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
AdminDep = Annotated[CurrentUser, Depends(require_role("admin"))]


@router.get("/users", response_model=ApiResponse[list[AdminUserOut]])
async def list_users(_: AdminDep, db: DbDep) -> ApiResponse[list[AdminUserOut]]:
    return ok(await AdminService(db).list_users())


@router.post("/users", response_model=ApiResponse[AdminUserOut])
async def create_user(
    body: CreateAdminUserRequest, _: AdminDep, db: DbDep
) -> ApiResponse[AdminUserOut]:
    return ok(await AdminService(db).create_user(body))


@router.patch("/users/{user_id}", response_model=ApiResponse[AdminUserOut])
async def patch_user(
    user_id: UUID, body: PatchAdminUserRequest, _: AdminDep, db: DbDep
) -> ApiResponse[AdminUserOut]:
    return ok(await AdminService(db).patch_user(user_id, body))


@router.get("/chats", response_model=ApiResponse[list[AdminChatSessionOut]])
async def list_chats(_: AdminDep, db: DbDep) -> ApiResponse[list[AdminChatSessionOut]]:
    return ok(await AdminService(db).list_chats())


@router.get("/usage", response_model=ApiResponse[AdminUsageOut])
async def usage(_: AdminDep, db: DbDep) -> ApiResponse[AdminUsageOut]:
    return ok(await AdminService(db).usage())
