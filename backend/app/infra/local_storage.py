"""로컬 디스크 저장 — AWS 없이 multipart 업로드·VLM URL 검증용."""

import asyncio
from pathlib import Path

from app.infra.storage import StoredObject
from app.shared.config import settings


class LocalStorageBackend:
    def __init__(self) -> None:
        self._root = Path(settings.local_storage_dir)
        self._base_url = settings.storage_public_base_url.rstrip("/")

    async def upload(self, key: str, data: bytes, content_type: str) -> StoredObject:
        dest = self._root / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(dest.write_bytes, data)
        return StoredObject(
            path=key,
            url=f"{self._base_url}/{key.replace(chr(92), '/')}",
            content_type=content_type,
        )
