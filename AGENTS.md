# AGENTS.md – Guide for AI coding agents

This file is for **AI coding agents** (Claude Code, Codex, Cursor, Copilot...) and for new team members.
**Project language: English** for everything that goes into the repo (code, comments, docs, commits, PRs). Only UI text is Vietnamese. Chat with the team can be in any language. See section 5.0.
Read all of it before writing code. If this file disagrees with another document, **this file wins** on how to work; [BUSINESS_PROJECT.md](BUSINESS_PROJECT.md) wins on business rules.

Version: v1.1, 25/11/2026. The **project skeleton exists**: folders (`backend/`, `frontend/`, `knowledge/`), config files, and installed packages. **There is no application code yet**; empty folders hold a `.gitkeep`. Delete the `.gitkeep` when you add the first real file to a folder.

Decisions on 25/11/2026: there is **no Head of department role** any more (7 account roles + Guest); the **receptionist assigns** the doctor / technicians. Frontend uses the newest major versions (React 19, React Router 8). Python stays 3.12. The working language is English (section 5.0).

---

## 1. The project in 5 lines

- **RehabGraph-RAG**: internal web app for one Rehabilitation center (Phục hồi chức năng, PHCN).
- AI Q&A based on Ministry of Health (MoH) documents (Decisions 3553/3554/3555/QĐ-BYT, Decision 5623/QĐ-BYT (2018) for stroke, Guideline for diagnosis and treatment in rehabilitation 2014), using **Graph-RAG**.
- Suggests a **recovery pathway** for each patient, **the doctor approves**.
- Answers are **filtered by role** (7 account roles: patient, relative, receptionist, doctor, technician, curator, admin; plus guest). **Every conclusion must cite an MoH document.**
- The MVP only covers **stroke (TBMMN)**. We build a real product, not a research paper.

## 2. What to read first

| File | When to read |
|---|---|
| [BUSINESS_PROJECT.md](BUSINESS_PROJECT.md) | Always read section 4 (roles) and section 6 (rules R-01 … R-14) |
| [BACKEND-ARCHITECTURE.md](BACKEND-ARCHITECTURE.md) | When changing `backend/` |
| [FRONT-END-ARCHITECTURE.md](FRONT-END-ARCHITECTURE.md) | When changing `frontend/` |
| [DESIGN.md](DESIGN.md) | When building UI |
| ERD (provided by the team) | When adding / changing tables or entities |

## 3. Common commands

Tools: `uv`, Node 24, `pnpm` (if `corepack enable` fails on Windows without admin rights: `npm i -g pnpm`), Docker.
Commands marked *(after code)* only work once the matching code exists (e.g. `main.py`, `alembic.ini`, `src/*.ts`).

```bash
# Run everything locally (from the repo root)
docker compose up -d --build               # whole project: frontend :8080, api :8000, postgres, neo4j, redis
docker compose up -d postgres neo4j redis  # only the infrastructure (when running api / frontend by hand)
cp backend/.env.example backend/.env       # then fill in secrets
cp frontend/.env.example frontend/.env

# Backend
cd backend
uv sync                                    # install packages (works now)
uv run alembic upgrade head                # run migrations (after code)
uv run fastapi dev src/rehabgraph/main.py  # run the API on :8000, docs at /docs (after code)
uv run arq rehabgraph.worker.WorkerSettings  # run background jobs (after code)
uv run ruff check . && uv run ruff format --check .
uv run mypy src                            # (after code)
uv run lint-imports                        # check hexagonal rules (after code: needs __init__.py)
uv run pytest tests/unit                   # fast, run often
uv run pytest tests/integration tests/api  # needs docker
uv run pytest tests/rag_eval               # AI quality, slow

# Frontend
cd frontend
pnpm install
pnpm gen:api                               # generate types from OpenAPI (backend must be running)
pnpm dev                                   # :5173 (after code: index.html, src/main.tsx)
pnpm lint && pnpm typecheck                # typecheck needs at least one .ts file in src/
pnpm format:check                          # Prettier
pnpm test                                  # Vitest
pnpm e2e                                   # Playwright (first time: pnpm exec playwright install)
```

