# FRONT-END-ARCHITECTURE – RehabGraph-RAG

This document describes the frontend architecture: **React + Vite + TypeScript**.
For business rules, see [BUSINESS_PROJECT.md](BUSINESS_PROJECT.md). For the API, see [BACKEND-ARCHITECTURE.md](BACKEND-ARCHITECTURE.md).

Version: v1.1, 25/11/2026. All technologies in the table in section 1 are decided. The team chose the **newest major versions** (25/11/2026).

**Current state:** the project skeleton exists (folders + config, `.gitkeep` in empty folders). **No components or app code yet.** Packages are installed and locked in `frontend/pnpm-lock.yaml`.

Note: the app UI is in Vietnamese. When this document quotes a UI label, the Vietnamese text is in brackets.

---

## 1. Technology

Versions below are the ones in `frontend/package.json` on 25/11/2026.

| Part | Choice | Note |
|---|---|---|
| Framework | React 19.3 + Vite 8 | Decided |
| Language | TypeScript 6.0 (strict) | Not 7.x yet: `typescript-eslint` only supports `<6.1`. |
| Router | React Router 8 (data router: `createBrowserRouter`) | Decided. Import from `react-router` (`RouterProvider` from `react-router/dom`). There is no `react-router-dom` package any more. |
| API calls, cache | TanStack Query 5 | Decided |
| Client state | Zustand 5 (only for the login session, workspace, UI) | Decided |
| Forms | React Hook Form 7 + Zod 4 (`@hookform/resolvers`) | Decided |
| UI | Tailwind CSS v4 (`@tailwindcss/vite`, no `tailwind.config`) + shadcn/ui (Radix) | Decided. `components.json` puts shadcn components in `src/shared/ui`. |
| Icons | lucide-react | See DESIGN §8. |
| Font | `@fontsource/be-vietnam-pro` | Works without the internet (DESIGN §3.1). |
| API types | Generated from the backend OpenAPI with `openapi-typescript` 7 + `openapi-fetch` | Decided |
| Knowledge graph drawing | Cytoscape.js 3 | Decided |
| AI / document content | `react-markdown` + `rehype-sanitize` | See section 8. |
| Dates and times | date-fns 4 + `@date-fns/tz` (Asia/Ho_Chi_Minh) | |
| Languages | i18next + react-i18next (MVP is Vietnamese only, but no hard-coded text in components) | Decided |
| Tests | Vitest 5 + Testing Library, MSW 3 (mock API), Playwright (E2E) + `@axe-core/playwright` | |
| Lint, format | ESLint 10 (`typescript-eslint`, `eslint-plugin-boundaries`) + Prettier 3 (+ Tailwind plugin) | |
| Package manager | pnpm 12 | Decided. If `corepack enable` fails on Windows (no admin rights), use `npm i -g pnpm`. |

Config files: `package.json`, `tsconfig.json` (+ `tsconfig.app.json`, `tsconfig.node.json`), `vite.config.ts` (also holds the Vitest config, alias `@` → `src`), `eslint.config.js`, `.prettierrc.json`, `components.json`, `playwright.config.ts`, `.env.example`.

Not created yet (they are code): `index.html`, `src/main.tsx`, `src/index.css` (tokens in DESIGN §13), `src/test/setup.ts`. When `src/test/setup.ts` is added, add it to `test.setupFiles` in `vite.config.ts`. `pnpm typecheck` fails with "No inputs were found" until the first `.ts` file exists in `src/`.

---

## 2. Main ideas

1. **Split by feature, not by file type.** Everything about "pathways" lives in one folder.
2. **One workspace per role.** Each role has its own area in the app (`/doctor`, `/technician`...). Switching workspace means switching area.
3. **Server state ≠ client state.** Data from the API is kept by TanStack Query. Zustand only keeps the login session and UI state.
4. **The frontend does not decide permissions.** The frontend only hides / shows things to make the app easy to use. The backend does the real blocking.
5. **Citations are always clickable.** Every AI answer and pathway item shows its citations, and a click opens the source passage.

