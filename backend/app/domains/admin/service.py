"""admin 유스케이스."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.admin.repository import AdminRepository
from app.domains.admin.schemas import (
    AdminChatSessionOut,
    AdminUsageOut,
    AdminUserOut,
    CreateAdminUserRequest,
    PatchAdminUserRequest,
)
from app.models.user import User
from app.shared.exceptions import AppException
from app.shared.schemas import ErrorCode
from app.shared.security import hash_password


class AdminService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AdminRepository(db)

    @staticmethod
    def _user_out(u: User) -> AdminUserOut:
        return AdminUserOut(
            id=u.id,
            email=u.email,
            name=u.name,
            role=u.role,
            organization_id=u.organization_id,
            is_active=u.is_active,
            last_login_at=u.last_login_at,
            created_at=u.created_at,
        )

    async def list_users(self) -> list[AdminUserOut]:
        return [self._user_out(u) for u in await self.repo.list_users()]

    async def create_user(self, body: CreateAdminUserRequest) -> AdminUserOut:
        if await self.repo.email_exists(body.email):
            raise AppException(ErrorCode.CONFLICT, "이미 사용 중인 이메일입니다", 409)
        user = User(
            organization_id=body.organization_id,
            email=body.email,
            password_hash=hash_password(body.password),
            name=body.name,
            role=body.role,
        )
        self.repo.add_user(user)
        await self.db.commit()
        await self.db.refresh(user)
        return self._user_out(user)

    async def patch_user(self, user_id: uuid.UUID, body: PatchAdminUserRequest) -> AdminUserOut:
        user = await self.repo.get_user(user_id)
        if not user:
            raise AppException(ErrorCode.NOT_FOUND, "사용자를 찾을 수 없습니다", 404)
        if body.name is not None:
            user.name = body.name
        if body.role is not None:
            user.role = body.role
        if body.is_active is not None:
            user.is_active = body.is_active
        await self.db.commit()
        await self.db.refresh(user)
        return self._user_out(user)

    async def list_chats(self) -> list[AdminChatSessionOut]:
        rows = await self.repo.list_chat_sessions()
        return [
            AdminChatSessionOut(
                id=s.id,
                user_id=s.user_id,
                user_email=email,
                project_id=s.project_id,
                title=s.title,
                message_count=cnt,
                updated_at=s.updated_at,
            )
            for s, email, cnt in rows
        ]

    async def usage(self) -> AdminUsageOut:
        stats = await self.repo.usage_stats()
        return AdminUsageOut(**stats)
