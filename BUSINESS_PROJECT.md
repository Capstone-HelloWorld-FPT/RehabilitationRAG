# BUSINESS_PROJECT – RehabGraph-RAG

This document describes the **business side** of the project: what the system does, who it is for, and which rules it follows.
It does not talk about code. For code, see [BACKEND-ARCHITECTURE.md](BACKEND-ARCHITECTURE.md) and [FRONT-END-ARCHITECTURE.md](FRONT-END-ARCHITECTURE.md).

---

## 1. What the project is

RehabGraph-RAG is an **internal web app for one Rehabilitation center (Phục hồi chức năng, PHCN)**. The system helps the center to:

1. **Look up rehabilitation knowledge** through AI Q&A. The AI answers only from Ministry of Health (MoH, Bộ Y tế / BYT) documents loaded into the system, and **every conclusion has a citation** (document name, page, or technical procedure number).
2. **Suggest a personal recovery pathway** for each patient. The AI writes a draft, and **the doctor approves it**.
3. **Follow each patient** from admission, through diagnosis and the treatment pathway, to discharge and follow-up visits at home.

What makes it different:
- MoH knowledge is stored as a **knowledge graph**. The AI finds answers with **Graph-RAG** (walk the graph + search related text passages).
- **Answers are filtered by role**. The knowledge source is the same, but a patient sees a simple answer, a technician sees technical details, and a doctor sees the full answer.

## 2. Goals

- Build a product that **really runs (production-ready)**. No research paper.
- AI quality is checked with a **test question set** that runs automatically in CI: finds the right source, cites correctly, never leaks content above the user's access, and the pathway matches the documents.

## 3. Scope

### 3.1 MVP (build first)

| Item | Decision |
|---|---|
| LLM | Called through **OpenRouter**. |
| Conditions | The system is designed for 3 conditions. **The MVP only covers rehabilitation for hemiplegia after stroke (tai biến mạch máu não, TBMMN).** |
| Context | The system serves **one rehabilitation center**: one installation, one database, accounts for the center's staff and patients. |
| Platform | Web app (React + Vite). No mobile app in the MVP. |
| Knowledge sources | MoH documents first: Guideline for diagnosis and treatment in rehabilitation (Hướng dẫn chẩn đoán và điều trị PHCN, 2014), Decision 3553/QĐ-BYT, Decision 3554/QĐ-BYT, Decision 3555/QĐ-BYT (rehabilitation technical procedures), Decision 5623/QĐ-BYT (2018) for stroke. Foreign sources only when reputable and approved. |

### 3.2 After the MVP

- Add 2 conditions: rehabilitation after knee replacement, rehabilitation after low back pain surgery.
- Mobile app to remind patients after discharge.
- Connect to HIS (hospital information system) if the center has one.

### 3.3 Out of scope

- No prescribing, no diagnosing in place of the doctor. The AI **only supports**, and every answer shows the note "AI only supports".
- Nobody can edit the **original** MoH knowledge.

---

## 4. Users (actors) and roles

There are **7 roles with an account**, plus Guest (no account). One **account can hold many roles** (e.g., a doctor is also a curator). Each role is a **workspace**. The workspace you are in decides your permissions and how the AI filters its answers.

| Role | Who | Main tasks |
|---|---|---|
| **Guest** (Khách) | Person without an account | Ask general questions, read daily-life tips. Limited number of questions, no saved history. |
| **Patient** (Bệnh nhân, BN) | Person under treatment | Ask questions, see own pathway, see follow-up schedule, mark home exercises, manage consent and relatives. |
| **Relative** (Người nhà) | Family member of the patient | See what the patient allows, mark exercises for the patient. A relative can be the **legal representative** (signs consent for the patient). |
| **Receptionist** (Lễ tân) | Front-desk staff | Create patient records, link the representative, **assign the main doctor / technicians to a treatment episode**, book follow-up visits. **Cannot see medical records.** |
| **Rehabilitation doctor** (Bác sĩ, BS) | Main treating person | Diagnose, enter patient status, **approve pathways**, handle technician proposals, discharge, run follow-up visits. |
| **Technician / Rehab nurse** (Kỹ thuật viên, KTV / Điều dưỡng) | Person who does exercises with the patient | Enter patient status, mark exercise sessions, **propose** a stage change / pathway edit (doctor approves). |
| **Curator** | Knowledge manager | Load MoH documents, review concepts and relations in the graph, set who can see which content, handle questions with no source. |
| **Admin** | System manager of the center | Create accounts, assign roles, read the audit log, see statistics. |

