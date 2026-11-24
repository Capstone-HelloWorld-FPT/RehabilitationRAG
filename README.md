# RehabGraph-RAG

Internal web app for one Rehabilitation center: AI Q&A based on Ministry of Health documents (Graph-RAG, with citations) and recovery pathway suggestions for each patient (approved by the doctor). MVP: stroke.

Status: **project skeleton only** (folders + config files). No code yet.

| Folder | Content |
|---|---|
| `backend/` | FastAPI + Hexagonal, Python 3.12, uv |
| `frontend/` | React 19 + Vite + TypeScript, pnpm |
| `knowledge/` | Original Ministry of Health documents (never edit) |
| `docker-compose.yml` | PostgreSQL + pgvector, Neo4j, Redis for local runs |

Read before working: [AGENTS.md](AGENTS.md) → [BUSINESS_PROJECT.md](BUSINESS_PROJECT.md) → [BACKEND-ARCHITECTURE.md](BACKEND-ARCHITECTURE.md) / [FRONT-END-ARCHITECTURE.md](FRONT-END-ARCHITECTURE.md) → [DESIGN.md](DESIGN.md).

Working language: **English** for code, comments, docs, commits and PRs. Only the app's UI text is Vietnamese (in `frontend/src/shared/i18n/vi.json`). See AGENTS.md section 5.
