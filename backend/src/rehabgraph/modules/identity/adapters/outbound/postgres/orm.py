"""SQLAlchemy tables of the identity module."""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from rehabgraph.modules.identity.domain.models import AccountStatus
from rehabgraph.shared.adapters.postgres import Base, Timestamp, UuidPk, enum_column
from rehabgraph.shared.auth import Role


class AccountRow(Base):
    """# ERD: Tài khoản"""

    __tablename__ = "accounts"
    __table_args__ = (CheckConstraint("email IS NOT NULL OR phone IS NOT NULL", name="login_id"),)

    id: Mapped[UuidPk]
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[AccountStatus] = mapped_column(enum_column(AccountStatus, "account_status"))
    last_active_role: Mapped[Role | None] = mapped_column(enum_column(Role, "role"))
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[Timestamp]
    updated_at: Mapped[Timestamp]


class AccountRoleRow(Base):
    """# ERD: Admin, Lễ tân, Bác sĩ, KTV, Curator, Bệnh nhân, Người nhà (role subtypes)"""

    __tablename__ = "account_roles"

    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), primary_key=True)
    role: Mapped[Role] = mapped_column(enum_column(Role, "role"), primary_key=True)
    granted_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    granted_at: Mapped[Timestamp]
