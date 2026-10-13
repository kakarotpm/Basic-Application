"""Employee business logic, as plain functions.

The API routes call these, and later the AI agent (Stage 3) can call them too.
They don't know anything about HTTP; they just take a database session and data.
"""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Employee
from app.schemas import EmployeeIn


class DuplicateEmailError(Exception):
    """Raised when another employee already uses this email address."""


def list_employees(db: Session, search: str | None = None, department: str | None = None) -> list[Employee]:
    """All employees, optionally filtered by a search term and/or department."""
    query = select(Employee).order_by(Employee.name)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(Employee.name.ilike(pattern), Employee.email.ilike(pattern), Employee.job_title.ilike(pattern))
        )
    if department:
        query = query.where(Employee.department == department)
    return list(db.scalars(query))


def list_departments(db: Session) -> list[str]:
    """Every department that has at least one employee, alphabetically."""
    return list(db.scalars(select(Employee.department).distinct().order_by(Employee.department)))


def get_employee(db: Session, employee_id: int) -> Employee | None:
    return db.get(Employee, employee_id)


def create_employee(db: Session, data: EmployeeIn) -> Employee:
    _check_email_is_free(db, data.email)
    employee = Employee(**data.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def update_employee(db: Session, employee_id: int, data: EmployeeIn) -> Employee | None:
    employee = db.get(Employee, employee_id)
    if employee is None:
        return None
    _check_email_is_free(db, data.email, ignore_id=employee_id)
    for field, value in data.model_dump().items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee_id: int) -> bool:
    """Returns True if the employee was deleted, False if they didn't exist."""
    employee = db.get(Employee, employee_id)
    if employee is None:
        return False
    db.delete(employee)
    db.commit()
    return True


def _check_email_is_free(db: Session, email: str, ignore_id: int | None = None) -> None:
    """Emails count as the same regardless of upper/lower case."""
    existing = db.scalar(select(Employee).where(func.lower(Employee.email) == email.lower()))
    if existing is not None and existing.id != ignore_id:
        raise DuplicateEmailError(f"An employee with email {email} already exists.")