---

## 3. Folder structure

```
frontend/
├── index.html                   # (later)
├── package.json
├── vite.config.ts               # Vite + Vitest config
├── tsconfig.json                # + tsconfig.app.json, tsconfig.node.json
├── eslint.config.js
├── .prettierrc.json
├── components.json              # shadcn/ui
├── playwright.config.ts
├── .env.example
├── docker/                      # Dockerfile + nginx.conf (later)
├── e2e/                         # Playwright tests
├── public/
└── src/
    ├── main.tsx                 # entry point: render <App/>
    ├── app/                     # app shell
    │   ├── App.tsx
    │   ├── providers.tsx        # QueryClientProvider, i18n, theme
    │   ├── router.tsx           # routes per workspace
    │   └── layouts/
    │       ├── PublicLayout.tsx      # guest, login
    │       └── WorkspaceLayout.tsx   # menu by role + workspace switch button
    │
    ├── workspaces/              # one folder per role, only puts together pages from features
    │   ├── guest/
    │   ├── patient/
    │   ├── caregiver/
    │   ├── receptionist/
    │   ├── doctor/
    │   ├── technician/
    │   ├── curator/
    │   └── admin/
    │
    ├── features/                # business features, reused across workspaces
    │   ├── auth/                # login, switch workspace
    │   ├── patients/            # patient record, consent, relatives, invite codes
    │   ├── episodes/            # treatment episodes, assignments (done by the receptionist)
    │   ├── clinical-status/     # clinical record, patient status, stage
    │   ├── pathways/            # pathways, review, technician proposals, exercise sessions
    │   ├── discharge/           # discharge, checklist, follow-up
    │   ├── qa/                  # AI chat, history, citations
    │   ├── evidence/            # view source passages, evidence chain
    │   ├── knowledge-graph/     # explore the graph
    │   ├── knowledge-admin/     # curator: documents, review items, detail levels, tests
    │   ├── notifications/
    │   ├── accounts/            # admin: accounts, roles
    │   └── audit/               # audit log
    │
    ├── shared/                  # knows nothing about the business
    │   ├── api/
    │   │   ├── client.ts        # openapi-fetch + attach token + refresh
    │   │   ├── schema.d.ts      # GENERATED from OpenAPI, do not edit by hand
    │   │   └── errors.ts        # read the error shape { error: { code, message } }
    │   ├── auth/
    │   │   ├── session-store.ts # Zustand: token, roles, activeRole
    │   │   ├── permissions.ts   # role → permissions (a copy, only to hide/show UI)
    │   │   └── Can.tsx          # <Can perm="PATHWAY_APPROVE">...</Can>
    │   ├── ui/                  # Button, Dialog, Table... (shadcn/ui)
    │   ├── components/          # shared components: PageHeader, EmptyState, ErrorBoundary
    │   ├── hooks/
    │   ├── i18n/
    │   │   └── vi.json          # all display text
    │   └── lib/                 # date format, number format
    │
    └── test/
        ├── msw/                 # mock API handlers
        └── setup.ts
```

### 3.1 Inside one feature

Example: `features/pathways/`:

```
features/pathways/
├── api.ts                 # API calls + TanStack Query hooks (usePathway, useApproveVersion)
├── query-keys.ts          # cache keys: ['pathways', patientId]
├── types.ts               # types re-exported from schema.d.ts with readable names
├── components/
│   ├── PathwayTimeline.tsx
│   ├── PathwayItemCard.tsx     # shows the item, eligibility result, citations
│   ├── ApproveDialog.tsx       # requires a reason when keeping a violation item
│   └── ProposalForm.tsx        # technician sends a proposal
├── pages/
│   ├── PatientPathwayPage.tsx
│   └── ReviewPathwayPage.tsx
├── schemas.ts             # Zod schemas for forms
└── index.ts               # only exports what other features / workspaces may use
```

**Import rules:**

