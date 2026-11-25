"""SQLAlchemy tables of the knowledge module."""

import uuid
from datetime import date

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from rehabgraph.modules.knowledge.domain.models import (
    CuratorQueueStatus,
    DocumentStatus,
    EdgeType,
    FileType,
    NodeType,
    ReviewStatus,
)
from rehabgraph.shared.adapters.postgres import Base, Timestamp, UuidPk, enum_column
from rehabgraph.shared.auth import DetailLevel


class DocumentRow(Base):
    """# ERD: TAI_LIEU (Tài liệu)"""

    __tablename__ = "documents"

    id: Mapped[UuidPk]
    code: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(500))
    file_key: Mapped[str] = mapped_column(Text)
    file_type: Mapped[FileType] = mapped_column(enum_column(FileType, "file_type"))
    is_scan: Mapped[bool]
    status: Mapped[DocumentStatus] = mapped_column(enum_column(DocumentStatus, "document_status"))
    effective_from: Mapped[date | None] = mapped_column(Date)
    expired_at: Mapped[Timestamp | None]
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"), unique=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[Timestamp]


class DetailLevelRow(Base):
    """# ERD: Quyền xem. Holds BASIC and DEEP (seeded by the first migration)."""

    __tablename__ = "detail_levels"

    code: Mapped[DetailLevel] = mapped_column(
        enum_column(DetailLevel, "detail_level"), primary_key=True
    )
    name: Mapped[str] = mapped_column(String(64))


class DocumentSectionRow(Base):
    """# ERD: MUC_TAI_LIEU (Mục tài liệu)"""

    __tablename__ = "document_sections"

    id: Mapped[UuidPk]
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), index=True)
    parent_section_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("document_sections.id"))
    section_code: Mapped[str | None] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    page_from: Mapped[int | None]
    page_to: Mapped[int | None]
    detail_level: Mapped[DetailLevel] = mapped_column(
        enum_column(DetailLevel, "detail_level"), ForeignKey("detail_levels.code")
    )
    # TODO: set the dimension when the embedding model is chosen (BACKEND-ARCHITECTURE section 1).
    embedding: Mapped[list[float] | None] = mapped_column(Vector())


class KnowledgeNodeRow(Base):
    """# ERD: Node tri thức (Sinh ra)"""

    __tablename__ = "knowledge_nodes"

    id: Mapped[UuidPk]
    section_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_sections.id"), index=True)
    node_type: Mapped[NodeType] = mapped_column(enum_column(NodeType, "node_type"))
    name: Mapped[str] = mapped_column(String(500))
    detail_level: Mapped[DetailLevel] = mapped_column(
        enum_column(DetailLevel, "detail_level"), ForeignKey("detail_levels.code")
    )
    review_status: Mapped[ReviewStatus] = mapped_column(enum_column(ReviewStatus, "review_status"))
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("accounts.id"))
    graph_id: Mapped[str | None] = mapped_column(String(64))


class KnowledgeEdgeRow(Base):
    """# ERD: Cạnh tri thức (Nút đầu / Nút cuối)"""

    __tablename__ = "knowledge_edges"

    id: Mapped[UuidPk]
    section_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_sections.id"), index=True)
    from_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_nodes.id"), index=True)
    to_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_nodes.id"), index=True)
    edge_type: Mapped[EdgeType] = mapped_column(enum_column(EdgeType, "edge_type"))
    detail_level: Mapped[DetailLevel] = mapped_column(
        enum_column(DetailLevel, "detail_level"), ForeignKey("detail_levels.code")
    )
    review_status: Mapped[ReviewStatus] = mapped_column(enum_column(ReviewStatus, "review_status"))
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("accounts.id"))


class TestQuestionRow(Base):
    """# ERD: CAU_HOI_KIEM_THU (Câu hỏi kiểm thử)"""

    __tablename__ = "test_questions"
    __test__ = False  # not a pytest test class

    id: Mapped[UuidPk]
    question_text: Mapped[str] = mapped_column(Text)
    expected_section_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("document_sections.id")
    )
    max_detail_level: Mapped[DetailLevel] = mapped_column(enum_column(DetailLevel, "detail_level"))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[Timestamp]


class TestResultRow(Base):
    """# ERD: KET_QUA_KIEM_THU (Kết quả kiểm thử)"""

    __tablename__ = "test_results"
    __test__ = False  # not a pytest test class

    id: Mapped[UuidPk]
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), index=True)
    test_question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("test_questions.id"))
    passed: Mapped[bool]
    citation_correct: Mapped[bool]
    deep_leak: Mapped[bool]
    run_at: Mapped[Timestamp]


class UnansweredQuestionRow(Base):
    """# ERD: CAU_HOI_CHO_CURATOR (Xử lý câu hỏi thiếu nguồn)"""

    __tablename__ = "unanswered_questions"

    id: Mapped[UuidPk]
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("qa_questions.id"), unique=True)
    status: Mapped[CuratorQueueStatus] = mapped_column(
        enum_column(CuratorQueueStatus, "curator_queue_status")
    )
    handled_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("accounts.id"))
    resolution_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[Timestamp]
    resolved_at: Mapped[Timestamp | None]
