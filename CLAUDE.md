# Employee Management App

An Employee Management app built in stages. The user is a product manager learning to build AI apps. They can read a little code.

See [README.md](README.md) for setup commands, project structure and the full API endpoint list.

## Tech stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2, SQLite
  - We will move to PostgreSQL later. The database URL lives only in `backend/app/database.py` (overridable with the `DATABASE_URL` env var). Keep it that way.
- **Frontend:** React 19 with Vite 7, Tailwind CSS v4 (via `@tailwindcss/vite`, no config file), React Router 7, Recharts 3. Plain JavaScript (JSX), not TypeScript.
- **Layout:** `backend/` and `frontend/` folders at the repo root
- **Environment:** Windows, VS Code, PowerShell, Node.js v24 LTS. Give commands in PowerShell syntax.

## Stages

### Stage 1: complete (committed)
Dashboard, Employee Directory, Add/Edit Employee, and Leave, with a nav bar. The seed adds 15 employees across 4 departments (Engineering, Sales, Marketing, HR) and 5 leave requests.

### Stage 2: HR policy chatbot (RAG), in progress
Decisions made with the user:
- **Documents:** the user's **real organization HR policies, as PDFs**, in `backend/policies/`. (Claude's sample Markdown policies were deleted at the user's request.) Treat them as confidential: don't quote them outside what's needed. `backend/policies/*.pdf` is gitignored at the user's request.
  - Files: `Kanerika Employee Handbook.pdf` (22 pages: leave, professional development, anti-sexual-harassment, code of conduct), `IT Policies.pdf` (5 pages, the company address repeats as a header on every page), `India Holiday List-January to December 2026.pdf` (1 page, table). All text-based, no OCR needed.
  - The organization is in India (Telangana holidays). **The whole app uses ₹ INR** (decided by the user): salaries are annual INR, shown as `₹12,00,000` and as `₹12L` on chart axes.
- **Chatbot instructions decided by the user** (put these in the Phase 4 system prompt):
  - **Leave type mapping** from the policy to the app's Leave form: Earned/Privilege Leave (EL/PL) → **Annual**; Sick Leave → **Sick**; everything else (Maternity, Paternity, Bereavement, Comp Off, Leave Without Pay) → **Casual**. When explaining how to apply, name the app type to choose.
  - **Earned Leave builds up at 1.5 days per month** (18 per year). The handbook also says "one day per month" in one place, which is an error. Always use 1.5.
- **Embeddings:** a free local model (no API key). **Vector DB:** Chroma, stored in a local folder, kept behind one small module so it can be swapped for pgvector when we move to PostgreSQL.
- **LLM:** Claude Opus 5.5 (`claude-opus-5-5`) through the official `anthropic` Python SDK. The API key goes in `backend/.env` (gitignored).
- The chatbot answers **only from retrieved policy passages**, cites its sources, and says when a policy doesn't cover a question. It's read-only and never changes app data.

Phases: 1 policy docs, 2 indexing + search playground, 3 `search_policies` service + `GET /policies/search`, 4 `POST /chat` with Claude, 5 HR Assistant screen, 6 test-question set + docs.

### Future stage (design so it fits)
- **Stage 3:** AI agent with tools that call this backend (e.g. apply for leave, search policies). Tools should call the existing functions in `backend/app/services/` or the REST API.

## Code conventions

**Backend** (`backend/app/`):
- `models.py`: SQLAlchemy tables. `schemas.py`: Pydantic input/output shapes with validation (`EmployeeIn`/`EmployeeOut` pattern).
- `services/*.py`: business logic as plain functions taking `(db, ...)`. No HTTP knowledge. They raise simple custom exceptions (e.g. `DuplicateEmailError`, `LeaveRequestError`) and return `None` for "not found".
- `routers/*.py`: thin endpoints that call a service function and turn exceptions into HTTP errors (404 not found, 409 conflict, 400 rule broken, 422 validation).
- Register new routers in `main.py`. Tables are created with `Base.metadata.create_all` at startup. There are no migrations yet, so adding columns to an existing table means deleting `employees.db` and re-seeding (or adding migrations).
- Dashboard numbers are **plain SQL strings** in `services/dashboard.py`, written to work on both SQLite and PostgreSQL.

**Frontend** (`frontend/src/`):
- Every backend call goes through `api.js`, which turns FastAPI error bodies into readable `Error` messages.
- One file per screen in `pages/`. Forms validate in the browser first (mirroring the backend rules) and show backend errors in a red banner.
- Shared formatting is in `format.js` (`formatMoney`, `formatDate`). Styling uses Tailwind classes inline, with indigo as the primary color.

## Business rules (decided with the user)

- Dashboard: **Inactive employees are excluded from all calculations** except the "Total employees" card.
- Inactive employees can't apply for leave, and the Leave form's dropdown shows only Active employees.
- Only Pending leave requests can be approved or rejected, and decisions are final.
- Deleting an employee also deletes their leave requests (ORM cascade).
- Emails are unique, compared case-insensitively.

## Running and testing

- Backend: `cd backend; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload` (port 8000). Frontend: `cd frontend; npm run dev` (port 5173, which must match CORS in `main.py`).
- The user usually has their own servers running on 8000 and 5173. When testing myself, start a separate backend on **port 8001** and stop it afterwards. Clean up any test data I create, so the user's data stays as they left it.
- Check that the frontend compiles with `npm run build`, then delete `frontend/dist`.
- SQL playground: `.\.venv\Scripts\python.exe -m app.sql_playground "SELECT ..."` (read-only).
- The npm "skipped install-scripts for esbuild" warning is harmless.

## How to work with this user

- Build in **small phases**. Stop after each phase so the user can test before moving on.
- Explain changes in **plain language a PM would understand**: what was built and why, not just how.
- Before writing dashboard/reporting SQL, **offer the user the chance to write it themselves first**. They may decline and ask me to write it, as they did in Stage 1.
- After each phase, give the **exact commands to run** (PowerShell) and describe **what they should see in the browser**.
- Don't write app code until the user has approved the plan for the current stage.
- When I make a product decision the user didn't specify (e.g. a business rule), call it out so they can change it.
- Don't commit to Git unless the user asks.
