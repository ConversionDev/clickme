"""users/org/settings 유스케이스."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.users.dto import (
    OrganizationOut,
    UpdateUserSettingsRequest,
    UserProfileOut,
    UserSettingsOut,
)
from app.db.models.organization import Organization
from app.db.models.user import User
from app.db.models.user_settings import UserSettings
from app.shared.exceptions import AppException
from app.shared.envelope import ErrorCode


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_organization(self, org_id: uuid.UUID, user_org_id: str) -> OrganizationOut:
        if str(org_id) != user_org_id:
            raise AppException(ErrorCode.FORBIDDEN, "조직 접근 권한이 없습니다", 403)
        org = await self.db.get(Organization, org_id)
        if not org:
            raise AppException(ErrorCode.NOT_FOUND, "조직을 찾을 수 없습니다", 404)
        return OrganizationOut(
            id=org.id,
            name=org.name,
            plan_type=org.plan_type,
            created_at=org.created_at,
        )

    async def get_profile(self, user_id: str) -> UserProfileOut:
        user = await self.db.get(User, uuid.UUID(user_id))
        if not user:
            raise AppException(ErrorCode.NOT_FOUND, "사용자를 찾을 수 없습니다", 404)
        return UserProfileOut(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            organization_id=user.organization_id,
        )

    async def get_settings(self, user_id: str) -> UserSettingsOut:
        res = await self.db.execute(
            select(UserSettings).where(UserSettings.user_id == uuid.UUID(user_id))
        )
        settings = res.scalar_one_or_none()
        if not settings:
            return UserSettingsOut(theme="light", notifications={})
        return UserSettingsOut(theme=settings.theme, notifications=settings.notifications)

    async def update_settings(
        self, user_id: str, body: UpdateUserSettingsRequest
    ) -> UserSettingsOut:
        uid = uuid.UUID(user_id)
        res = await self.db.execute(select(UserSettings).where(UserSettings.user_id == uid))
        settings = res.scalar_one_or_none()
        if not settings:
            settings = UserSettings(user_id=uid)
            self.db.add(settings)
        if body.theme is not None:
            settings.theme = body.theme
        if body.notifications is not None:
            settings.notifications = body.notifications
        await self.db.commit()
        await self.db.refresh(settings)
        return UserSettingsOut(theme=settings.theme, notifications=settings.notifications)
