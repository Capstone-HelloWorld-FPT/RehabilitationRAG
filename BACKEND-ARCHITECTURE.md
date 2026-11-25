# BACKEND-ARCHITECTURE – RehabGraph-RAG

This document describes the backend architecture: **FastAPI + Hexagonal (Ports & Adapters)**.
For business rules, see [BUSINESS_PROJECT.md](BUSINESS_PROJECT.md). For rules for AI coding agents, see [AGENTS.md](AGENTS.md).

Version: v1.1, 25/11/2026. All technologies and designs in this file are decided, except the embedding model (chosen later).

**Current state:** the project skeleton exists (folders + config, `.gitkeep` in empty folders). **No application code yet.** Packages are installed and locked in `backend/uv.lock`.

---

## 1. Technology

Versions below are the ones locked in `uv.lock` on 25/11/2026.

| Part | Choice | Note |
|---|---|---|
| Language | Python 3.12 | Pinned in `backend/.python-version`. uv downloads it if needed. |
| Web framework | FastAPI 0.165 | Decided |
| Data types, validation | Pydantic 2.14, pydantic-settings 2.16 | |
| Business database | PostgreSQL 16 | Decided. Docker image `pgvector/pgvector:pg16` (default), or Neon (hosted PostgreSQL with pgvector) through `DATABASE_URL`. Real patient data on Neon needs a team decision first (Decree 13/2023, AGENTS section 8). |
| ORM, migrations | SQLAlchemy 2.1 (async, asyncpg) + Alembic 1.20 | Decided |
| Vector search | pgvector (inside PostgreSQL) | Decided |
| Knowledge graph | Neo4j 5 (server), Python driver `neo4j` 6.4 | Decided. Can be swapped for PostgreSQL because it sits behind a port. |
| Background jobs | arq 0.28 + Redis 7 | Decided. Used for document loading, OCR, running the test question set. |
| LLM | **OpenRouter** | Decided. Goes through the `LLMGateway` port, adapter `OpenRouterGateway` (OpenAI-style API, called with `httpx`). Changing the model only needs an environment variable. |
| Auth | PyJWT 2.15, argon2-cffi 25.1 | |
| Package manager | uv | Decided |
| Tests | pytest 9, pytest-asyncio 1.5, testcontainers 4 | |
| Lint, format, types | ruff 0.17, mypy 2.4 (strict), import-linter 2.17 | Config in `backend/pyproject.toml`. |
| Local run | Docker Compose (`docker-compose.yml` at the repo root) | Runs `postgres`, `neo4j`, `redis`, `api` (`backend/docker/Dockerfile`) and `frontend` (nginx, `frontend/docker/Dockerfile`). |

---

## 2. What Hexagonal means (short version)

Idea: **the business logic sits in the middle and does not depend on technology.** Technology (FastAPI, PostgreSQL, Neo4j, LLM) plugs in from outside through "sockets" called **ports**. The things that plug in are called **adapters**.

```
                 ┌──────────────────────────────────────────┐
  HTTP request → │  Inbound adapter (FastAPI router)        │
                 └──────────────┬───────────────────────────┘
                                │ calls
                 ┌──────────────▼───────────────────────────┐
                 │  Application (use case)                  │
                 │  - checks permissions, calls domain/port │
                 │  ┌────────────────────────────────────┐  │
                 │  │  Domain (entities, business rules) │  │
                 │  │  imports NOTHING from outside      │  │
                 │  └────────────────────────────────────┘  │
                 └──────────────┬───────────────────────────┘
                                │ through outbound port (interface)
                 ┌──────────────▼───────────────────────────┐
                 │  Outbound adapter                        │
                 │  PostgreSQL / Neo4j / LLM / OCR / Email  │
                 └──────────────────────────────────────────┘
```

**Dependency rule (mandatory):**