### 4.1 Answer detail level: Basic and Deep

Answers have **2 detail levels**:

| Level | Content |
|---|---|
| **Basic** (Thường) | Simple, easy explanation. Daily-life tips, home safety, things to do. No drugs, no doses, no differential diagnosis. |
| **Deep** (Sâu) | Full professional detail: technique steps, parameters, procedure numbers, differential diagnosis, causes, lab tests, drugs. |

| Role | Allowed levels |
|---|---|
| Guest, patient, relative | **Basic** only |
| Technician / nurse, doctor, curator | **Basic** and **Deep**. Default is Deep, can be changed for each question. |

The Curator tags each **node and passage** of the knowledge as Basic or Deep. For a user who may only see Basic, the system **does not fetch** Deep content during search. Filtering happens **at search time**, not after the AI has answered.

---

## 5. Main business flows

Numbers in brackets are the team's swim lane codes.

### 5.1 Patient flow (from admission to follow-up)

```
Receptionist creates patient record + patient gives consent (60)
   → Receptionist assigns main doctor + technicians (61)
   → Doctor / technician enters patient status, system computes the stage (62)
   → AI creates a draft pathway (63)
   → Doctor approves / edits / rejects the pathway (64)
   → Technician trains the patient, proposes a stage change when needed, doctor approves (65)
   → Doctor discharges the patient, receptionist books follow-up visits (66)
   → Patient exercises at home, relatives help, follow-up visits
```

1. **Record and consent (60).** The receptionist creates the patient record. The patient consents to each purpose separately (store and track data, use the AI chatbot, share with relatives, anonymous research). If the patient cannot consent, the representative signs instead. After consent, the patient gets an account.
2. **Assignment (61).** The receptionist assigns the team. Each treatment episode has **exactly 1 main doctor** and 0 or more technicians.
3. **Status and stage (62).** Enter NIHSS, mRS, Barthel, onset date, stroke type, paralysed side. The system computes the stage (hyperacute, acute, early subacute, late subacute, chronic). Only the doctor can override the stage, and must give a reason.
4. **AI pathway (63).** The AI creates a draft from MoH knowledge. Each pathway item has a citation and an eligibility result: eligible, violation (contraindication), or missing data.
5. **Doctor review (64).** The doctor approves, edits, or rejects. Keeping a "violation" item needs a reason. Items the doctor adds without a citation get the label "Added by doctor".
6. **Technician proposal (65).** Technicians cannot change the pathway or stage themselves. They send a proposal (stage change or pathway edit), and the doctor approves.
7. **Discharge and follow-up (66).** The doctor checks the discharge checklist. Discharging with an unmet item needs a reason. After discharge, the treatment episode moves to "Home follow-up". Assignments stay so the team can follow up.

### 5.2 AI Q&A flow (67)

1. The user asks in Vietnamese.
2. The system checks: is the question **urgent**? **out of scope**?
   - Urgent: show emergency instructions, notify the assigned doctor / technician (if the user is a patient).
   - Out of scope: refuse politely.
3. The system searches the knowledge graph, **only in the part the current role may see**.
4. The AI writes the answer. **Every conclusion must have a citation.** The user clicks a citation to see the source passage.
5. No source found: the AI says "no information yet", and the question is logged for the Curator. **The AI must never make things up.**

Guest: the first 5 questions are normal, from the 6th question a Captcha is required. Questions are counted by IP + device. A guest chat session is deleted when it ends.

