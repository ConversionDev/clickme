"""ads 라우터 — multipart(베이스라인) + JSON 텍스트(호환)."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.ads.dto import AdOut, CreateTextAdRequest
from app.domains.ads.service import AdService
from app.domains.ads.validation import MAX_AD_IMAGE_BYTES
from app.db.session import get_db
from app.shared.deps import CurrentUser, get_current_user
from app.shared.exceptions import AppException
from app.shared.envelope import ApiResponse, ErrorCode, ok

router = APIRouter(prefix="/api", tags=["ads"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[CurrentUser, Depends(get_current_user)]


async def _read_upload_limited(file: UploadFile, limit: int = MAX_AD_IMAGE_BYTES) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        block = await file.read(1024 * 64)
        if not block:
            break
        total += len(block)
        if total > limit:
            raise AppException(
                ErrorCode.VALIDATION_ERROR,
                "이미지 크기는 10MB 이하여야 합니다",
                400,
            )
        chunks.append(block)
    return b"".join(chunks)


@router.get("/projects/{project_id}/ads", response_model=ApiResponse[list[AdOut]])
async def list_ads(
    project_id: UUID, user: UserDep, db: DbDep
) -> ApiResponse[list[AdOut]]:
    return ok(await AdService(db).list_for_project(project_id, user.id))


@router.post("/ads", response_model=ApiResponse[AdOut])
async def create_ad_multipart(
    user: UserDep,
    db: DbDep,
    project_id: UUID = Form(...),
    name: str = Form(...),
    input_type: str = Form(..., description="text | image"),
    headline: str | None = Form(None),
    body: str | None = Form(None),
    cta: str | None = Form(None),
    file: UploadFile | None = File(None),
) -> ApiResponse[AdOut]:
    """베이스라인 업로드 — text: 폼 필드 / image: multipart file (10MB)."""
    file_bytes = None
    if file and file.filename:
        file_bytes = await _read_upload_limited(file)
    return ok(
        await AdService(db).create_multipart(
            user.id,
            project_id,
            name,
            input_type,
            headline=headline,
            body=body,
            cta=cta,
            file_bytes=file_bytes,
            file_content_type=file.content_type,
            file_filename=file.filename,
        )
    )


@router.post("/ads/text", response_model=ApiResponse[AdOut])
async def create_ad_text_json(
    body: CreateTextAdRequest, user: UserDep, db: DbDep
) -> ApiResponse[AdOut]:
    """JSON 텍스트 광고 (개발·스크립트용 호환)."""
    return ok(await AdService(db).create_text(user.id, body))


@router.get("/ads/{ad_id}", response_model=ApiResponse[AdOut])
async def get_ad(ad_id: UUID, user: UserDep, db: DbDep) -> ApiResponse[AdOut]:
    return ok(await AdService(db).get_ad(ad_id, user.id))