| Layer | May import | Must not import |
|---|---|---|
| `domain` | Only the Python standard library and `shared/domain` | FastAPI, SQLAlchemy, Neo4j, Pydantic, LLM SDK, `application`, `adapters` |
| `application` | `domain`, `ports` | `adapters`, FastAPI, SQLAlchemy |
| `ports` | `domain` | `adapters` |
| `adapters` | Everything above + external libraries | Adapters of other modules |

This rule is checked automatically with `import-linter` in CI (see section 10). The contracts are in `[tool.importlinter]` in `backend/pyproject.toml`:

1. **Layers** inside each module: `adapters` > `application` > `ports` > `domain`.
2. **Forbidden**: `domain`, `application`, `ports` and `shared/domain`, `shared/auth`, `shared/ports` must not import FastAPI, Pydantic, SQLAlchemy, Neo4j, Redis, httpx, JWT... (`shared/auth` is pure Python too, because use cases import it.)
3. **Independence**: modules do not import each other. Each allowed exception (an adapter calling `B/ports/inbound.py`, a listener importing an event class from `B/domain/events.py`) is written one by one in `ignore_imports`.

Note: `lint-imports` only works once the packages have `__init__.py` files (they do not yet, see "Current state").

---

## 3. Folder structure

Split by **business module** first. Inside each module, split by hexagonal layer.

Files that exist today: `pyproject.toml`, `uv.lock`, `.python-version`, `.env.example`, `README.md`. Every other folder only has a `.gitkeep`. Files marked *(later)* are added with the first code.

```
backend/
├── pyproject.toml                 # packages + config for ruff, mypy, pytest, import-linter
├── uv.lock
├── .python-version                # 3.12
├── .env.example
├── alembic.ini                    # (later)
├── migrations/                    # Alembic migrations
│   └── versions/
├── docker/
│   └── Dockerfile                 # (later)
├── src/rehabgraph/
│   ├── main.py                    # create the FastAPI app, mount routers, middleware
│   ├── config.py                  # read environment variables (pydantic-settings)
│   ├── container.py               # wire ports to adapters (dependency injection)
│   ├── worker.py                  # entry point for background jobs (arq)
│   │
│   ├── shared/                    # shared by all modules
│   │   ├── domain/                # Entity base, IDs, business errors, Clock, DomainEvent
│   │   ├── auth/                  # ActorContext, Role, Permission, common policies
│   │   ├── ports/                 # UnitOfWork, EventBus, AuditLogPort, Clock
│   │   └── adapters/              # SQLAlchemy session, Unit of Work, in-process event bus
│   │
│   └── modules/
│       ├── identity/              # accounts, 7 roles (+ Guest without account), workspaces, login
│       ├── patients/              # patients, consent, relatives, invite codes, relative permissions
│       ├── care/                  # treatment episodes, assignments, clinical records, status, stages
│       ├── pathways/              # pathways, versions, items, technician proposals, exercise sessions
│       ├── discharge/             # discharge, checklist, follow-up visits
│       ├── knowledge/             # MoH documents, loading, OCR, graph, detail levels, test set
│       ├── qa/                    # AI Q&A, Graph-RAG, citations, guest quota
│       ├── notifications/         # notifications
│       └── audit/                 # audit log (append-only)
│
└── tests/
    ├── unit/                      # domain + application tests (with fake adapters)
    ├── integration/               # adapter tests with a real DB (testcontainers)
    ├── api/                       # end-to-end HTTP tests
    └── rag_eval/                  # AI quality test question set
```

### 3.1 Inside one module

Example: the `pathways` module:

