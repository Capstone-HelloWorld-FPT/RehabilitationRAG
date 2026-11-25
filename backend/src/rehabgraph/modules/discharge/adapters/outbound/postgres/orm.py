"""SQLAlchemy tables of the discharge module."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from rehabgraph.modules.discharge.domain.models import VisitStatus
from rehabgraph.shared.adapters.postgres import Base, Timestamp, UuidPk, enum_column


class DischargeChecklistItemRow(Base):
    """# ERD: Checklist xuất viện"""

    __tablename__ = "discharge_checklist_items"

    id: Mapped[UuidPk]
    episode_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("treatment_episodes.id"), index=True)
    item_label: Mapped[str] = mapped_column(String(255))
    is_met: Mapped[bool]
    unmet_reason: Mapped[str | None] = mapped_column(Text)
    checked_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    checked_at: Mapped[Timestamp]


class FollowUpVisitRow(Base):
    """# ERD: Lịch tái khám (Đặt lịch / Của / Hẹn)"""

    __tablename__ = "follow_up_visits"

    id: Mapped[UuidPk]
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    episode_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("treatment_episodes.id"), index=True)
    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), index=True)
    booked_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    scheduled_at: Mapped[Timestamp]
    status: Mapped[VisitStatus] = mapped_column(enum_column(VisitStatus, "visit_status"))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[Timestamp]
