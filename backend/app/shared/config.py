"""전역 설정 (pydantic-settings). 환경변수에서 읽고, 미설정 시 안전한 기본값으로 부팅."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    log_level: str = "info"

    # DB (asyncpg). 엔진 생성은 lazy → 미설정이어도 부팅 자체엔 영향 없음.
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/clickme"

    # JWT / OAuth2
    jwt_secret: str = "change-me-please"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    # CORS (프론트 origin)
    cors_origins: list[str] = ["http://localhost:3000"]

    # Storage — local(개발) | s3(프로덕션). API는 동일, 어댑터만 스왑.
    storage_backend: str = "local"
    local_storage_dir: str = str(_BACKEND_ROOT / "uploads")
    storage_public_base_url: str = "http://127.0.0.1:8000/uploads"
    s3_bucket: str = ""
    s3_public_base_url: str = ""
    aws_region: str = "ap-northeast-2"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
