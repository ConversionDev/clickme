"""Alembic env (async). 런타임 URL(asyncpg)을 그대로 사용. 모든 모델은 app.db.models에서 import."""

import asyncio
from logging.config import fileConfig

from alembic import context
from app.db.models import Base  # noqa: F401  (모든 테이블 등록)
from app.db.session import asyncpg_connect_args
from app.shared.config import settings
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
        connect_args=asyncpg_connect_args(settings.database_url),
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url, target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
