"""The FastAPI application: the entry point for the backend server."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models  # noqa: F401  (registers the tables so create_all can see them)
from app.database import Base, engine, get_db
from app.routers import dashboard, employees, leave, policies

# Create any database tables that don't exist yet.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Management API")

# Allow the React frontend (which runs on port 5173) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(leave.router)
app.include_router(dashboard.router)
app.include_router(policies.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Confirm the server is running and can talk to the database."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
