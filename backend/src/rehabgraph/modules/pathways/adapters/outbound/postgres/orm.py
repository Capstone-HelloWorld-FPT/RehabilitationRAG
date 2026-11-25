"""SQLAlchemy tables of the pathways module."""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from rehabgraph.modules.pathways.domain.models import (
    EligibilityResult,
    ProposalStatus,
    ProposalType,
    VersionStatus,
)
from rehabgraph.shared.adapters.postgres import Base, Timestamp, UuidPk, enum_column, no_overwrite
from rehabgraph.shared.auth import Role


class PathwayRow(Base):
    """# ERD: Lộ trình (Dùng trong)"""

    __tablename__ = "pathways"

    id: Mapped[UuidPk]
    episode_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("treatment_episodes.id"), unique=True)
    created_at: Mapped[Timestamp]


class PathwayVersionRow(Base):
    """# ERD: Lộ trình - phiên bản (Duyệt). No delete, only the status columns may be updated."""

    __tablename__ = "pathway_versions"
    __table_args__ = (
        UniqueConstraint("pathway_id", "version"),
        no_overwrite("status", "decided_by", "decided_at", "reject_reason"),
    )

    id: Mapped[UuidPk]
    pathway_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pathways.id"))
    version: Mapped[int]
    status: Mapped[VersionStatus] = mapped_column(enum_column(VersionStatus, "version_status"))
    generated_by_ai: Mapped[bool]
    decided_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("accounts.id"))
    decided_at: Mapped[Timestamp | None]
    reject_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[Timestamp]


class PathwayItemRow(Base):
    """# ERD: Mục lộ trình"""

    __tablename__ = "pathway_items"

    id: Mapped[UuidPk]
    pathway_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pathway_versions.id"), index=True
    )
    sort_order: Mapped[int]
    intervention_code: Mapped[str] = mapped_column(String(32))
    eligibility: Mapped[EligibilityResult] = mapped_column(
        enum_column(EligibilityResult, "eligibility_result")
    )
    added_by_doctor: Mapped[bool]
    keep_reason: Mapped[str | None] = mapped_column(Text)


class TechnicianProposalRow(Base):
    """# ERD: Đề xuất (Gửi / Xử lý / Về)"""

    __tablename__ = "technician_proposals"
    __table_args__ = (
        # R-10: 1 pathway has at most 1 PENDING stage-change proposal.
        Index(
            "uq_technician_proposals_pending_stage_change",
            "pathway_id",
            unique=True,
            postgresql_where=text("proposal_type = 'STAGE_CHANGE' AND status = 'PENDING'"),
        ),
    )

    id: Mapped[UuidPk]
    pathway_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pathways.id"), index=True)
    submitted_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    proposal_type: Mapped[ProposalType] = mapped_column(enum_column(ProposalType, "proposal_type"))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[ProposalStatus] = mapped_column(enum_column(ProposalStatus, "proposal_status"))
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("accounts.id"))
    review_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[Timestamp]
    reviewed_at: Mapped[Timestamp | None]


class ExerciseRow(Base):
    """# ERD: Bài tập phục hồi (Sở hữu / Có)"""

    __tablename__ = "exercises"

    id: Mapped[UuidPk]
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    pathway_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pathway_versions.id"))
    pathway_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("pathway_items.id"))
    name: Mapped[str] = mapped_column(String(255))
    instructions: Mapped[str] = mapped_column(Text)
    created_at: Mapped[Timestamp]


class ExerciseMarkRow(Base):
    """# ERD: Đánh dấu"""

    __tablename__ = "exercise_marks"

    id: Mapped[UuidPk]
    exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exercises.id"), index=True)
    marked_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    marker_role: Mapped[Role] = mapped_column(enum_column(Role, "role"))
    session_date: Mapped[date] = mapped_column(Date)
    completed: Mapped[bool]
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[Timestamp]
