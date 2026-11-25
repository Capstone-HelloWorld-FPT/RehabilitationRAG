"""SQLAlchemy tables of the patients module."""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from rehabgraph.modules.patients.domain.models import (
    ConsentDecision,
    ConsentPurpose,
    ConsentSigner,
    Gender,
    LinkStatus,
)
from rehabgraph.shared.adapters.postgres import Base, Timestamp, UuidPk, enum_column, no_overwrite


class PatientRow(Base):
    """# ERD: BENH_NHAN (Bệnh nhân)"""

    __tablename__ = "patients"

    id: Mapped[UuidPk]
    account_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("accounts.id"), unique=True)
    full_name: Mapped[str] = mapped_column(String(255))
    date_of_birth: Mapped[date] = mapped_column(Date)
    gender: Mapped[Gender] = mapped_column(enum_column(Gender, "gender"))
    phone: Mapped[str | None] = mapped_column(String(20))
    id_card_number: Mapped[str | None] = mapped_column(String(20), unique=True)
    address: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[Timestamp]


class ConsentTermRow(Base):
    """# ERD: Điều khoản"""

    __tablename__ = "consent_terms"
    __table_args__ = (UniqueConstraint("purpose", "version"),)

    id: Mapped[UuidPk]
    purpose: Mapped[ConsentPurpose] = mapped_column(enum_column(ConsentPurpose, "consent_purpose"))
    version: Mapped[int]
    content: Mapped[str] = mapped_column(Text)
    effective_from: Mapped[Timestamp]
    created_at: Mapped[Timestamp]


class ConsentRow(Base):
    """# ERD: Đồng ý. Append-only (R-08)."""

    __tablename__ = "consents"
    __table_args__ = no_overwrite()

    id: Mapped[UuidPk]
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    term_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("consent_terms.id"))
    signed_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    signed_as: Mapped[ConsentSigner] = mapped_column(enum_column(ConsentSigner, "consent_signer"))
    decision: Mapped[ConsentDecision] = mapped_column(
        enum_column(ConsentDecision, "consent_decision")
    )
    created_at: Mapped[Timestamp]


class RepresentativeRow(Base):
    """# ERD: Đại diện"""

    __tablename__ = "representatives"
    __table_args__ = (
        # 1 patient has at most 1 ACTIVE representative (BACKEND-ARCHITECTURE section 7).
        Index(
            "uq_representatives_active_patient",
            "patient_id",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'"),
        ),
    )

    id: Mapped[UuidPk]
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    caregiver_account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    status: Mapped[LinkStatus] = mapped_column(enum_column(LinkStatus, "link_status"))
    linked_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[Timestamp]
    ended_at: Mapped[Timestamp | None]


class InviteCodeRow(Base):
    """# ERD: Mã mời"""

    __tablename__ = "invite_codes"

    id: Mapped[UuidPk]
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    code_hash: Mapped[str] = mapped_column(Text, unique=True)
    expires_at: Mapped[Timestamp]
    used_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("accounts.id"))
    used_at: Mapped[Timestamp | None]
    created_at: Mapped[Timestamp]


class CaregiverLinkRow(Base):
    """# ERD: Tài khoản liên kết"""

    __tablename__ = "caregiver_links"

    id: Mapped[UuidPk]
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    caregiver_account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), index=True)
    invite_code_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("invite_codes.id"), unique=True
    )
    status: Mapped[LinkStatus] = mapped_column(enum_column(LinkStatus, "link_status"))
    requested_at: Mapped[Timestamp]
    accepted_at: Mapped[Timestamp | None]
    removed_at: Mapped[Timestamp | None]


class CaregiverPermissionVersionRow(Base):
    """# ERD: Quyền cấp cho người nhà. Append-only (R-08)."""

    __tablename__ = "caregiver_permission_versions"
    __table_args__ = (UniqueConstraint("link_id", "version"), no_overwrite())

    id: Mapped[UuidPk]
    link_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("caregiver_links.id"))
    version: Mapped[int]
    can_view_pathway: Mapped[bool]
    can_view_questions: Mapped[bool]
    can_view_progress: Mapped[bool]
    can_mark_exercises: Mapped[bool]
    created_at: Mapped[Timestamp]
