"""광고 업로드 검증 — 베이스라인 10MB · image/jpeg|png|webp."""
from app.shared.exceptions import AppException
from app.shared.schemas import ErrorCode

MAX_AD_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def validate_image(content_type: str | None, size: int) -> str:
    if not content_type or content_type not in ALLOWED_IMAGE_TYPES:
        raise AppException(
            ErrorCode.VALIDATION_ERROR,
            "이미지는 JPEG, PNG, WebP만 허용됩니다",
            400,
        )
    if size > MAX_AD_IMAGE_BYTES:
        raise AppException(
            ErrorCode.VALIDATION_ERROR,
            "이미지 크기는 10MB 이하여야 합니다",
            400,
        )
    return ALLOWED_IMAGE_TYPES[content_type]
