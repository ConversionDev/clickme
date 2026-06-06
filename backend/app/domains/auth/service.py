"""auth 비즈니스 로직 — 로그인/리프레시(회전)/로그아웃/비밀번호 변경."""

import hashlib
from datetime import UTC, datetime, timedelta

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.domains.auth.dto import TokenResponse, UserOut
from app.domains.auth.repository import AuthRepository
from app.shared import security
from app.shared.config import settings
from app.shared.envelope import ErrorCode
from app.shared.exceptions import AppException


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AuthRepository(db)

    @staticmethod
    def _to_user_out(user: User) -> UserOut:
        return UserOut(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role,
            organization_id=str(user.organization_id),
        )

    async def _issue(self, user: User) -> TokenResponse:
        access = security.create_access_token(user.id, user.role.value, user.organization_id)
        refresh = security.create_refresh_token(user.id, user.role.value, user.organization_id)
        self.repo.add_refresh_token(
            user.id,
            _hash_token(refresh),
            datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )
        return TokenResponse(
            access_token=access, refresh_token=refresh, user=self._to_user_out(user)
        )

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.repo.get_user_by_email(email)
        if not user or not security.verify_password(password, user.password_hash):
            raise AppException(
                ErrorCode.INVALID_CREDENTIALS, "이메일 또는 비밀번호가 올바르지 않습니다", 401
            )
        if not user.is_active:
            raise AppException(ErrorCode.FORBIDDEN, "비활성 계정입니다", 403)
        user.last_login_at = datetime.now(UTC)
        tokens = await self._issue(user)
        await self.db.commit()
        return tokens

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = security.decode_token(refresh_token)
        except JWTError as err:
            raise AppException(ErrorCode.TOKEN_EXPIRED, "리프레시 토큰 검증 실패", 401) from err
        if payload.get("type") != "refresh":
            raise AppException(ErrorCode.UNAUTHORIZED, "refresh 토큰이 아닙니다", 401)

        stored = await self.repo.get_refresh_token(_hash_token(refresh_token))
        if not stored or stored.revoked:
            raise AppException(ErrorCode.UNAUTHORIZED, "리프레시 토큰이 무효합니다", 401)
        stored.revoked = True  # rotate: 1회용

        user = await self.repo.get_user_by_id(payload["sub"])
        if not user or not user.is_active:
            raise AppException(ErrorCode.UNAUTHORIZED, "사용자를 찾을 수 없습니다", 401)
        tokens = await self._issue(user)
        await self.db.commit()
        return tokens

    async def logout(self, refresh_token: str) -> None:
        stored = await self.repo.get_refresh_token(_hash_token(refresh_token))
        if stored:
            stored.revoked = True
            await self.db.commit()

    async def change_password(self, user_id: str, current: str, new: str) -> None:
        user = await self.repo.get_user_by_id(user_id)
        if not user or not security.verify_password(current, user.password_hash):
            raise AppException(
                ErrorCode.INVALID_CREDENTIALS, "현재 비밀번호가 올바르지 않습니다", 400
            )
        user.password_hash = security.hash_password(new)
        await self.db.commit()
