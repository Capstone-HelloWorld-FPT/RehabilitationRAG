"""Discharge checklist and follow-up visits (BUSINESS_PROJECT 5.1 step 7)."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from rehabgraph.shared.domain import DomainError, EntityId


class VisitStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    MISSED = "MISSED"


@dataclass
class DischargeChecklistItem:
    """# ERD: Checklist xuất viện. Item labels are not seeded here: they need an MoH source."""

    id: EntityId
    episode_id: EntityId
    item_label: str
    is_met: bool
    checked_by: EntityId
    checked_at: datetime
    unmet_reason: str | None = None


def ensure_ready_for_discharge(items: Iterable[DischargeChecklistItem]) -> None:
    """Discharging with an unmet item needs a reason (BUSINESS_PROJECT 5.1 step 7)."""
    for item in items:
        if not item.is_met and not (item.unmet_reason or "").strip():
            raise DomainError("REASON_REQUIRED", "An unmet checklist item needs a reason")


@dataclass
class FollowUpVisit:
    """# ERD: Lịch tái khám (Đặt lịch / Của / Hẹn). Booked by the receptionist."""

    id: EntityId
    patient_id: EntityId
    episode_id: EntityId
    doctor_id: EntityId
    booked_by: EntityId
    scheduled_at: datetime
    created_at: datetime
    status: VisitStatus = VisitStatus.SCHEDULED
    note: str | None = None