```
modules/pathways/
├── domain/
│   ├── models.py          # Pathway, PathwayVersion, PathwayItem, TechnicianProposal
│   ├── rules.py           # rules: only the assigned doctor approves, keeping a violation needs a reason...
│   ├── events.py          # PathwayApproved, PathwayMarkedNeedsReview
│   └── errors.py          # PathwayAlreadyApproved, ReasonRequired...
├── application/
│   ├── commands/          # one file per use case
│   │   ├── generate_draft_pathway.py
│   │   ├── approve_pathway_version.py
│   │   ├── reject_pathway_version.py
│   │   └── submit_technician_proposal.py
│   ├── queries/           # read data (light CQRS)
│   │   └── get_patient_pathway.py
│   └── dto.py             # use case input / output (dataclass, not Pydantic)
├── ports/
│   ├── inbound.py         # (optional) use case Protocols if another module needs to call them
│   └── outbound.py        # PathwayRepository, PathwayGenerator, CareQueryPort...
└── adapters/
    ├── inbound/
    │   └── http/
    │       ├── router.py   # FastAPI router
    │       └── schemas.py  # Pydantic request / response
    └── outbound/
        ├── postgres/
        │   ├── orm.py          # SQLAlchemy tables
        │   └── repository.py   # SqlPathwayRepository implements PathwayRepository
        └── graph_rag/
            └── generator.py    # GraphRagPathwayGenerator implements PathwayGenerator
```

### 3.2 How modules talk to each other

- Module A **does not import** the `domain` or `adapters` of module B.
- If module A needs data from B: A declares an **outbound port** in `A/ports/outbound.py`. The adapter of that port calls B's `application` (through `B/ports/inbound.py`).
- If something happened and others must react (e.g., a document was replaced → pathway "Needs review"): use a **domain event** through the `EventBus`.

| Event | Sent by | Listened by | Action |
|---|---|---|---|
| `DocumentSuperseded` | knowledge | pathways | Mark "Needs review" on pathways that cite a changed section |
| `ConsentWithdrawn` | patients | qa, patients | Stop the chatbot for the patient / block relatives, depending on the purpose |
| `UrgentQuestionAsked` | qa | notifications | Notify the assigned doctor / technician |
| `UnansweredQuestionLogged` | qa | knowledge | Create a CAU_HOI_CHO_CURATOR (question waiting for the Curator) |
| `TechnicianProposalSubmitted` | pathways | notifications | Notify the doctor |
| `PatientDischarged` | discharge | care | Move the treatment episode to THEO_DOI_TAI_NHA (home follow-up) |

---

## 4. Code examples for each layer

### 4.1 Domain (pure Python)

```python
# modules/pathways/domain/models.py
from dataclasses import dataclass, field
from enum import StrEnum
from rehabgraph.shared.domain import EntityId, DomainError

class EligibilityResult(StrEnum):
    ELIGIBLE = "eligible"
    VIOLATION = "violation"          # breaks a contraindication
    MISSING_DATA = "missing_data"

@dataclass
class PathwayItem:
    intervention_code: str           # technical procedure (QTKT) code
    eligibility: EligibilityResult
    citation_ids: list[EntityId]     # citations to document sections (MUC_TAI_LIEU)
    added_by_doctor: bool = False
    keep_reason: str | None = None   # reason for keeping a violation item

    def ensure_valid_for_approval(self) -> None:
        if self.eligibility is EligibilityResult.VIOLATION and not self.keep_reason:
            raise DomainError("REASON_REQUIRED", "Keeping a violation item needs a reason")
        if not self.citation_ids and not self.added_by_doctor:
            raise DomainError("CITATION_REQUIRED", "An AI-created item must have a citation")
```

### 4.2 Outbound port (interface)

```python
# modules/pathways/ports/outbound.py
from typing import Protocol
from rehabgraph.shared.domain import EntityId
from ..domain.models import Pathway, PathwayVersion

class PathwayRepository(Protocol):
    async def get(self, pathway_id: EntityId) -> Pathway: ...
    async def get_by_patient(self, patient_id: EntityId) -> Pathway | None: ...
    async def save(self, pathway: Pathway) -> None:   # only adds new versions, never overwrites
        ...

class PathwayGenerator(Protocol):
    """Create a draft pathway from MoH knowledge. Every item must have a citation."""
    async def generate(self, patient_status: "PatientStatusSnapshot", role: str) -> PathwayVersion: ...

class CareQueryPort(Protocol):
    """Ask the care module: is this doctor assigned to this treatment episode?"""
    async def is_assigned(self, account_id: EntityId, episode_id: EntityId, role: str) -> bool: ...
```

