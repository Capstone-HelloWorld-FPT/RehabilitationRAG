"""Pathways, versions, items, technician proposals and home exercises (BUSINESS_PROJECT 5.1)."""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum

from rehabgraph.shared.auth import Role
from rehabgraph.shared.domain import DomainError, EntityId


class VersionStatus(StrEnum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"  # a cited document section changed (BUSINESS_PROJECT 5.3)


class EligibilityResult(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    VIOLATION = "VIOLATION"  # breaks a contraindication
    MISSING_DATA = "MISSING_DATA"


class ProposalType(StrEnum):
    STAGE_CHANGE = "STAGE_CHANGE"
    PATHWAY_EDIT = "PATHWAY_EDIT"


class ProposalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class Pathway:
    """# ERD: Lộ trình (Dùng trong). One per treatment episode, changes are new versions."""

    id: EntityId
    episode_id: EntityId
    created_at: datetime


@dataclass
class PathwayItem:
    """# ERD: Mục lộ trình"""

    id: EntityId
    pathway_version_id: EntityId
    sort_order: int
    intervention_code: str  # technical procedure (QTKT) code
    eligibility: EligibilityResult
    citation_ids: list[EntityId] = field(default_factory=list)  # citations (TRICH_DAN)
    added_by_doctor: bool = False  # shown as "Added by doctor" (BUSINESS_PROJECT 5.1 step 5)
    keep_reason: str | None = None  # reason for keeping a violation item

    def ensure_valid_for_approval(self) -> None:
        if self.eligibility is EligibilityResult.VIOLATION and not (self.keep_reason or "").strip():
            raise DomainError("REASON_REQUIRED", "Keeping a violation item needs a reason")
        if not self.citation_ids and not self.added_by_doctor:
            raise DomainError("CITATION_REQUIRED", "An AI-created item must have a citation")


@dataclass
class PathwayVersion:
    """# ERD: Lộ trình - phiên bản (Duyệt).

    No delete. Only the status columns may change (R-08 exception): `status`, `decided_by`,
    `decided_at`, `reject_reason`. Items never change: an edit is a new version.
    """

    id: EntityId
    pathway_id: EntityId
    version: int
    created_at: datetime
    generated_by_ai: bool = True
    status: VersionStatus = VersionStatus.DRAFT
    decided_by: EntityId | None = None
    decided_at: datetime | None = None
    reject_reason: str | None = None
    items: list[PathwayItem] = field(default_factory=list)

    def approve(self, by: EntityId, at: datetime) -> None:
        if self.status is not VersionStatus.DRAFT:
            raise DomainError("PATHWAY_NOT_DRAFT", "Only a draft version can be approved")
        for item in self.items:
            item.ensure_valid_for_approval()
        self.status, self.decided_by, self.decided_at = VersionStatus.APPROVED, by, at

    def reject(self, by: EntityId, at: datetime, reason: str | None = None) -> None:
        if self.status is not VersionStatus.DRAFT:
            raise DomainError("PATHWAY_NOT_DRAFT", "Only a draft version can be rejected")
        self.status, self.decided_by, self.decided_at = VersionStatus.REJECTED, by, at
        self.reject_reason = reason

    def mark_needs_review(self) -> None:
        """A cited document section changed (BUSINESS_PROJECT 5.3 step 5)."""
        if self.status is not VersionStatus.APPROVED:
            raise DomainError("PATHWAY_NOT_APPROVED", "Only an approved version needs review")
        self.status = VersionStatus.NEEDS_REVIEW


@dataclass
class TechnicianProposal:
    """# ERD: Đề xuất (Gửi / Xử lý / Về). A technician proposes, the doctor decides (R-10)."""

    id: EntityId
    pathway_id: EntityId
    submitted_by: EntityId
    proposal_type: ProposalType
    content: str
    created_at: datetime
    status: ProposalStatus = ProposalStatus.PENDING
    reviewed_by: EntityId | None = None
    review_note: str | None = None
    reviewed_at: datetime | None = None


@dataclass
class Exercise:
    """# ERD: Bài tập phục hồi (Sở hữu / Có).

    TODO: the details of an exercise session at home are open (BUSINESS_PROJECT Q-05).
    """

    id: EntityId
    patient_id: EntityId
    pathway_version_id: EntityId
    name: str
    instructions: str
    created_at: datetime
    pathway_item_id: EntityId | None = None


@dataclass(frozen=True)
class ExerciseMark:
    """# ERD: Đánh dấu. Marked by the patient, a relative or a technician."""

    id: EntityId
    exercise_id: EntityId
    marked_by: EntityId
    marker_role: Role
    session_date: date
    completed: bool
    created_at: datetime
    note: str | None = None
