"""비밀번호 해시(bcrypt) + JWT 발급/검증. 클레임 = {sub, role, org_id, type, iat, exp}."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
from jose import jwt

from app.shared.config import settings

# bcrypt는 72바이트까지만 사용 (초과분 무시) → 안전하게 잘라 ValueError 방지
_BCRYPT_MAX = 72


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:_BCRYPT_MAX]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        pw = password.encode("utf-8")[:_BCRYPT_MAX]
        return bcrypt.checkpw(pw, password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _create_token(sub: UUID, role: str, org_id: UUID, expires: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(sub),
        "role": role,
        "org_id": str(org_id),
        "type": token_type,
        "iat": now,
        "exp": now + expires,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(sub: UUID, role: str, org_id: UUID) -> str:
    return _create_token(
        sub, role, org_id, timedelta(minutes=settings.access_token_expire_minutes), "access"
    )


def create_refresh_token(sub: UUID, role: str, org_id: UUID) -> str:
    return _create_token(
        sub, role, org_id, timedelta(days=settings.refresh_token_expire_days), "refresh"
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
