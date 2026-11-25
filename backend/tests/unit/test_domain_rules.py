"""Business rules in the entities: one allowed case and one blocked case each (AGENTS section 6)."""

from datetime import UTC, date, datetime, timedelta

import pytest

from rehabgraph.modules.care.domain.models import (
    Assignment,
    AssignmentRole,
    AssignmentStatus,
    StatusRecord,
    StrokeStage,
)
from rehabgraph.modules.discharge.domain.models import (
    DischargeChecklistItem,
    ensure_ready_for_discharge,
)
from rehabgraph.modules.knowledge.domain.models import Document, FileType, TestResult
from rehabgraph.modules.pathways.domain.models import (
    EligibilityResult,
    PathwayItem,
    PathwayVersion,
    VersionStatus,
)
from rehabgraph.modules.patients.domain.models import InviteCode
from rehabgraph.modules.qa.domain.models import Answer, AnswerStatus, Citation
from rehabgraph.shared.domain import DomainError, new_id

NOW = datetime(2026, 11, 25, 8, 0, tzinfo=UTC)


def expect_error(code: str) -> pytest.RaisesExc[DomainError]:
    return pytest.raises(DomainError, check=lambda e: e.code == code)


# ---- patients: invite code (BUSINESS_PROJECT 5.4)
def test_invite_code_can_be_used_once_within_48_hours() -> None:
    code = InviteCode.issue(new_id(), new_id(), "hash", NOW)
    code.use(new_id(), NOW + timedelta(hours=47))
    assert code.used_at is not None


def test_invite_code_cannot_be_used_twice() -> None:
    code = InviteCode.issue(new_id(), new_id(), "hash", NOW)
    code.use(new_id(), NOW)
    with expect_error("INVITE_CODE_USED"):
        code.use(new_id(), NOW)


def test_invite_code_expires_after_48_hours() -> None:
    code = InviteCode.issue(new_id(), new_id(), "hash", NOW)
    with expect_error("INVITE_CODE_EXPIRED"):
        code.use(new_id(), NOW + timedelta(hours=48))


# ---- care: stage override needs a reason (BUSINESS_PROJECT 5.1 step 3)
def make_status(**overrides: object) -> StatusRecord:
    values: dict[str, object] = {
        "id": new_id(),
        "clinical_record_id": new_id(),
        "entered_by": new_id(),
        "computed_stage": StrokeStage.ACUTE,
        "recorded_at": NOW,
    }
    values.update(overrides)
    return StatusRecord(**values)  # type: ignore[arg-type]


def test_stage_override_with_reason_is_allowed() -> None:
    status = make_status(override_stage=StrokeStage.CHRONIC, override_reason="Doctor decision")
    assert status.stage is StrokeStage.CHRONIC


def test_stage_override_without_reason_is_blocked() -> None:
    with expect_error("REASON_REQUIRED"):
        make_status(override_stage=StrokeStage.CHRONIC, override_reason="  ")


# ---- care: an assignment can only go ACTIVE → ENDED (R-08 exception)
def test_active_assignment_can_be_ended() -> None:
    assignment = Assignment(new_id(), new_id(), new_id(), AssignmentRole.TECHNICIAN, new_id(), NOW)
    assignment.end()
    assert assignment.status is AssignmentStatus.ENDED


def test_ended_assignment_cannot_be_ended_again() -> None:
    assignment = Assignment(new_id(), new_id(), new_id(), AssignmentRole.TECHNICIAN, new_id(), NOW)
    assignment.end()
    with expect_error("ASSIGNMENT_ALREADY_ENDED"):
        assignment.end()


# ---- pathways: approval rules (BUSINESS_PROJECT 5.1 step 5)
def make_item(**overrides: object) -> PathwayItem:
    values: dict[str, object] = {
        "id": new_id(),
        "pathway_version_id": new_id(),
        "sort_order": 1,
        "intervention_code": "TEST-CODE",  # fake code, not a real procedure
        "eligibility": EligibilityResult.ELIGIBLE,
        "citation_ids": [new_id()],
    }
    values.update(overrides)
    return PathwayItem(**values)  # type: ignore[arg-type]


def make_version(*items: PathwayItem) -> PathwayVersion:
    return PathwayVersion(new_id(), new_id(), 1, NOW, items=list(items))


def test_version_with_valid_items_can_be_approved() -> None:
    version = make_version(
        make_item(),
        make_item(eligibility=EligibilityResult.VIOLATION, keep_reason="Doctor accepts the risk"),
        make_item(citation_ids=[], added_by_doctor=True),
    )
    version.approve(by=new_id(), at=NOW)
    assert version.status is VersionStatus.APPROVED


def test_keeping_a_violation_item_without_reason_is_blocked() -> None:
    version = make_version(make_item(eligibility=EligibilityResult.VIOLATION))
    with expect_error("REASON_REQUIRED"):
        version.approve(by=new_id(), at=NOW)


