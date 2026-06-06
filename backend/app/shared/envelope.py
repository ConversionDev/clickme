"""공통 응답 봉투 + 에러코드 (contracts SSOT의 뼈대). 모든 API가 이 형태로 응답."""

from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INTERNAL = "INTERNAL"


class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    message: str | None = None
    error: ErrorDetail | None = None


def ok(data: T | None = None, message: str | None = None) -> ApiResponse[T]:
    return ApiResponse(success=True, data=data, message=message)
