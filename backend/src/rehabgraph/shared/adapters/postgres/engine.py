"""Create the async engine from DATABASE_URL, for local Docker PostgreSQL or Neon.

Neon gives URLs like `postgresql://user:pass@ep-x.region.aws.neon.tech/db?sslmode=require&
channel_binding=require`. asyncpg does not understand `sslmode` / `channel_binding`, so the URL is
normalized first. Hosts with `-pooler` go through PgBouncer, which needs asyncpg's statement cache
turned off.
"""

import os
import uuid
from typing import Any

from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

_SYNC_DRIVERS = {"postgres", "postgresql", "postgresql+psycopg", "postgresql+psycopg2"}
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
# Set by docker-compose: inside the api container "localhost" means the container itself, so a
# local URL from backend/.env is pointed at the postgres container instead. Neon URLs are kept.
LOCALHOST_ALIAS_ENV = "DATABASE_LOCALHOST_ALIAS"


def normalize_database_url(raw_url: str, localhost_alias: str | None = None) -> URL:
    """Turn any PostgreSQL URL into a `postgresql+asyncpg` URL that asyncpg accepts."""
    url = make_url(raw_url)
    alias = localhost_alias if localhost_alias is not None else os.environ.get(LOCALHOST_ALIAS_ENV)
    if alias and url.host in _LOCAL_HOSTS:
        url = url.set(host=alias)
    if url.drivername in _SYNC_DRIVERS:
        url = url.set(drivername="postgresql+asyncpg")
    query = dict(url.query)
    sslmode = query.pop("sslmode", None)
    query.pop("channel_binding", None)  # asyncpg negotiates SCRAM itself
    if sslmode and "ssl" not in query:
        query["ssl"] = sslmode
    return url.set(query=query)


def uses_pgbouncer(url: URL) -> bool:
    return "-pooler" in (url.host or "")


def connect_args_for(url: URL) -> dict[str, Any]:
    if not uses_pgbouncer(url):
        return {}
    # SQLAlchemy recipe for PgBouncer in transaction mode (Neon pooled connections).
    return {
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
    }


def create_engine(raw_url: str, **kwargs: Any) -> AsyncEngine:
    url = normalize_database_url(raw_url)
    # pool_pre_ping: Neon suspends idle computes, so stale connections are checked first.
    return create_async_engine(
        url, connect_args=connect_args_for(url), pool_pre_ping=True, **kwargs
    )
