"""SQLAlchemy tables of the care module."""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, SmallInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from rehabgraph.modules.care.domain.models import (
    AssignmentRole,
    AssignmentStatus,
    BodySide,
    Condition,
    EpisodeStatus,
    StrokeStage,
)
from rehabgraph.shared.adapters.postgres import Base, Timestamp, UuidPk, enum_column, no_overwrite


class TreatmentEpisodeRow(Base):
    """# ERD: DOT_DIEU_TRI (Đợt điều trị)"""

    __tablename__ = "treatment_episodes"
    __table_args__ = (
        # R-09: 1 patient has at most 1 treatment episode that is not CLOSED.
        Index(
            "uq_treatment_episodes_open_patient",
            "patient_id",
            unique=True,
            postgresql_where=text("status <> 'CLOSED'"),
        ),
    )

    id: Mapped[UuidPk]
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    condition: Mapped[Condition] = mapped_column(enum_column(Condition, "condition_code"))
    status: Mapped[EpisodeStatus] = mapped_column(enum_column(EpisodeStatus, "episode_status"))
    admitted_at: Mapped[Timestamp]
    discharged_at: Mapped[Timestamp | None]
    discharged_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("accounts.id"))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[Timestamp]


class AssignmentRow(Base):
    """# ERD: Thông tin phụ trách / Phụ trách / Phân công.

    No delete. Only `status` may be updated (R-08 exception, BACKEND-ARCHITECTURE section 7).
    """

    __tablename__ = "assignments"
    __table_args__ = (
        # 1 treatment episode has exactly 1 ACTIVE main doctor (BACKEND-ARCHITECTURE section 7).
        Index(
            "uq_assignments_active_main_doctor",
            "episode_id",
            unique=True,
            postgresql_where=text("assignment_role = 'MAIN_DOCTOR' AND status = 'ACTIVE'"),
        ),
        no_overwrite("status"),
    )

    id: Mapped[UuidPk]
    episode_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("treatment_episodes.id"), index=True)
    staff_account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), index=True)
    assignment_role: Mapped[AssignmentRole] = mapped_column(
        enum_column(AssignmentRole, "assignment_role")
    )
    status: Mapped[AssignmentStatus] = mapped_column(
        enum_column(AssignmentStatus, "assignment_status")
    )
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assignments.id"))
    assigned_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[Timestamp]


class ClinicalRecordRow(Base):
    """# ERD: Hồ sơ lâm sàng (Chẩn đoán)"""

    __tablename__ = "clinical_records"

    id: Mapped[UuidPk]
    episode_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("treatment_episodes.id"), unique=True)
    diagnosed_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    diagnosis: Mapped[str] = mapped_column(Text)
    stroke_type: Mapped[str | None] = mapped_column(String(32))
    paralysed_side: Mapped[BodySide | None] = mapped_column(enum_column(BodySide, "body_side"))
    onset_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[Timestamp]


class StatusRecordRow(Base):
    """# ERD: Trạng thái bệnh nhân (Nhập). Append-only (R-08)."""

    __tablename__ = "status_records"
    __table_args__ = no_overwrite()

    id: Mapped[UuidPk]
    clinical_record_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clinical_records.id"), index=True
    )
    entered_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    nihss: Mapped[int | None] = mapped_column(SmallInteger)
    mrs: Mapped[int | None] = mapped_column(SmallInteger)
    barthel: Mapped[int | None] = mapped_column(SmallInteger)
    computed_stage: Mapped[StrokeStage] = mapped_column(enum_column(StrokeStage, "computed_stage"))
    override_stage: Mapped[StrokeStage | None] = mapped_column(
        enum_column(StrokeStage, "override_stage")
    )
    override_reason: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[Timestamp]
