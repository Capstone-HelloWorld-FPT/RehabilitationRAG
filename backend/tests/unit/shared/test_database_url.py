from rehabgraph.shared.adapters.postgres.engine import (
    connect_args_for,
    normalize_database_url,
    uses_pgbouncer,
)

NEON = (
    "postgresql://user:secret@ep-fake-123.ap-southeast-1.aws.neon.tech/neondb"
    "?sslmode=require&channel_binding=require"
)


def test_neon_url_becomes_asyncpg_with_ssl() -> None:
    url = normalize_database_url(NEON)
    assert url.drivername == "postgresql+asyncpg"
    assert dict(url.query) == {"ssl": "require"}
    assert url.password == "secret"


def test_local_docker_url_is_unchanged() -> None:
    raw = "postgresql+asyncpg://rehabgraph:rehabgraph@postgres:5432/rehabgraph"
    assert normalize_database_url(raw).render_as_string(hide_password=False) == raw


def test_direct_neon_host_keeps_statement_cache() -> None:
    url = normalize_database_url(NEON)
    assert not uses_pgbouncer(url)
    assert connect_args_for(url) == {}


def test_pooled_neon_host_turns_statement_cache_off() -> None:
    url = normalize_database_url(NEON.replace("ep-fake-123.", "ep-fake-123-pooler."))
    assert uses_pgbouncer(url)
    assert connect_args_for(url)["statement_cache_size"] == 0


def test_localhost_points_to_postgres_container_inside_docker() -> None:
    raw = "postgresql+asyncpg://rehabgraph:rehabgraph@localhost:5432/rehabgraph"
    assert normalize_database_url(raw, localhost_alias="postgres").host == "postgres"


def test_neon_host_is_kept_inside_docker() -> None:
    url = normalize_database_url(NEON, localhost_alias="postgres")
    assert url.host == "ep-fake-123.ap-southeast-1.aws.neon.tech"
