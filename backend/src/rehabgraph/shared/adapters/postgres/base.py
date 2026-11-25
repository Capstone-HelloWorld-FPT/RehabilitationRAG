"""SQLAlchemy base shared by every module's `orm.py` (BACKEND-ARCHITECTURE section 7).

All tables use one MetaData, so a module can point to another module's table with a string
foreign key (`ForeignKey("accounts.id")`) without importing that module.
"""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Annotated

from sqlalchemy import DateTime, Enum, MetaData, Uuid
from sqlalchemy.orm import DeclarativeBase, mapped_column

# Stable constraint names, so Alembic migrations do not depend on database defaults.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Primary key: UUID v7, created by the application (`shared.domain.new_id`), not by the database.
UuidPk = Annotated[uuid.UUID, mapped_column(Uuid, primary_key=True)]
# Times are stored in UTC with time zone.
Timestamp = Annotated[datetime, mapped_column(DateTime(timezone=True))]


def enum_column[E: StrEnum](enum_cls: type[E], name: str) -> Enum:
    """Store a StrEnum as VARCHAR + CHECK constraint, not a native PostgreSQL enum.

    `name` becomes the CHECK constraint name (`ck_<table>_<name>`), so it must be unique per table.

    Several tables share the same enum (e.g. `role`); a native type would be created many
    times and is hard to extend. The stored value is the enum value (UPPER_SNAKE_CASE).
    """
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=32,
        values_callable=lambda members: [m.value for m in members],
        validate_strings=True,
    )


def no_overwrite(*updatable_columns: str) -> dict[str, dict[str, object]]:
    """Table options for R-08 / R-13 tables: no DELETE, and UPDATE only on the listed columns.

    With no columns the table is append-only. The database enforces it with the trigger
    `forbid_overwrite` (first migration); keep that migration's NO_OVERWRITE list in sync.
    """
    return {"info": {"no_delete": True, "updatable_columns": tuple(updatable_columns)}}