### 4.3 Application (use case)

```python
# modules/pathways/application/commands/approve_pathway_version.py
from dataclasses import dataclass
from rehabgraph.shared.auth import ActorContext, Permission, require
from rehabgraph.shared.domain import NotFoundError
from rehabgraph.shared.ports import UnitOfWork, AuditLogPort
from ...ports.outbound import PathwayRepository, CareQueryPort

@dataclass(frozen=True)
class ApprovePathwayVersion:
    pathway_id: str
    version_id: str

class ApprovePathwayVersionHandler:
    def __init__(self, repo: PathwayRepository, care: CareQueryPort,
                 uow: UnitOfWork, audit: AuditLogPort) -> None:
        self.repo, self.care, self.uow, self.audit = repo, care, uow, audit

    async def __call__(self, cmd: ApprovePathwayVersion, actor: ActorContext) -> None:
        require(actor, Permission.PATHWAY_APPROVE)             # 1. permission by role
        async with self.uow:
            pathway = await self.repo.get(cmd.pathway_id)
            if not await self.care.is_assigned(actor.account_id, pathway.episode_id, "DOCTOR"):
                await self.audit.denied(actor, "pathway", cmd.pathway_id, "approve")
                raise NotFoundError("pathway", cmd.pathway_id)   # 2. permission by assignment → 404
            pathway.approve(cmd.version_id, by=actor.account_id)   # 3. rule inside the domain
            await self.repo.save(pathway)
            await self.audit.granted(actor, "pathway", cmd.pathway_id, "approve")
            await self.uow.commit()                            # 4. data + audit log in 1 transaction
```

### 4.4 Inbound adapter (FastAPI)

```python
# modules/pathways/adapters/inbound/http/router.py
from fastapi import APIRouter, Depends
from rehabgraph.shared.adapters.http import get_actor
from rehabgraph.container import Container
from ....application.commands.approve_pathway_version import ApprovePathwayVersion

router = APIRouter(prefix="/api/v1/pathways", tags=["pathways"])

@router.post("/{pathway_id}/versions/{version_id}/approve", status_code=204)
async def approve(pathway_id: str, version_id: str,
                  actor = Depends(get_actor),
                  handler = Depends(Container.approve_pathway_version)):
    await handler(ApprovePathwayVersion(pathway_id, version_id), actor)
```

A router does **only** 3 things: read the request, call the use case, return the response. No business logic in routers.

---

## 5. Graph-RAG (`qa` and `knowledge` modules)

### 5.1 Flow for answering one question

```
Question
  │
  ▼
[1] Safety check ── urgent? → return emergency instructions + send UrgentQuestionAsked
  │              └ out of scope? → refuse
  ▼
[2] Get the current role (workspace) + level chosen by the user → allowed level (Basic, or Basic + Deep)
  ▼
[3] Find the concepts in the question (entity linking) → nodes in the graph
  ▼
[4] Search the graph (walk 1–2 steps along edges) + vector search on passages
    *** ONLY nodes / passages the role may see, ONLY documents in effect ***
  ▼
[5] Merge and rank the source passages → context
  ▼
[6] The LLM writes the answer, each point tagged with a passage code [S1], [S2]...
  ▼
[7] Check citations: does every point have a citation? is every citation code in the context?
    Fails → drop the answer, return "no information yet", send UnansweredQuestionLogged
  ▼
[8] Save CAU_HOI, CAU_TRA_LOI, TRICH_DAN (question, answer, citation with a copy of the passage) + audit log → return
```

