"""Patients, consent, representatives, invite codes and caregivers (BUSINESS_PROJECT 5.1, 5.4)."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import StrEnum

from rehabgraph.shared.domain import DomainError, EntityId

INVITE_CODE_TTL = timedelta(hours=48)  # BUSINESS_PROJECT 5.4: single use, expires after 48 hours


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class ConsentPurpose(StrEnum):
    """Consent is given per purpose (BUSINESS_PROJECT 5.1 step 1)."""

    DATA_TRACKING = "DATA_TRACKING"  # store and track data
    AI_CHATBOT = "AI_CHATBOT"  # use the AI chatbot
    SHARE_WITH_CAREGIVER = "SHARE_WITH_CAREGIVER"  # share with relatives
    ANONYMOUS_RESEARCH = "ANONYMOUS_RESEARCH"  # anonymous research


class ConsentSigner(StrEnum):
    SELF = "SELF"
    REPRESENTATIVE = "REPRESENTATIVE"  # the patient cannot consent, the representative signs


class ConsentDecision(StrEnum):
    GRANTED = "GRANTED"
    WITHDRAWN = "WITHDRAWN"


class LinkStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"


@dataclass
class Patient:
    """# ERD: BENH_NHAN (Bệnh nhân). The account is created after consent, so it may be empty."""

    id: EntityId
    full_name: str
    date_of_birth: date
    gender: Gender
    created_by: EntityId  # receptionist (Tạo hồ sơ)
    created_at: datetime
    account_id: EntityId | None = None
    phone: str | None = None
    id_card_number: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class ConsentTerm:
    """# ERD: Điều khoản. One version of the text for one purpose."""

    id: EntityId
    purpose: ConsentPurpose
    version: int
    content: str
    effective_from: datetime
    created_at: datetime


@dataclass(frozen=True)
class Consent:
    """# ERD: Đồng ý. Append-only (R-08): withdrawing adds a new row."""

    id: EntityId
    patient_id: EntityId
    term_id: EntityId
    signed_by: EntityId
    signed_as: ConsentSigner
    decision: ConsentDecision
    created_at: datetime


@dataclass
class Representative:
    """# ERD: Đại diện. Linked by the receptionist, no invite code. At most 1 ACTIVE per patient."""

    id: EntityId
    patient_id: EntityId
    caregiver_account_id: EntityId
    linked_by: EntityId
    created_at: datetime
    status: LinkStatus = LinkStatus.ACTIVE
    ended_at: datetime | None = None


@dataclass
class InviteCode:
    """# ERD: Mã mời. Only the hash of the code is stored."""

    id: EntityId
    patient_id: EntityId
    code_hash: str
    created_at: datetime
    expires_at: datetime
    used_by: EntityId | None = None
    used_at: datetime | None = None

    @classmethod
    def issue(
        cls, code_id: EntityId, patient_id: EntityId, code_hash: str, now: datetime
    ) -> "InviteCode":
        return cls(code_id, patient_id, code_hash, created_at=now, expires_at=now + INVITE_CODE_TTL)

    def use(self, caregiver_account_id: EntityId, now: datetime) -> None:
        if self.used_at is not None:
            raise DomainError("INVITE_CODE_USED", "The invite code was already used")
        if now >= self.expires_at:
            raise DomainError("INVITE_CODE_EXPIRED", "The invite code has expired")
        self.used_by = caregiver_account_id
        self.used_at = now


@dataclass
class CaregiverLink:
    """# ERD: Tài khoản liên kết. Active only when the patient accepts (BUSINESS_PROJECT 5.4)."""

    id: EntityId
    patient_id: EntityId
    caregiver_account_id: EntityId
    requested_at: datetime
    invite_code_id: EntityId | None = None
    status: LinkStatus = LinkStatus.PENDING
    accepted_at: datetime | None = None
    removed_at: datetime | None = None


@dataclass(frozen=True)
class CaregiverPermissionVersion:
    """# ERD: Quyền cấp cho người nhà. Append-only: a change is a new version (R-08)."""

    id: EntityId
    link_id: EntityId
    version: int
    can_view_pathway: bool
    can_view_questions: bool
    can_view_progress: bool
    can_mark_exercises: bool
    created_at: datetime
