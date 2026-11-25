"""Treatment episodes, assignments, clinical records and patient status (BUSINESS_PROJECT 5.1)."""

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from rehabgraph.shared.domain import DomainError, EntityId


class Condition(StrEnum):
    """The MVP only covers rehabilitation for hemiplegia after stroke (BUSINESS_PROJECT 3.1)."""

    STROKE = "STROKE"  # TBMMN


class EpisodeStatus(StrEnum):
    IN_TREATMENT = "IN_TREATMENT"
    HOME_FOLLOW_UP = "HOME_FOLLOW_UP"  # after discharge (BUSINESS_PROJECT 5.1 step 7)
    CLOSED = "CLOSED"


class AssignmentRole(StrEnum):
    MAIN_DOCTOR = "MAIN_DOCTOR"  # exactly 1 per treatment episode
    TECHNICIAN = "TECHNICIAN"  # 0 or more


class AssignmentStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"


class StrokeStage(StrEnum):
    """Stage names from BUSINESS_PROJECT 5.1 step 3."""

    HYPERACUTE = "HYPERACUTE"
    ACUTE = "ACUTE"
    EARLY_SUBACUTE = "EARLY_SUBACUTE"
    LATE_SUBACUTE = "LATE_SUBACUTE"
    CHRONIC = "CHRONIC"


class BodySide(StrEnum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


@dataclass
class TreatmentEpisode:
    """# ERD: DOT_DIEU_TRI (Đợt điều trị). At most 1 not CLOSED per patient (R-09)."""

    id: EntityId
    patient_id: EntityId
    admitted_at: datetime
    created_by: EntityId
    created_at: datetime
    condition: Condition = Condition.STROKE
    status: EpisodeStatus = EpisodeStatus.IN_TREATMENT
    discharged_at: datetime | None = None
    discharged_by: EntityId | None = None


@dataclass
class Assignment:
    """# ERD: Thông tin phụ trách / Phụ trách / Phân công.

    No delete. Only `status` may change (R-08 exception): ACTIVE → ENDED. A new person is a new
    row; `supersedes_id` points to the assignment it replaces.
    """

    id: EntityId
    episode_id: EntityId
    staff_account_id: EntityId
    assignment_role: AssignmentRole
    assigned_by: EntityId  # receptionist (BUSINESS_PROJECT 5.1 step 2)
    created_at: datetime
    status: AssignmentStatus = AssignmentStatus.ACTIVE
    supersedes_id: EntityId | None = None

    def end(self) -> None:
        if self.status is AssignmentStatus.ENDED:
            raise DomainError("ASSIGNMENT_ALREADY_ENDED", "The assignment has already ended")
        self.status = AssignmentStatus.ENDED


@dataclass
class ClinicalRecord:
    """# ERD: Hồ sơ lâm sàng (Chẩn đoán). One per treatment episode."""

    id: EntityId
    episode_id: EntityId
    diagnosed_by: EntityId
    diagnosis: str
    created_at: datetime
    # TODO: turn into an enum once the team gives the list from the MoH documents.
    stroke_type: str | None = None
    paralysed_side: BodySide | None = None
    onset_date: date | None = None


@dataclass(frozen=True)
class StatusRecord:
    """# ERD: Trạng thái bệnh nhân (Nhập). Append-only (R-08).

    `computed_stage` is stored as given. The rule that computes it needs an MoH source and is not
    written yet (AGENTS 4.1). Only a doctor may override the stage (checked in the use case).
    """

    id: EntityId
    clinical_record_id: EntityId
    entered_by: EntityId
    computed_stage: StrokeStage
    recorded_at: datetime
    nihss: int | None = None
    mrs: int | None = None
    barthel: int | None = None
    override_stage: StrokeStage | None = None
    override_reason: str | None = None

    def __post_init__(self) -> None:
        # BUSINESS_PROJECT 5.1 step 3: overriding the stage needs a reason.
        if self.override_stage is not None and not (self.override_reason or "").strip():
            raise DomainError("REASON_REQUIRED", "Overriding the stage needs a reason")

    @property
    def stage(self) -> StrokeStage:
        return self.override_stage or self.computed_stage