**Step [4] is where access is blocked.** Filtering happens inside the graph / vector query, not after the LLM has read the content. So the LLM **never sees** content above the user's access.

### 5.2 Graph-RAG ports and adapters

| Port (in `qa/ports/outbound.py` or `knowledge/ports/outbound.py`) | Adapter | Job |
|---|---|---|
| `SafetyClassifier` | `LlmSafetyClassifier` + keyword rules | Detect urgent / out-of-scope questions |
| `EntityLinker` | `GraphEntityLinker` (Neo4j full-text + aliases) | Question → graph nodes |
| `GraphRetriever` | `Neo4jGraphRetriever` | Walk edges, filtered by detail level + effective date |
| `PassageRetriever` | `PgVectorPassageRetriever` | Find passages with close meaning, filtered by detail level + effective date |
| `Reranker` | `SimpleScoreReranker` (can be swapped for a cross-encoder) | Rank source passages |
| `LLMGateway` | `OpenRouterGateway` | Call the LLM through OpenRouter. The model is set by the `LLM_MODEL` environment variable. |
| `EmbeddingModel` | Multilingual embedding model, through OpenRouter or run locally (**model chosen later**) | Create vectors |
| `CitationValidator` | **Domain service** (not an adapter) | Check R-01, R-02 |

The use case `AskQuestionHandler` (in `qa/application/commands/ask_question.py`) only connects the ports above in order. Changing Neo4j, the LLM, or the search method: **the use case does not change**.

### 5.3 Document loading (`knowledge` module, background jobs)

```
Curator uploads a file
  → [job] store the original file (FileStorage port)
  → [job] OCR if it is a scan (OcrEngine port) → GOI_Y_SUA_OCR (OCR fix suggestions) for unsure spots
  → [job] split sections / procedures (DocumentSplitter port)
  → [job] LLM proposes nodes + edges (KnowledgeExtractor port), each node / edge points to its source passage
  → Curator reviews each item, tags it Basic / Deep
  → [job] create embeddings, write to Neo4j + pgvector
  → [job] run CAU_HOI_KIEM_THU (test questions) → KET_QUA_KIEM_THU (test results)
  → All pass + effective date reached → TAI_LIEU (document) becomes "in use"
```

### 5.4 Graph model

| Node | Example |
|---|---|
| `Disease` | Hemiplegia after stroke |
| `Stage` | Hyperacute, acute, early subacute, late subacute, chronic |
| `Assessment` | NIHSS, mRS, Barthel |
| `Intervention` | Technical procedure (code from Decisions 3553/3554/3555) |
| `Indication` / `Contraindication` | Indication, contraindication |
| `Goal` | Recovery goal |
| `SourceSection` | Document section (MUC_TAI_LIEU) |

| Edge | Example |
|---|---|
| `HAS_STAGE` | Disease → Stage |
| `RECOMMENDS` | Stage → Intervention |
| `INDICATED_FOR` / `CONTRAINDICATED_FOR` | Intervention → condition |
| `ASSESSED_BY` | Stage → Assessment |
| `SUPPORTED_BY` | any node / edge → SourceSection |

Every node and edge has the properties `detail_level` (`BASIC` = Basic, `DEEP` = Deep), `document_id`, `effective_from`, `status`. Anything without `SUPPORTED_BY` cannot be used in an answer.

---

## 6. Authentication and authorization (Auth / RBAC)

### 6.1 Login

- Log in with email / phone number + password. Passwords are hashed with Argon2.
- Returns an **access token (JWT, 15 minutes)** + a **refresh token (httpOnly cookie, 7 days)**.
- The JWT contains: `sub` (account_id), `roles` (roles held), `active_role` (current workspace), `perm_ver` (permission version).
- Switch workspace: call `POST /api/v1/auth/workspace` → new token + audit log entry (R-14).
- Guest: no token. Quota counted by IP + device (HAN_MUC_KHACH, guest quota). From the 6th question a Captcha is required.

