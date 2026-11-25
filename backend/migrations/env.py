"""Alembic environment (async, asyncpg). Loads every module's `orm.py` into one MetaData."""

import asyncio
import importlib
import os
import pkgutil

from alembic import context
from sqlalchemy.engine import Connection

import rehabgraph.modules
from rehabgraph.shared.adapters.postgres import Base
from rehabgraph.shared.adapters.postgres.engine import create_engine, normalize_database_url


def load_all_orm_modules() -> None:
    for info in pkgutil.walk_packages(rehabgraph.modules.__path__, "rehabgraph.modules."):
        if info.name.endswith(".adapters.outbound.postgres.orm"):
            importlib.import_module(info.name)


load_all_orm_modules()
target_metadata = Base.metadata


def database_url() -> str:
    """Docker PostgreSQL or Neon. For Neon migrations, use the direct host (no `-pooler`)."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Set DATABASE_URL (see backend/.env.example) before running Alembic")
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=normalize_database_url(database_url()),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_engine(database_url())
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
