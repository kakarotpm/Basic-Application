"""Leave request business logic, as plain functions.

Like services/employees.py, these are shared by the API routes and (in Stage 3)
the AI agent's tools.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Employee, LeaveRequest
from app.schemas import LeaveRequestIn


class LeaveRequestError(Exception):
    """Raised when a leave action breaks a business rule. The message explains why."""


def apply_leave(db: Session, data: LeaveRequestIn) -> LeaveRequest:
    employee = db.get(Employee, data.employee_id)
    if employee is None:
        raise LeaveRequestError(f"No employee with id {data.employee_id}.")
    if employee.status != "Active":
        raise LeaveRequestError(f"{employee.name} is Inactive and cannot apply for leave.")

    leave = LeaveRequest(**data.model_dump(), status="Pending")
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


def list_leave_requests(db: Session, status: str | None = None, employee_id: int | None = None) -> list[LeaveRequest]:
    """All leave requests, newest first, optionally filtered by status and/or employee."""
    query = (
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.employee))  # load employee names in one go
        .order_by(LeaveRequest.created_at.desc(), LeaveRequest.id.desc())
    )
    if status:
        query = query.where(LeaveRequest.status == status)
    if employee_id:
        query = query.where(LeaveRequest.employee_id == employee_id)
    return list(db.scalars(query))


def get_leave_request(db: Session, leave_id: int) -> LeaveRequest | None:
    return db.get(LeaveRequest, leave_id)


def approve_leave(db: Session, leave_id: int) -> LeaveRequest | None:
    return _decide(db, leave_id, "Approved")


def reject_leave(db: Session, leave_id: int) -> LeaveRequest | None:
    return _decide(db, leave_id, "Rejected")


def _decide(db: Session, leave_id: int, new_status: str) -> LeaveRequest | None:
    """Approve or reject a request. Only Pending requests can be decided."""
    leave = db.get(LeaveRequest, leave_id)
    if leave is None:
        return None
    if leave.status != "Pending":
        raise LeaveRequestError(f"This request is already {leave.status}.")
    leave.status = new_status
    db.commit()
    db.refresh(leave)
    return leave
