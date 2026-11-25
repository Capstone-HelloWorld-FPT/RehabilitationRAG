"""Every table builds and every string foreign key resolves, without a database."""

import importlib
import pkgutil
from collections import Counter

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

import rehabgraph.modules
from rehabgraph.shared.adapters.postgres import Base


def load_all_orm_modules() -> list[str]:
    loaded = []
    for info in pkgutil.walk_packages(rehabgraph.modules.__path__, "rehabgraph.modules."):
        if info.name.endswith(".adapters.outbound.postgres.orm"):
            importlib.import_module(info.name)
            loaded.append(info.name)
    return loaded


def test_all_tables_compile_for_postgresql() -> None:
    assert len(load_all_orm_modules()) == 8  # every module except notifications
    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
    for table in Base.metadata.sorted_tables:  # resolves every ForeignKey("table.column") string
        assert str(CreateTable(table).compile(dialect=dialect))


def test_physical_model_tables_exist() -> None:
    load_all_orm_modules()
    assert len(Base.metadata.tables) == 33


def test_constraint_names_are_unique() -> None:
    load_all_orm_modules()
    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
    names: Counter[str] = Counter()
    for table in Base.metadata.sorted_tables:
        CreateTable(table).compile(dialect=dialect)  # resolves naming-convention names
        names.update(str(c.name) for c in table.constraints if c.name)
        names.update(str(i.name) for i in table.indexes)
    assert [name for name, count in names.items() if count > 1] == []


def test_times_are_timestamptz_and_optional_columns_are_nullable() -> None:
    load_all_orm_modules()
    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
    for table in Base.metadata.sorted_tables:
        assert "WITHOUT TIME ZONE" not in str(CreateTable(table).compile(dialect=dialect))
    mapped = [m.class_ for m in Base.registry.mappers]
    for cls in mapped:
        for name, hint in cls.__annotations__.items():
            column = cls.__table__.c.get(name)
            if column is not None and not column.primary_key:
                optional = "None" in str(hint) or "Optional[" in str(hint)
                assert column.nullable == optional, f"{cls.__tablename__}.{name}"


def test_no_overwrite_tables_match_r08_and_r13() -> None:
    """BUSINESS_PROJECT R-08 / R-13 and BACKEND-ARCHITECTURE section 7."""
    load_all_orm_modules()
    policy = {
        name: table.info["updatable_columns"]
        for name, table in Base.metadata.tables.items()
        if table.info.get("no_delete")
    }
    assert policy == {
        "consents": (),
        "status_records": (),
        "caregiver_permission_versions": (),
        "audit_log": (),
        "assignments": ("status",),
        "pathway_versions": ("status", "decided_by", "decided_at", "reject_reason"),
    }
    for name, columns in policy.items():
        assert set(columns) <= set(Base.metadata.tables[name].c.keys())
