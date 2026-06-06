"""Storage 포트 — local(개발) / s3(프로덕션) 스왑."""

from dataclasses import dataclass
from typing import Protocol

from app.shared.config import settings


@dataclass(frozen=True)
class StoredObject:
    """업로드 결과 — DB에는 path(키) + url(공개 URL) 저장."""

    path: str
    url: str
    content_type: str


class StorageBackend(Protocol):
    async def upload(self, key: str, data: bytes, content_type: str) -> StoredObject: ...


def get_storage() -> StorageBackend:
    if settings.storage_backend == "s3":
        from app.infra.s3_storage import S3StorageBackend

        return S3StorageBackend()
    from app.infra.local_storage import LocalStorageBackend

    return LocalStorageBackend()