Where the config lives: backend → `backend/pyproject.toml` (ruff, mypy, pytest, import-linter); frontend → `vite.config.ts` (Vite + Vitest), `eslint.config.js` (import boundaries, bans on `localStorage` and `dangerouslySetInnerHTML`), `.prettierrc.json`, `components.json` (shadcn/ui).

**Before saying a task is done**: run lint + typecheck + unit tests for the part you changed. If you changed the API, run `pnpm gen:api` and commit `schema.d.ts`.

---

## 4. Mandatory rules

### 4.1 Medical content and citations (most important)

1. **Never make up medical content.** Do not write indications, contraindications, doses, parameters, time limits, or scales yourself. All of that must come from loaded MoH documents.
2. **Every AI conclusion must have a citation** to a document section that is in effect (R-01). No source → return "no information yet" and log it for the Curator (R-02). Never loosen `CitationValidator` to make tests pass.
3. When writing **seed data, prompts, test cases, fixtures** with medical content: write the source right next to it, like `# Source: QĐ 3553/QĐ-BYT, procedure no. 49` or `# Source: Rehabilitation diagnosis and treatment guideline 2014, p. 291`. If you do not know the source, **stop and ask**, do not guess.
4. Never edit the **original** MoH documents in `knowledge/`.
5. AI answers shown to users always include "AI only supports".
6. LLM prompts live in separate files (`backend/src/rehabgraph/modules/qa/adapters/outbound/llm/prompts/`), with versions, not spread around the code.

### 4.2 Permissions and patient data

7. **Filter the detail level (Basic / Deep) inside the graph / vector query.** Do not fetch everything and filter later. The LLM must never see content above the user's access (R-04).
8. Every use case that reads / writes patient data must check **3 layers**: role → scope (assignment / relative permission / own data) → knowledge level. See BACKEND section 6.
9. The permission matrix is only changed in `shared/auth/permissions.py` (backend). The frontend has a copy to hide / show UI: **change both** and update the permission tests.
10. **Audit log**: write it in the same transaction. If writing fails, return no data (R-12). Log denied actions too.
11. **No update, no delete** on these tables: consent, patient status, assignments, pathway versions, relative permission versions, audit log. A change = a new row (R-08). Only exception: the status columns of `assignments` (`status`) and `pathway_versions` (`status`, `decided_by`, `decided_at`, `reject_reason`) may be updated.
12. The LLM is called through **OpenRouter**. **Never send patient identity data** (name, phone, ID card number, date of birth) in a prompt. Only send the question and the clinical data that is needed.
13. **Never write patient information to logs** (name, phone, ID card number, diagnosis, question text). Logs only contain IDs.
14. Never put real patient data in tests, seeds, fixtures, or screenshots. Use fake data.
15. Patient data outside the user's access → return **404**, not 403 (so we do not reveal that it exists).

### 4.3 Backend architecture (Hexagonal)

16. `domain/` uses **only** the Python standard library. Do not import FastAPI, SQLAlchemy, Pydantic, Neo4j, or an LLM SDK.
17. `application/` only calls `domain/` and `ports/`. Do not import `adapters/`.
18. A FastAPI router only: reads the request → calls the use case → returns the response. **No business logic in routers.**
19. A module does not import the `domain` / `adapters` of another module. Need data: declare a port. Need to react: use a domain event.
20. New technology (DB, LLM, OCR...) = a new **adapter** for an existing port. Do not change the use case.
21. One use case per file in `application/commands/` or `application/queries/`.
22. Test use cases with in-memory **fake adapters**, do not mock function by function.

### 4.4 Frontend

23. Split by feature. Other features import only through `index.ts`.
24. Data from the API → TanStack Query. Zustand only for the login session and UI.
25. `shared/api/schema.d.ts` is generated. **Do not edit by hand.**
26. All display text lives in `shared/i18n/vi.json`. No hard-coded Vietnamese text in components.
27. Never use `dangerouslySetInnerHTML`. AI content is shown as sanitized Markdown.
28. Never store tokens or patient data in `localStorage` / `sessionStorage`.
29. Workspace switch / logout → `queryClient.clear()`.

---

