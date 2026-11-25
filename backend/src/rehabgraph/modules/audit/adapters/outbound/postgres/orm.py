"""SQLAlchemy tables of the audit module.

`audit_log` is append-only: the app DB user gets INSERT and SELECT only (BACKEND-ARCHITECTURE 6.3).
"""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from rehabgraph.modules.audit.domain.models import AuditResult
from rehabgraph.shared.adapters.postgres import Base, Timestamp, UuidPk, enum_column, no_overwrite
from rehabgraph.shared.auth import Role


class AuditLogRow(Base):
    """# ERD: Nhật ký truy cập"""

    __tablename__ = "audit_log"
    __table_args__ = no_overwrite()

    id: Mapped[UuidPk]
    actor_account_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("accounts.id"), index=True
    )
    active_role: Mapped[Role | None] = mapped_column(enum_column(Role, "role"))
    action: Mapped[str] = mapped_column(String(64))
    resource_type: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[uuid.UUID | None]
    patient_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("patients.id"), index=True)
    result: Mapped[AuditResult] = mapped_column(enum_column(AuditResult, "audit_result"))
    ip_address: Mapped[str | None] = mapped_column(INET)
    created_at: Mapped[Timestamp]