| From | May import | Must not import |
|---|---|---|
| `shared/*` | external libraries | `features`, `workspaces`, `app` |
| `features/X` | `shared`, `features/Y` **through `index.ts`** | files inside `features/Y/components/...` |
| `workspaces/*` | `features`, `shared` | other workspaces |
| `app/*` | everything | |

Checked automatically in `eslint.config.js`:
- `boundaries/element-types`: the table above (`app`, `workspace`, `feature`, `shared`, `test`).
- `no-restricted-imports`: blocks `@/features/X/...` deep imports. Inside one feature, use relative imports (`./components/...`).
- `no-restricted-globals` / `no-restricted-properties`: blocks `localStorage` / `sessionStorage`.
- `no-restricted-syntax`: blocks `dangerouslySetInnerHTML`.

---

## 4. Routes and workspaces

```
/                         Guest home: Q&A at Basic level, daily-life tips
/login
/invite/:code             Relative uses an invite code
/w                        → go to the last-used workspace

/w/patient/...            My pathway, home exercises, follow-up schedule, Q&A, relatives, consent
/w/caregiver/...          Linked patients → view by permission, mark exercises
/w/receptionist/...       Create patient record, consent, representative, assign doctor / technicians, follow-up schedule
/w/technician/...         My patients, status, exercise sessions, proposals, Q&A (Basic / Deep), graph
/w/doctor/...             My patients, clinical record, review pathways, pending proposals, discharge, Q&A (Basic / Deep)
/w/curator/...            Documents, review items, OCR, detail levels, test set, questions with no source
/w/admin/...              Accounts, roles, audit log, statistics
```

- Each `/w/:role` route has a **guard**: the role must be in the session's `roles`. If not, go back to `/w`.
- Switching workspace: call `POST /api/v1/auth/workspace`, get a new token, **clear the whole TanStack Query cache** (so no data from the old workspace leaks), then change route.
- Each workspace is lazy-loaded (`React.lazy`) so patients do not download the Curator's code.

```tsx
// app/router.tsx (short version). React Router 8: import from "react-router".
import { createBrowserRouter } from "react-router";
// main.tsx: import { RouterProvider } from "react-router/dom";

const router = createBrowserRouter([
  { path: "/", element: <PublicLayout />, children: guestRoutes },
  { path: "/login", element: <LoginPage /> },
  {
    path: "/w",
    element: <RequireAuth><WorkspaceLayout /></RequireAuth>,
    children: [
      { index: true, element: <RedirectToLastWorkspace /> },
      { path: "doctor/*", element: <RequireRole role="DOCTOR"><DoctorWorkspace /></RequireRole> },
      { path: "technician/*", element: <RequireRole role="TECHNICIAN"><TechnicianWorkspace /></RequireRole> },
      // ... other roles
    ],
  },
]);
```

---

## 5. Calling the API

- `shared/api/schema.d.ts` is generated from OpenAPI: `pnpm gen:api`. **Do not edit by hand.** When the backend API changes, run the command again.
- The access token is kept **in memory** (Zustand, not in localStorage). The refresh token is an httpOnly cookie set by the backend.
- On 401: call refresh once, then retry. If refresh fails, go to `/login`.
- On 403 / 404 for patient data: show "Not found or you do not have access" ("Không tìm thấy hoặc bạn không có quyền"). Do not guess more.
- Business errors (422): use `error.code` to show the Vietnamese message from `vi.json`, e.g. `errors.REASON_REQUIRED`.

```ts
// features/pathways/api.ts
export function useApproveVersion(pathwayId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (versionId: string) =>
      api.POST("/api/v1/pathways/{pathway_id}/versions/{version_id}/approve", {
        params: { path: { pathway_id: pathwayId, version_id: versionId } },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: pathwayKeys.detail(pathwayId) }),
  });
}
```

---

## 6. Key screens

### 6.1 AI chat (`features/qa`)

