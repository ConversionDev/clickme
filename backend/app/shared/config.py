"""전역 설정 (pydantic-settings). 환경변수에서 읽고, 미설정 시 안전한 기본값으로 부팅."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