def test_ai_item_without_citation_is_blocked() -> None:
    version = make_version(make_item(citation_ids=[]))
    with expect_error("CITATION_REQUIRED"):
        version.approve(by=new_id(), at=NOW)


def test_approved_version_cannot_be_approved_again() -> None:
    version = make_version(make_item())
    version.approve(by=new_id(), at=NOW)
    with expect_error("PATHWAY_NOT_DRAFT"):
        version.approve(by=new_id(), at=NOW)


def test_draft_version_can_be_rejected() -> None:
    version = make_version(make_item())
    version.reject(by=new_id(), at=NOW, reason="Not suitable")
    assert (version.status, version.reject_reason) == (VersionStatus.REJECTED, "Not suitable")


def test_approved_version_cannot_be_rejected() -> None:
    version = make_version(make_item())
    version.approve(by=new_id(), at=NOW)
    with expect_error("PATHWAY_NOT_DRAFT"):
        version.reject(by=new_id(), at=NOW)


def test_approved_version_can_be_marked_needs_review() -> None:
    version = make_version(make_item())
    version.approve(by=new_id(), at=NOW)
    version.mark_needs_review()
    assert version.status is VersionStatus.NEEDS_REVIEW


def test_draft_version_cannot_be_marked_needs_review() -> None:
    with expect_error("PATHWAY_NOT_APPROVED"):
        make_version(make_item()).mark_needs_review()


# ---- discharge: unmet item needs a reason (BUSINESS_PROJECT 5.1 step 7)
def make_check(is_met: bool, reason: str | None = None) -> DischargeChecklistItem:
    return DischargeChecklistItem(new_id(), new_id(), "Item", is_met, new_id(), NOW, reason)


def test_discharge_with_met_items_or_reasons_is_allowed() -> None:
    ensure_ready_for_discharge([make_check(True), make_check(False, "Family will help")])


def test_discharge_with_unmet_item_without_reason_is_blocked() -> None:
    with expect_error("REASON_REQUIRED"):
        ensure_ready_for_discharge([make_check(True), make_check(False)])


# ---- qa: citations (R-01, R-02, R-03)
def make_citation(**overrides: object) -> Citation:
    values: dict[str, object] = {
        "id": new_id(),
        "document_section_id": new_id(),
        "quoted_text": "Fake passage for tests",
        "created_at": NOW,
        "answer_id": new_id(),
    }
    values.update(overrides)
    return Citation(**values)  # type: ignore[arg-type]


def test_answer_with_citation_is_allowed() -> None:
    answer = Answer(new_id(), new_id(), AnswerStatus.ANSWERED, NOW, "Text", [make_citation()])
    assert answer.citations


def test_answer_without_citation_is_blocked() -> None:
    with expect_error("CITATION_REQUIRED"):
        Answer(new_id(), new_id(), AnswerStatus.ANSWERED, NOW, "Text")


def test_no_source_answer_needs_no_citation() -> None:
    assert Answer(new_id(), new_id(), AnswerStatus.NO_SOURCE, NOW).citations == []


def test_citation_with_two_owners_is_blocked() -> None:
    with expect_error("CITATION_OWNER_INVALID"):
        make_citation(pathway_item_id=new_id())


def test_citation_without_quoted_text_is_blocked() -> None:
    with expect_error("CITATION_TEXT_REQUIRED"):
        make_citation(quoted_text=" ")


# ---- knowledge: a document goes live only after tests pass and on its effective date (5.3)
def make_document(effective_from: date | None) -> Document:
    return Document(
        new_id(),
        "TEST-DOC",
        "Fake document",
        "key",
        FileType.PDF,
        new_id(),
        NOW,
        effective_from=effective_from,
    )


def make_result(passed: bool = True, deep_leak: bool = False) -> TestResult:
    return TestResult(new_id(), new_id(), new_id(), passed, True, deep_leak, NOW)


def test_document_with_passing_tests_on_effective_date_can_go_live() -> None:
    make_document(date(2026, 11, 25)).ensure_can_go_live([make_result()], date(2026, 11, 25))


@pytest.mark.parametrize(
    "results", [[], [make_result(passed=False)], [make_result(deep_leak=True)]]
)
def test_document_without_all_tests_passed_is_blocked(results: list[TestResult]) -> None:
    with expect_error("TESTS_NOT_PASSED"):
        make_document(date(2026, 11, 1)).ensure_can_go_live(results, date(2026, 11, 25))


def test_document_before_effective_date_is_blocked() -> None:
    with expect_error("NOT_EFFECTIVE_YET"):
        make_document(date(2026, 12, 1)).ensure_can_go_live([make_result()], date(2026, 11, 25))