### 6.2 Three layers of permission checks

| Layer | Question | Where |
|---|---|---|
| 1. Role | May the current role do this action? | `require(actor, Permission.X)` at the start of each use case |
| 2. Data scope | Is this person linked to this patient? (assigned doctor / technician, relative allowed by the patient, the patient themself) | Inside the use case, through ports of the `care` / `patients` modules |
| 3. Knowledge level | May this role see Basic only, or Basic + Deep? | Inside the queries of `GraphRetriever` / `PassageRetriever` |

The permission matrix lives in code at `shared/auth/permissions.py`, **in one place only**. Example:

```python
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.RECEPTIONIST: {Permission.PATIENT_CREATE, Permission.FOLLOWUP_SCHEDULE,
                        Permission.ASSIGNMENT_MANAGE},
    Role.DOCTOR:       {Permission.CLINICAL_RECORD_WRITE, Permission.STATUS_WRITE,
                        Permission.PATHWAY_APPROVE, Permission.PROPOSAL_REVIEW,
                        Permission.DISCHARGE_CONFIRM, Permission.KNOWLEDGE_READ_DEEP},
    Role.TECHNICIAN:   {Permission.STATUS_WRITE, Permission.PROPOSAL_SUBMIT,
                        Permission.EXERCISE_MARK, Permission.KNOWLEDGE_READ_DEEP},
    Role.CAREGIVER:    {Permission.EXERCISE_MARK, Permission.CONSENT_SIGN_AS_PROXY},
    Role.CURATOR:      {Permission.DOCUMENT_UPLOAD, Permission.KNOWLEDGE_REVIEW,
                        Permission.VISIBILITY_SET, Permission.KNOWLEDGE_READ_DEEP},
    Role.ADMIN:        {Permission.ACCOUNT_MANAGE, Permission.AUDIT_READ},
    Role.PATIENT:      {Permission.OWN_PATHWAY_READ, Permission.EXERCISE_MARK,
                        Permission.INVITE_CAREGIVER},
}
```

Role names in code ↔ ERD: `RECEPTIONIST`=LE_TAN, `DOCTOR`=BAC_SI, `TECHNICIAN`=KTV, `CAREGIVER`=NGUOI_NHA, `CURATOR`, `ADMIN`, `PATIENT`=BENH_NHAN, `GUEST`=Khách.

### 6.3 Audit log

- `AuditLogPort` writes to the `audit_log` table **in the same transaction** as the data.
- Writing the log fails → rollback → no data is returned (R-12). This also applies to **read queries** on patient data.
- Denied actions are logged too (`DENIED`).
- `audit_log` table: no `UPDATE` / `DELETE`. A database trigger (`forbid_overwrite`, first migration) rejects them for every DB user.

---

## 7. Database

- **Business data** is in PostgreSQL. Table names in English, plural, snake_case (`pathway_versions`). The matching ERD table is written in a comment on the ORM model.
- **No overwriting**: the tables `consents`, `status_records`, `assignments`, `pathway_versions`, `caregiver_permission_versions`, `audit_log` only get new rows. Exception (R-08): `assignments.status` and the status columns of `pathway_versions` (`status`, `decided_by`, `decided_at`, `reject_reason`) may be updated. This is enforced in the database by the trigger `forbid_overwrite` (first migration): `DELETE` is rejected, and `UPDATE` is rejected unless only the allowed columns change. The list lives in `no_overwrite(...)` in each `orm.py` and in the migration.
- Primary keys: UUID v7.
- Times are stored in UTC (`timestamptz`). The frontend shows Vietnam time.
- Key business constraints are also enforced in the DB (partial unique indexes):
  - 1 patient has at most 1 treatment episode that is not `KET_THUC` (closed).
  - 1 treatment episode has exactly 1 `ACTIVE` main doctor.
  - 1 patient has at most 1 `ACTIVE` representative.
  - 1 pathway has at most 1 `PENDING` stage-change proposal.
