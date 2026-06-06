"""S3 저장 — 프로덕션(EC2 IAM 롤). AWS 미설정 시 명확한 오류."""

from app.infra.storage import StoredObject
from app.shared.config import settings


class S3StorageBackend:
    """boto3 put_object. STORAGE_BACKEND=s3 + 버킷 설정 후 사용."""

    async def upload(self, key: str, data: bytes, content_type: str) -> StoredObject:
        if not settings.s3_bucket:
            raise RuntimeError(
                "S3_BUCKET이 설정되지 않았습니다. 로컬 개발은 STORAGE_BACKEND=local 을 사용하세요."
            )
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("S3 백엔드에 boto3가 필요합니다: uv add boto3") from exc

        client = boto3.client("s3", region_name=settings.aws_region or None)
        client.put_object(
            Bucket=settings.s3_bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        base = settings.s3_public_base_url.rstrip("/")
        url = f"{base}/{key}"
        return StoredObject(path=key, url=url, content_type=content_type)