### 5.3 Document loading flow (68) and update when a document changes (69)

1. The Curator uploads an MoH document (PDF, DOC, DOCX, may be a scan).
2. The system runs OCR (for scans), splits sections / procedures, and the AI proposes concepts and relations.
3. The Curator approves, edits, or rejects each item, and tags it Basic / Deep.
4. A document is used only when **all test questions pass** and **its effective date has arrived**.
5. A new document replaces an old one: the old one expires. Unchanged sections switch their citation source automatically. For changed sections, related pathways are marked **"Needs review"** for the doctor.

### 5.4 Relative flow

1. The patient creates an **invite code** (single use, expires after 48 hours) and sends it to the relative.
2. The relative uses the code to request a link. The link becomes active only when the patient accepts and chooses permissions (see pathway, see questions, see progress...).
3. When the patient changes permissions, a new permission version is created. The patient can remove the link.
4. The representative is linked by the receptionist when creating the record, with no invite code. Each patient has at most 1 active representative.

---

## 6. Key business rules

These rules are **mandatory**. Code must enforce them, and tests must cover them.

**Citations and sources**
- R-01. Every AI conclusion (answer, pathway item) must cite at least one section of an MoH document that is loaded and currently in effect.
- R-02. No source means no medical answer. Log the question for the Curator.
- R-03. A citation stores a **copy** of the quoted passage, so the exact content at answer time can be checked later.

**Permissions**
- R-04. Answers and source passages are filtered by the role of the current workspace. Deep content is never shown to patients, relatives, or guests.
- R-05. Doctors / technicians only see patients assigned to them.
- R-06. Receptionists cannot see medical records (they can still assign doctors / technicians).
- R-07. Relatives only see what the patient allowed.

**No overwriting data**
- R-08. Consent, patient status, assignments, pathways, relative permissions: **no update, no delete**. Each change is a new row / version.
- R-09. Each patient has at most 1 open treatment episode.
- R-10. Each pathway has at most 1 pending stage-change proposal.

**Audit log**
- R-11. Every action on patient data is logged, even when it is denied.
- R-12. **If the audit log cannot be written, no data is returned.**
- R-13. The audit log is append-only: no update, no delete. Only the patient (for their own data) and the Admin can read it.

**Workspace**
- R-14. After login, the user goes straight to the last-used workspace. Every workspace switch is logged.

---

## 7. Non-functional requirements

| Requirement | Target |
|---|---|
| Security | HTTPS, hashed passwords, permissions by role and assignment, audit log |
| Personal data | Follow Decree 13/2023/NĐ-CP on personal data protection. Consent per purpose. |
| Language | UI and answers in Vietnamese |
| AI quality | Test question set runs in CI: right source, right citation, 0 leaks of Deep content to Basic-only users, pathway matches the documents |
| Deployment | Docker. One installation for the center. |

---

## 8. Open questions

| Code | Question | Who decides |
|---|---|---|
| Q-06 | Product name: "RehabRAG" (Figma) or "RehabGraph-RAG"? Code uses RehabGraph-RAG for now. See DESIGN §14. | Team |
| Q-05 | What are the details of LAN_TAP (exercise session at home)? Waiting for the home-exercise swim lane. | Team |

---

## 9. Glossary

| Term | Meaning |
|---|---|
| PHCN | Rehabilitation (Phục hồi chức năng) |
| TBMMN | Stroke (Tai biến mạch máu não) |
| QTKT | Technical procedure (Quy trình kỹ thuật), in Decisions 3553/3554/3555 |
| BYT | Ministry of Health (Bộ Y tế), MoH |
| NIHSS, mRS, Barthel | Scales to assess stroke and level of independence |
| Knowledge graph | Concepts (nodes) connected by relations (edges) |
| Graph-RAG | The AI searches the knowledge graph first, then writes the answer |
| Curator | Knowledge manager |
| Workspace | Work area for one role |
| Treatment episode (Đợt điều trị) | One hospital stay of a patient |