- The answer appears step by step (SSE stream).
- Each point has a citation number `[1]`, `[2]`. A click opens the **source panel** (`features/evidence`): document name, decision number, page or procedure number, quoted passage.
- Always show the line **"AI only supports, it does not replace the doctor."** ("AI chỉ hỗ trợ, không thay thế bác sĩ.")
- Urgent question: show a red box with instructions to call 115 at the top, before anything else.
- No source: show "No information yet in the loaded MoH documents" ("Chưa có thông tin trong tài liệu Bộ Y tế đã nạp"). Never show an empty answer.
- Guest: show how many questions are left; from the 6th question show a Captcha.
- A **Basic / Deep** detail level switch next to the question box. Only shown to technicians, doctors, curators (default Deep). Guests, patients, and relatives do not see this switch; they always get Basic.
- Each answer has a small label "Level: Basic" or "Level: Deep" ("Mức: Thường" / "Mức: Sâu").

### 6.2 Pathway (`features/pathways`)

- Each item is a card: intervention name, procedure code, frequency, eligibility result (green = eligible, red = violation, yellow = missing data), citations.
- Items the doctor added without a citation: label **"Added by doctor"** ("Bác sĩ thêm").
- Doctor approval: if red items remain, the form requires a reason (Zod validation) before sending.
- Pathway "Needs review" (because a document changed): yellow banner at the top, showing which items changed.
- Compare versions: 2 columns, marking what was added / removed / changed.

### 6.3 Knowledge graph (`features/knowledge-graph`)

- Cytoscape.js. Only load the part of the graph around the current node (1–2 steps), never the whole graph.
- Click a node / edge: show the source passage (`SUPPORTED_BY`).
- Content is already filtered by role in the backend. The frontend does no filtering of its own.

### 6.4 Curator (`features/knowledge-admin`)

- Document list with status: processing, waiting for effective date, in use, expired.
- Item review screen: original on the left (PDF viewer), AI-proposed nodes / edges on the right. Approve / edit / reject each one, tag Basic / Deep.
- OCR screen: show the original passage + fix suggestion, choose accept / edit / drop.
- Test set results: pass / fail for each question.

---

## 7. UI and accessibility

- **Simple words, short sentences.** Users include older patients and their relatives. One team member also finds long text hard to read.
- Minimum font size 16px. Minimum touch target 44×44px on mobile.
- Color is never the only way to show status: always add text or an icon (green "Eligible", red "Violation").
- Meet WCAG 2.1 AA: contrast, keyboard use, labels for screen readers.
- Responsive: patients and relatives mostly use phones. Doctor / Curator screens are desktop-first.
- Dates and times in Vietnam time, format `dd/MM/yyyy HH:mm`.

---

## 8. Frontend security

- Never store tokens or patient information in `localStorage` / `sessionStorage`.
- Never log patient information to the console.
- On workspace switch or logout: `queryClient.clear()`.
- All AI and document content is shown as text or sanitized Markdown (rehype-sanitize). Never use `dangerouslySetInnerHTML`.
- `<Can>` and route guards only hide / show. They are not security.

---

## 9. Environment variables

| Variable | Example |
|---|---|
| `VITE_API_BASE_URL` | `https://api.trungtam-phcn.vn` (local: `http://localhost:8000`) |
| `VITE_CENTER_NAME` | `Trung tâm PHCN A` |
| `VITE_CAPTCHA_SITE_KEY` | |

Sample file: `frontend/.env.example`. Only variables starting with `VITE_` go into the bundle. **Never put secrets in the frontend.**

---

## 10. Testing

| Type | What it checks | Tools |
|---|---|---|
| Unit / component | Components render correctly, forms validate correctly | Vitest + Testing Library + MSW |
| UI permissions | Each workspace only sees its own menu and buttons | Vitest, run for each role |
| E2E | Main flows: Q&A with citations, doctor approves pathway, technician sends proposal, discharge | Playwright, against the real backend in Docker Compose |
| Accessibility | Basic a11y errors | `@axe-core/playwright` |

---

## 11. Build and deploy

- `pnpm build` → `dist/` folder (static files).
- Served by nginx in Docker. Any route that is not a file returns `index.html`.