## 5. Language and naming conventions

### 5.0 Working language: English

All work in this repo is done **in English**:

- Code, identifiers, **comments**, docstrings, log messages, developer-facing error messages (the `message` field of API errors), test names.
- Docs (`*.md`), commit messages, branch names, PR titles and descriptions, TODO notes.

AI coding agents may **chat** with the team in any language. This rule is about what goes into the project.

The only Vietnamese allowed:

- **UI text** shown to users: only in `frontend/src/shared/i18n/vi.json` (the app UI and AI answers are in Vietnamese, BUSINESS §7).
- Official names and quotes that must stay exact: MoH document names (`QĐ 3553/QĐ-BYT`), ERD names in `# ERD: DOT_DIEU_TRI` comments, Vietnamese glosses in docs (e.g. "Receptionist (Lễ tân)"), quoted source passages, and test data that checks Vietnamese input.
- Config **values** that are display text, like `CENTER_NAME=Trung tâm PHCN`.

When you touch a file that still has Vietnamese comments, translate them to English.

### 5.1 Code style

- **Code is written in English.** User-facing messages are in Vietnamese and live in `vi.json` (see 5.0).
- **UI text: short sentences, simple words.**
- Python: `snake_case` for functions / variables, `PascalCase` for classes. DB tables: English, plural, `snake_case`.
- TypeScript: `camelCase` for functions / variables, `PascalCase` for components and types. Component files: `PascalCase.tsx`. Folders: `kebab-case`.
- Error codes: `UPPER_SNAKE_CASE`, shared by the backend and `vi.json` (`errors.REASON_REQUIRED`).

### 5.2 Naming from the ERD

The team's ERD is the only source for entity, attribute, and status names. The team will provide the ERD separately.

- The ERD is written in Vietnamese (e.g., `BENH_NHAN`, `DOT_DIEU_TRI`). In code, use the **matching English name**, short and clear.
- Classes / entities: `PascalCase`, singular. DB tables: `snake_case`, plural.
- Status values (enums): keep the exact meaning from the ERD, written in English `UPPER_SNAKE_CASE`.
- Each Vietnamese name has **exactly one** English name, used the same way in backend, frontend, and DB.
- When you name an ERD entity in code, write the original ERD name in a comment on the model (e.g., `# ERD: DOT_DIEU_TRI`).
- An entity or attribute that is not in the ERD: **stop and ask**, do not add it yourself.

---

## 6. Required tests when adding a feature

| What you add | Required tests |
|---|---|
| A business rule in the domain | Unit tests for the allowed case and the blocked case |
| A new use case | Unit tests with fake adapters, including the **no permission** case |
| A new endpoint | API test + add it to the permission matrix test (each role allowed / blocked) |
| Changes to Graph-RAG, prompts, retrievers | Run `tests/rag_eval`. The correct-citation rate **must not drop**. **Leaks of Deep content to Basic-only users must be 0.** |
| Table changes | Alembic migration + integration test |
| A component with a form | Validation tests (especially: reason is required) |

Never delete or skip tests to make CI green.

---

## 7. Git

- Branches: `feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>`, `chore/<short-name>`.
- Commits follow Conventional Commits: `feat(pathways): require a reason when keeping a violation item`.
- One PR, one task. The PR describes: what, why, what was tested, whether permissions / medical content changed.
- Never commit `.env`, secrets, or real patient files.
- Never edit a merged migration. Add a new migration instead.

---

## 8. When to stop and ask a human

Stop and ask (do not decide yourself) when:

- You need medical content and cannot find an MoH source.
- The work would **change the permission matrix**, the Basic / Deep levels, or who can see patient data.
- The work needs to **update / delete data** in an append-only table.
- You need to send patient data to a new external service (other than the approved OpenRouter), e.g. email, SMS.
- The request is outside the MVP (conditions other than stroke, mobile, HIS).
- You find that documents (BUSINESS, architecture, ERD, DESIGN) contradict each other.

## 9. Still open

See BUSINESS_PROJECT section 8. Frontend and backend technologies are all decided; only the embedding model is not chosen yet. When the team changes a decision, update the documents first, then change the code.
