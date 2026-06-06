"""Async SQLAlchemy 엔진/세션. 의존성 get_db로 도메인에 주입."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.shared.config import settings


def asyncpg_connect_args(url: str) -> dict:
    """asyncpg(Neon 등) 연결 옵션.
    - statement_cache_size=0: Neon pooler(PgBouncer) 호환 — prepared statement 충돌 방지
    - ssl=require: Neon 등 SSL 필수 호스트 (로컬 PG는 SSL 없이)"""
    if not url.startswith("postgresql+asyncpg"):
        return {}
    args: dict = {"statement_cache_size": 0}
    if "neon.tech" in url or "amazonaws.com" in url:
        args["ssl"] = "require"
    return args


engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=asyncpg_connect_args(settings.database_url),
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
