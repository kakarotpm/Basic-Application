# Employee Management App

A web app for managing employees and leave requests, built with a **FastAPI** backend and a **React** frontend.

**Stage 1 (done):** employee directory, add/edit employees, dashboard with charts, and leave requests with approval.
**Coming next:** Stage 2, an HR policy chatbot (RAG); Stage 3, an AI agent that can act through this app's API.

## Screens

| Screen | Address | What it does |
|---|---|---|
| Dashboard | `/` | Summary cards, employees by department, average salary by department |
| Employees | `/employees` | Searchable table with a department filter, Edit and Delete |
| Add / Edit Employee | `/employees/new`, `/employees/{id}/edit` | One form with validation for both |
| Leave | `/leave` | Apply for leave, filter requests by status, Approve/Reject |

## Requirements

- **Python 3.11+**: check with `python --version`
- **Node.js LTS (v24)**: check with `node --version`
- Windows with PowerShell (the commands below use PowerShell)

## First-time setup

Run these once, after downloading the project.

**Backend**:

```powershell
cd backend
python -m venv .venv                                # create an isolated Python environment
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app.seed              # load 15 sample employees + 5 leave requests
```

**Frontend**:

```powershell
cd frontend
npm install
```

npm may warn that it skipped an install script for `esbuild`. That warning is harmless.

## Running the app

You need **two terminals open at the same time**.

**Terminal 1: backend** (runs at http://localhost:8000):

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

**Terminal 2: frontend** (runs at http://localhost:5173):

```powershell
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser. Press **Ctrl + C** in a terminal to stop that server.

Both servers reload automatically when code changes.

## Useful extras

**API docs:** http://localhost:8000/docs lists every backend endpoint, and you can try each one with "Try it out".

**Reset the sample data:** stop the backend, delete `backend\employees.db`, then run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.seed
```

**Run your own SQL:** query the database and see the results as a table (nothing is ever saved):

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.sql_playground "SELECT department, COUNT(*) FROM employees GROUP BY department"
```

## Project structure

```
backend/
├── requirements.txt          Python packages
└── app/
    ├── main.py               Starts the API and connects the endpoints
    ├── database.py           Database connection (the only file that knows which database we use)
    ├── models.py             Database tables: Employee, LeaveRequest
    ├── schemas.py            Data shapes and validation rules for the API
    ├── services/             Business logic as plain functions (reused by the future AI agent)
    │   ├── employees.py
    │   ├── leave.py
    │   └── dashboard.py      Dashboard numbers, written as plain SQL
    ├── routers/              API endpoints, thin wrappers around the services
    ├── seed.py               Sample data
    └── sql_playground.py     Run SQL from the terminal

frontend/
├── package.json              JavaScript packages and the "npm run dev" command
└── src/
    ├── App.jsx               Maps web addresses to pages
    ├── api.js                Every call to the backend goes through here
    ├── format.js             Money and date formatting
    ├── components/NavBar.jsx
    └── pages/                One file per screen
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/employees?search=&department=` | List, search and filter employees |
| GET | `/employees/departments` | Departments that have employees |
| GET | `/employees/{id}` | One employee |
| POST | `/employees` | Add an employee |
| PUT | `/employees/{id}` | Update an employee |
| DELETE | `/employees/{id}` | Delete an employee (also deletes their leave requests) |
| GET | `/leave-requests?status=&employee_id=` | List leave requests, newest first |
| GET | `/leave-requests/{id}` | One leave request |
| POST | `/leave-requests` | Apply for leave |
| POST | `/leave-requests/{id}/approve` | Approve a Pending request |
| POST | `/leave-requests/{id}/reject` | Reject a Pending request |
| GET | `/dashboard` | Summary numbers and chart data |
| GET | `/health` | Check that the server and database are running |

## Business rules

- Email addresses must be unique (upper/lower case doesn't matter).
- Inactive employees can't apply for leave.
- Only Pending leave requests can be approved or rejected, and a decision can't be changed.
- Deleting an employee also deletes their leave requests.
- Dashboard figures count Active employees only, except the "Total employees" card.

## Switching to PostgreSQL later

The database is set up in one place, `backend/app/database.py`. To switch:

1. Install the PostgreSQL driver: `.\.venv\Scripts\python.exe -m pip install "psycopg[binary]"`
2. Set the `DATABASE_URL` environment variable before starting the backend:
   ```powershell
   $env:DATABASE_URL = "postgresql+psycopg://user:password@localhost:5432/employees"
   ```
3. Run the seed script, then start the backend as usual.

The dashboard SQL works on both SQLite and PostgreSQL.
