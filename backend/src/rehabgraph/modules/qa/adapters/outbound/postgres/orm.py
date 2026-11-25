"""SQLAlchemy tables of the qa module."""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from rehabgraph.modules.qa.domain.models import AnswerStatus
from rehabgraph.shared.adapters.postgres import Base, Timestamp, UuidPk, enum_column
from rehabgraph.shared.auth import DetailLevel, Role


class QuestionRow(Base):
    """# ERD: CAU_HOI (Lịch sử hỏi đáp - câu hỏi)"""

    __tablename__ = "qa_questions"

    id: Mapped[UuidPk]
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), index=True)
    active_role: Mapped[Role] = mapped_column(enum_column(Role, "role"))
    detail_level: Mapped[DetailLevel] = mapped_column(enum_column(DetailLevel, "detail_level"))
    question_text: Mapped[str] = mapped_column(Text)
    is_urgent: Mapped[bool]
    is_out_of_scope: Mapped[bool]
    created_at: Mapped[Timestamp]


class AnswerRow(Base):
    """# ERD: CAU_TRA_LOI (Lịch sử hỏi đáp - câu trả lời)"""

    __tablename__ = "qa_answers"

    id: Mapped[UuidPk]
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("qa_questions.id"), unique=True)
    answer_text: Mapped[str | None] = mapped_column(Text)
    status: Mapped[AnswerStatus] = mapped_column(enum_column(AnswerStatus, "answer_status"))
    created_at: Mapped[Timestamp]


class CitationRow(Base):
    """# ERD: TRICH_DAN (Nguồn trích dẫn)"""

    __tablename__ = "citations"
    __table_args__ = (
        CheckConstraint("num_nonnulls(pathway_item_id, answer_id) = 1", name="one_owner"),
    )

    id: Mapped[UuidPk]
    document_section_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("document_sections.id"), index=True
    )
    pathway_item_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("pathway_items.id"), index=True
    )
    answer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("qa_answers.id"), index=True)
    quoted_text: Mapped[str] = mapped_column(Text)  # copy of the passage at answer time (R-03)
    page: Mapped[int | None]
    created_at: Mapped[Timestamp]
