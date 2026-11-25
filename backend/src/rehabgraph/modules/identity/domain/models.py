"""Identity: accounts and the roles they hold (BUSINESS_PROJECT section 4)."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from rehabgraph.shared.auth import Role
from rehabgraph.shared.domain import DomainError, EntityId


class AccountStatus(StrEnum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"


@dataclass(frozen=True)
class RoleGrant:
    """One role held by an account. One account can hold many roles (e.g. doctor + curator)."""

    role: Role
    granted_by: EntityId
    granted_at: datetime


@dataclass
class Account:
    """# ERD: Tài khoản"""

    id: EntityId
    full_name: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
    email: str | None = None
    phone: str | None = None
    status: AccountStatus = AccountStatus.ACTIVE
    last_active_role: Role | None = None  # R-14: go straight to the last-used workspace
    created_by: EntityId | None = None  # Admin who created it (empty for the first admin)
    roles: list[RoleGrant] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Login is by email or phone number (BACKEND-ARCHITECTURE section 6.1).
        if not self.email and not self.phone:
            raise DomainError("LOGIN_ID_REQUIRED", "An account needs an email or a phone number")

    def has_role(self, role: Role) -> bool:
        return any(grant.role is role for grant in self.roles)

    def switch_workspace(self, role: Role) -> None:
        """Workspace = role. Only a role the account holds can be used (R-14)."""
        if not self.has_role(role):
            raise DomainError("ROLE_NOT_HELD", "The account does not hold this role")
        self.last_active_role = role
