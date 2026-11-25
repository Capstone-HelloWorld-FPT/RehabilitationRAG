"""MoH documents, sections, graph review copies and the test question set (BUSINESS_PROJECT 5.3)."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from rehabgraph.shared.auth import DetailLevel
from rehabgraph.shared.domain import DomainError, EntityId


class FileType(StrEnum):
    PDF = "PDF"
    DOC = "DOC"
    DOCX = "DOCX"


class DocumentStatus(StrEnum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"  # OCR, split, AI proposes nodes and edges
    IN_REVIEW = "IN_REVIEW"  # Curator reviews each item
    TESTING = "TESTING"  # test question set runs
    IN_USE = "IN_USE"
    EXPIRED = "EXPIRED"  # replaced by a newer document


class ReviewStatus(StrEnum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class NodeType(StrEnum):
    """Graph node labels (BACKEND-ARCHITECTURE 5.4). Sections are their own table."""

    DISEASE = "DISEASE"
    STAGE = "STAGE"
    ASSESSMENT = "ASSESSMENT"
    INTERVENTION = "INTERVENTION"
    INDICATION = "INDICATION"
    CONTRAINDICATION = "CONTRAINDICATION"
    GOAL = "GOAL"


class EdgeType(StrEnum):
    """Graph edge types (BACKEND-ARCHITECTURE 5.4)."""

    HAS_STAGE = "HAS_STAGE"
    RECOMMENDS = "RECOMMENDS"
    INDICATED_FOR = "INDICATED_FOR"
    CONTRAINDICATED_FOR = "CONTRAINDICATED_FOR"
    ASSESSED_BY = "ASSESSED_BY"
    SUPPORTED_BY = "SUPPORTED_BY"


class CuratorQueueStatus(StrEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


@dataclass(frozen=True)
class TestResult:
    """# ERD: KET_QUA_KIEM_THU (Kết quả kiểm thử)"""

    __test__ = False  # not a pytest test class

    id: EntityId
    document_id: EntityId
    test_question_id: EntityId
    passed: bool
    citation_correct: bool
    deep_leak: bool
    run_at: datetime


@dataclass
class Document:
    """# ERD: TAI_LIEU (Tài liệu). The original file is never edited (AGENTS 4)."""

    id: EntityId
    code: str  # e.g. "3553/QĐ-BYT"
    title: str
    file_key: str
    file_type: FileType
    uploaded_by: EntityId
    created_at: datetime
    is_scan: bool = False
    status: DocumentStatus = DocumentStatus.UPLOADED
    effective_from: date | None = None
    expired_at: datetime | None = None
    supersedes_id: EntityId | None = None  # Thay thế: the older document it replaces

    def ensure_can_go_live(self, results: Iterable[TestResult], today: date) -> None:
        """A document is used only when all test questions pass and its effective date has
        arrived (BUSINESS_PROJECT 5.3 step 4)."""
        results = list(results)
        if not results or not all(r.passed and not r.deep_leak for r in results):
            raise DomainError("TESTS_NOT_PASSED", "All test questions must pass first")
        if self.effective_from is None or self.effective_from > today:
            raise DomainError("NOT_EFFECTIVE_YET", "The effective date has not arrived")


@dataclass
class DocumentSection:
    """# ERD: MUC_TAI_LIEU (Mục tài liệu). Tagged Basic or Deep by the Curator."""

    id: EntityId
    document_id: EntityId
    title: str
    content: str
    detail_level: DetailLevel
    parent_section_id: EntityId | None = None
    section_code: str | None = None  # technical procedure (QTKT) number
    page_from: int | None = None
    page_to: int | None = None


@dataclass
class KnowledgeNode:
    """# ERD: Node tri thức. Curator review copy; the graph is served from Neo4j."""

    id: EntityId
    section_id: EntityId  # source passage (SUPPORTED_BY)
    node_type: NodeType
    name: str
    detail_level: DetailLevel
    review_status: ReviewStatus = ReviewStatus.PROPOSED
    reviewed_by: EntityId | None = None
    graph_id: str | None = None


@dataclass
class KnowledgeEdge:
    """# ERD: Cạnh tri thức (Nút đầu / Nút cuối)"""

    id: EntityId
    section_id: EntityId
    from_node_id: EntityId
    to_node_id: EntityId
    edge_type: EdgeType
    detail_level: DetailLevel
    review_status: ReviewStatus = ReviewStatus.PROPOSED
    reviewed_by: EntityId | None = None


@dataclass
class TestQuestion:
    """# ERD: CAU_HOI_KIEM_THU (Câu hỏi kiểm thử). Content is written by the Curator, not seeded."""

    __test__ = False  # not a pytest test class

    id: EntityId
    question_text: str
    max_detail_level: DetailLevel
    created_by: EntityId
    created_at: datetime
    expected_section_id: EntityId | None = None


@dataclass
class UnansweredQuestion:
    """# ERD: CAU_HOI_CHO_CURATOR (Xử lý câu hỏi thiếu nguồn).

    Created when the qa module sends UnansweredQuestionLogged.
    """

    id: EntityId
    question_id: EntityId
    created_at: datetime
    status: CuratorQueueStatus = CuratorQueueStatus.OPEN
    handled_by: EntityId | None = None
    resolution_note: str | None = None
    resolved_at: datetime | None = None
