"""인증 의존성. get_current_user(토큰 검증) / require_role(RBAC, 실 인가)."""
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import BaseModel

from app.shared.exceptions import AppException
from app.shared.envelope import ErrorCode
from app.shared.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


class CurrentUser(BaseModel):
    id: str
    role: str
    org_id: str


async def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)]) -> CurrentUser:
    if not token:
        raise AppException(ErrorCode.UNAUTHORIZED, "인증 토큰이 없습니다", 401)
    try:
        payload = decode_token(token)
    except JWTError:
        raise AppException(ErrorCode.TOKEN_EXPIRED, "토큰 검증에 실패했습니다", 401)
    if payload.get("type") != "access":
        raise AppException(ErrorCode.UNAUTHORIZED, "access 토큰이 아닙니다", 401)
    return CurrentUser(id=payload["sub"], role=payload["role"], org_id=payload["org_id"])


def require_role(*roles: str):
    async def checker(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if user.role not in roles:
            raise AppException(ErrorCode.FORBIDDEN, "권한이 없습니다", 403)
        return user

    return checker