- Migrations: Alembic, one file per change, never edit a merged migration.

---

## 8. API

- Prefix: `/api/v1/...`. Auto-generated docs at `/docs` (OpenAPI). The frontend generates types from OpenAPI.
- Errors always use one shape:

```json
{ "error": { "code": "REASON_REQUIRED", "message": "Keeping a violation item needs a reason", "details": {} } }
```

- `DomainError` → 422, `PermissionError` → 403, not found → 404, not logged in → 401.
- Never reveal "exists but no access": patient data outside the user's access returns 404.
- AI answers can be streamed (Server-Sent Events) at `POST /api/v1/qa/sessions/{id}/ask:stream`. Citations are sent in the last event.

Main endpoint groups:

| Group | Examples |
|---|---|
| `/auth` | login, refresh, logout, workspace |
| `/accounts` | Admin creates accounts, assigns roles |
| `/patients` | create record, consent, invite codes, relatives, permissions |
| `/episodes` | treatment episodes, assignments (receptionist), clinical records, status |
| `/pathways` | AI draft, approve, reject, technician proposals, exercise sessions |
| `/discharges` | checklist, confirm discharge, follow-up visits |
| `/knowledge` | documents, sections, review, detail levels, graph, test set |
| `/qa` | sessions, ask, history, view the source passage of a citation |
| `/notifications` | list, mark as read |
| `/audit` | Admin reads the log, patient reads their own log |

---

## 9. Configuration

Read from environment variables through `config.py` (pydantic-settings). Sample file: `backend/.env.example` (copy to `backend/.env`). The local passwords in it match `docker-compose.yml`.

| Variable | Example |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...` (Docker) or the Neon connection string as is. `shared/adapters/postgres/engine.py` converts `sslmode` / `channel_binding` for asyncpg and turns the statement cache off for `-pooler` hosts. Run migrations on the direct Neon host. The same `backend/.env` is used in Docker: compose sets `DATABASE_LOCALHOST_ALIAS=postgres`, so a localhost URL reaches the postgres container. |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | |
| `REDIS_URL` | |
| `JWT_SECRET`, `JWT_ACCESS_TTL_MIN` | |
| `OPENROUTER_API_KEY` | |
| `LLM_MODEL` | model name on OpenRouter |
| `EMBEDDING_MODEL` | |
| `JWT_REFRESH_TTL_DAYS` | `7` |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |
| `CENTER_NAME`, `CENTER_DOMAIN` | name and domain of the center |
| `GUEST_FREE_QUESTIONS` | `5` |
| `CORS_ORIGINS` | `["http://localhost:5173"]` |

Never commit secrets. Never write patient information to logs.

---

## 10. Testing and CI

| Type | What it checks | Tools |
|---|---|---|
| Unit | Domain rules, use cases | pytest + **fake adapters** (in-memory classes that implement a port) |
| Integration | PostgreSQL, Neo4j adapters | testcontainers |
| API | HTTP flows, error codes, permissions | httpx AsyncClient |
| Permissions | Each endpoint × each role: allowed / blocked correctly | tests generated from the permission matrix |
| RAG eval | Right source, right citation, **0 leaks of Deep content** to Basic-only users, pathway matches the documents | `tests/rag_eval/`, runs in CI |
| Architecture | Dependency rules between layers | import-linter |

CI order: `ruff` → `mypy` → `lint-imports` → unit → integration → api → rag_eval.

---

## 11. Deployment

- One installation for the center includes: `api`, `worker`, `postgres`, `neo4j`, `redis`, `frontend` (nginx).
- `docker-compose.yml` runs `postgres`, `neo4j`, `redis`, `api` and `frontend`. The `api` container runs `alembic upgrade head` before starting. nginx in `frontend` forwards `/api/` to `api`, so the browser uses one origin. `worker` is added once it has a background job (arq needs at least one).
