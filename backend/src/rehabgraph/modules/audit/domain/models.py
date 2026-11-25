"""Audit log entries (R-11, R-12, R-13). Append-only: never updated, never deleted."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from rehabgraph.shared.auth import Role
from rehabgraph.shared.domain import EntityId


class AuditResult(StrEnum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"  # denied actions are logged too (R-11)


@dataclass(frozen=True)
class AuditEntry:
    """# ERD: Nhật ký truy cập. Holds IDs only, never patient names or question text (AGENTS 13)."""

    id: EntityId
    action: str
    resource_type: str
    result: AuditResult
    created_at: datetime
    actor_account_id: EntityId | None = None  # empty for a guest
    active_role: Role | None = None  # workspace used (R-14 logs every switch)
    resource_id: EntityId | None = None
    patient_id: EntityId | None = None  # lets the patient read the log of their own data (R-13)
    ip_address: str | None = None
