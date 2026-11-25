"""First migration on a real PostgreSQL (testcontainers): tables, indexes, R-08 triggers."""

import os
import uuid
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine
from testcontainers.postgres import PostgresContainer

BACKEND_DIR = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 11, 25, tzinfo=UTC)


@pytest.fixture(scope="module")
def database_url() -> Iterator[str]:
    with PostgresContainer("pgvector/pgvector:pg16", driver="asyncpg") as pg:
        url = pg.get_connection_url()
        previous = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = url
        try:
            command.upgrade(Config(str(BACKEND_DIR / "alembic.ini")), "head")
            yield url
        finally:
            if previous is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = previous


@pytest.fixture
async def conn(database_url: str) -> AsyncIterator[AsyncConnection]:
    """Each test runs in a transaction that is rolled back."""
    engine = create_async_engine(database_url)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        yield connection
        await transaction.rollback()
    await engine.dispose()


async def insert(conn: AsyncConnection, table: str, **values: object) -> uuid.UUID:
    values.setdefault("id", uuid.uuid4())
    columns = ", ".join(values)
    params = ", ".join(f":{k}" for k in values)
    sql = f"INSERT INTO {table} ({columns}) VALUES ({params})"  # noqa: S608 - names are test constants
    await conn.execute(text(sql), values)
    return values["id"]  # type: ignore[return-value]


async def make_episode(conn: AsyncConnection) -> tuple[uuid.UUID, uuid.UUID]:
    """Fake account + patient + open episode. Returns (account_id, episode_id)."""
    account = await insert(
        conn,
        "accounts",
        email=f"{uuid.uuid4()}@example.test",
        password_hash="x",
        full_name="Fake Staff",
        status="ACTIVE",
        created_at=NOW,
        updated_at=NOW,
    )
    patient = await insert(
        conn,
        "patients",
        full_name="Fake Patient",
        date_of_birth=NOW.date(),
        gender="OTHER",
        created_by=account,
        created_at=NOW,
    )
    episode = await insert(
        conn,
        "treatment_episodes",
        patient_id=patient,
        condition="STROKE",
        status="IN_TREATMENT",
        admitted_at=NOW,
        created_by=account,
        created_at=NOW,
    )
    return account, episode


async def assign(conn: AsyncConnection, account: uuid.UUID, episode: uuid.UUID) -> uuid.UUID:
    return await insert(
        conn,
        "assignments",
        episode_id=episode,
        staff_account_id=account,
        assignment_role="MAIN_DOCTOR",
        status="ACTIVE",
        assigned_by=account,
        created_at=NOW,
    )


async def test_all_tables_and_detail_levels_exist(conn: AsyncConnection) -> None:
    count = await conn.scalar(
        text(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name <> 'alembic_version'"
        )
    )
    assert count == 33
    levels = (await conn.execute(text("SELECT code FROM detail_levels ORDER BY code"))).scalars()
    assert list(levels) == ["BASIC", "DEEP"]


async def test_second_open_episode_for_a_patient_is_blocked(conn: AsyncConnection) -> None:
    account, episode = await make_episode(conn)
    patient = await conn.scalar(
        text("SELECT patient_id FROM treatment_episodes WHERE id = :id"), {"id": episode}
    )
    with pytest.raises(IntegrityError):
        await insert(
            conn,
            "treatment_episodes",
            patient_id=patient,
            condition="STROKE",
            status="IN_TREATMENT",
            admitted_at=NOW,
            created_by=account,
            created_at=NOW,
        )


async def test_second_active_main_doctor_is_blocked(conn: AsyncConnection) -> None:
    account, episode = await make_episode(conn)
    await assign(conn, account, episode)
    with pytest.raises(IntegrityError):
        await assign(conn, account, episode)


async def test_ending_an_assignment_by_updating_status_is_allowed(conn: AsyncConnection) -> None:
    account, episode = await make_episode(conn)
    assignment = await assign(conn, account, episode)
    await conn.execute(
        text("UPDATE assignments SET status = 'ENDED' WHERE id = :id"), {"id": assignment}
    )
    await assign(conn, account, episode)  # a new main doctor is allowed after the old one ended


async def test_updating_another_assignment_column_is_blocked(conn: AsyncConnection) -> None:
    account, episode = await make_episode(conn)
    assignment = await assign(conn, account, episode)
    with pytest.raises(DBAPIError, match="Only"):
        await conn.execute(
            text("UPDATE assignments SET assignment_role = 'TECHNICIAN' WHERE id = :id"),
            {"id": assignment},
        )


async def test_deleting_an_assignment_is_blocked(conn: AsyncConnection) -> None:
    account, episode = await make_episode(conn)
    assignment = await assign(conn, account, episode)
    with pytest.raises(DBAPIError, match="DELETE is not allowed"):
        await conn.execute(text("DELETE FROM assignments WHERE id = :id"), {"id": assignment})


async def test_audit_log_is_append_only(conn: AsyncConnection) -> None:
    entry = await insert(
        conn, "audit_log", action="read", resource_type="patient", result="GRANTED", created_at=NOW
    )
    with pytest.raises(DBAPIError, match="Only"):
        await conn.execute(
            text("UPDATE audit_log SET result = 'DENIED' WHERE id = :id"), {"id": entry}
        )
