"""Database connection setup.

Everything about *which* database we use lives in this file. To switch to
PostgreSQL later, set the DATABASE_URL environment variable, e.g.:
    postgresql://user:password@localhost:5432/employees
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./employees.db")

# SQLite needs this extra option to work with FastAPI; other databases don't.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """All database tables (Employee, LeaveRequest, ...) will inherit from this."""


def get_db():
    """Give each API request its own database session, and close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
