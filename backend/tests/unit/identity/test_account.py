from datetime import UTC, datetime

import pytest

from rehabgraph.modules.identity.domain.models import Account, RoleGrant
from rehabgraph.shared.auth import Role
from rehabgraph.shared.domain import DomainError, new_id

NOW = datetime(2026, 11, 25, tzinfo=UTC)


def make_account(**overrides: object) -> Account:
    values: dict[str, object] = {
        "id": new_id(),
        "full_name": "Test User",
        "password_hash": "hash",
        "created_at": NOW,
        "updated_at": NOW,
        "email": "user@example.test",
    }
    values.update(overrides)
    return Account(**values)  # type: ignore[arg-type]


def test_account_with_email_or_phone_is_allowed() -> None:
    assert make_account(email=None, phone="0900000000").phone == "0900000000"


def test_account_without_email_and_phone_is_blocked() -> None:
    with pytest.raises(DomainError) as error:
        make_account(email=None, phone=None)
    assert error.value.code == "LOGIN_ID_REQUIRED"


def test_switch_to_held_role_is_allowed() -> None:
    account = make_account(roles=[RoleGrant(Role.DOCTOR, new_id(), NOW)])
    account.switch_workspace(Role.DOCTOR)
    assert account.last_active_role is Role.DOCTOR


def test_switch_to_role_not_held_is_blocked() -> None:
    account = make_account(roles=[RoleGrant(Role.DOCTOR, new_id(), NOW)])
    with pytest.raises(DomainError) as error:
        account.switch_workspace(Role.ADMIN)
    assert error.value.code == "ROLE_NOT_HELD"
