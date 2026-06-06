"""앱 예외 + FastAPI 핸들러 → 항상 응답 봉투({success,error}) 형태로 반환."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.shared.logging import logger
from app.shared.schemas import ApiResponse, ErrorCode, ErrorDetail


class AppException(Exception):
    def __init__(self, code: ErrorCode, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code


def _error_response(status_code: int, code: ErrorCode, message: str) -> JSONResponse:
    body = ApiResponse(success=False, error=ErrorDetail(code=code, message=message))
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def _app_exc(_: Request, exc: AppException) -> JSONResponse:
        return _error_response(exc.status_code, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def _val_exc(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(422, ErrorCode.VALIDATION_ERROR, "요청 검증에 실패했습니다")

    @app.exception_handler(StarletteHTTPException)
    async def _http_exc(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = ErrorCode.NOT_FOUND if exc.status_code == 404 else ErrorCode.INTERNAL
        return _error_response(exc.status_code, code, str(exc.detail))

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        # 서버측에만 스택트레이스 기록(기밀 평문 금지), 클라엔 일반 메시지만
        logger.exception("unhandled exception: %s", type(exc).__name__)
        return _error_response(500, ErrorCode.INTERNAL, "서버 오류가 발생했습니다")
