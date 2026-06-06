"""users/org/settings 라우터."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.users.dto import (
    OrganizationOut,
    UpdateUserSettingsRequest,
    UserProfileOut,
    UserSettingsOut,
)
from app.domains.users.service import UserService
from app.db.session import get_db
from app.shared.deps import CurrentUser, get_current_user
from app.shared.envelope import ApiResponse, ok

router = APIRouter(prefix="/api", tags=["users"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.get("/users/me", response_model=ApiResponse[UserProfileOut])
async def get_me(user: UserDep, db: DbDep) -> ApiResponse[UserProfileOut]:
    return ok(await UserService(db).get_profile(user.id))


@router.get("/users/me/settings", response_model=ApiResponse[UserSettingsOut])
async def get_settings(user: UserDep, db: DbDep) -> ApiResponse[UserSettingsOut]:
    return ok(await UserService(db).get_settings(user.id))


@router.patch("/users/me/settings", response_model=ApiResponse[UserSettingsOut])
async def update_settings(
    body: UpdateUserSettingsRequest, user: UserDep, db: DbDep
) -> ApiResponse[UserSettingsOut]:
    return ok(await UserService(db).update_settings(user.id, body))


@router.get("/organizations/{org_id}", response_model=ApiResponse[OrganizationOut])
async def get_organization(
    org_id: UUID, user: UserDep, db: DbDep
) -> ApiResponse[OrganizationOut]:
    return ok(await UserService(db).get_organization(org_id, user.org_id))
