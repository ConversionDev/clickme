"""로컬 Storage 어댑터 테스트."""

import pytest
from app.infra.local_storage import LocalStorageBackend
from app.shared.config import settings


@pytest.mark.asyncio
async def test_local_storage_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "local_storage_dir", str(tmp_path))
    monkeypatch.setattr(settings, "storage_public_base_url", "http://test/uploads")
    backend = LocalStorageBackend()
    obj = await backend.upload("ads/p1/test.jpg", b"fake-image", "image/jpeg")
    assert obj.path == "ads/p1/test.jpg"
    assert obj.url == "http://test/uploads/ads/p1/test.jpg"
    assert (tmp_path / "ads" / "p1" / "test.jpg").read_bytes() == b"fake-image"
