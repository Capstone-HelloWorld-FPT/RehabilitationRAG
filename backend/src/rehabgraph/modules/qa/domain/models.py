"""AI Q&A: questions, answers and citations (BUSINESS_PROJECT 5.2, R-01 to R-03)."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from rehabgraph.shared.auth import DetailLevel, Role
from rehabgraph.shared.domain import DomainError, EntityId


class AnswerStatus(StrEnum):
    ANSWERED = "ANSWERED"
    NO_SOURCE = "NO_SOURCE"  # "no information yet", logged for the Curator (R-02)
    URGENT = "URGENT"  # emergency instructions shown
    OUT_OF_SCOPE = "OUT_OF_SCOPE"  # refused politely


@dataclass(frozen=True)
class Question:
    """# ERD: CAU_HOI (Lịch sử hỏi đáp - câu hỏi). Guests are not stored (quota lives in Redis)."""

    id: EntityId
    account_id: EntityId
    active_role: Role
    detail_level: DetailLevel
    question_text: str
    created_at: datetime
    is_urgent: bool = False
    is_out_of_scope: bool = False


@dataclass(frozen=True)
class Citation:
    """# ERD: TRICH_DAN (Nguồn trích dẫn). Keeps a copy of the quoted passage (R-03).

    Belongs to exactly one of: an answer, or a pathway item.
    """

    id: EntityId
    document_section_id: EntityId
    quoted_text: str
    created_at: datetime
    answer_id: EntityId | None = None
    pathway_item_id: EntityId | None = None
    page: int | None = None

    def __post_init__(self) -> None:
        if (self.answer_id is None) == (self.pathway_item_id is None):
            raise DomainError(
                "CITATION_OWNER_INVALID", "A citation belongs to one answer or one pathway item"
            )
        if not self.quoted_text.strip():
            raise DomainError("CITATION_TEXT_REQUIRED", "A citation keeps a copy of the passage")


@dataclass(frozen=True)
class Answer:
    """# ERD: CAU_TRA_LOI (Lịch sử hỏi đáp - câu trả lời)"""

    id: EntityId
    question_id: EntityId
    status: AnswerStatus
    created_at: datetime
    answer_text: str | None = None
    citations: list[Citation] = field(default_factory=list)

    def __post_init__(self) -> None:
        # R-01 / R-02: no source means no medical answer.
        if self.status is AnswerStatus.ANSWERED and not self.citations:
            raise DomainError("CITATION_REQUIRED", "An answer must cite at least one source")
