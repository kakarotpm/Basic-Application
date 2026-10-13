"""Leave request API endpoints. Each one is a thin wrapper around a service function."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import LeaveRequestIn, LeaveRequestOut
from app.services import leave as service

router = APIRouter(prefix="/leave-requests", tags=["Leave"])


@router.get("", response_model=list[LeaveRequestOut])
def list_leave_requests(
    status: Literal["Pending", "Approved", "Rejected"] | None = None,
    employee_id: int | None = None,
    db: Session = Depends(get_db),
):
    """List leave requests, newest first. Optional: filter by `status` and/or `employee_id`."""
    return service.list_leave_requests(db, status=status, employee_id=employee_id)


@router.get("/{leave_id}", response_model=LeaveRequestOut)
def get_leave_request(leave_id: int, db: Session = Depends(get_db)):
    leave = service.get_leave_request(db, leave_id)
    if leave is None:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave


@router.post("", response_model=LeaveRequestOut, status_code=status.HTTP_201_CREATED)
def apply_leave(data: LeaveRequestIn, db: Session = Depends(get_db)):
    """Apply for leave. New requests start as Pending."""
    try:
        return service.apply_leave(db, data)
    except service.LeaveRequestError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/{leave_id}/approve", response_model=LeaveRequestOut)
def approve_leave(leave_id: int, db: Session = Depends(get_db)):
    return _decide(service.approve_leave, leave_id, db)


@router.post("/{leave_id}/reject", response_model=LeaveRequestOut)
def reject_leave(leave_id: int, db: Session = Depends(get_db)):
    return _decide(service.reject_leave, leave_id, db)


def _decide(action, leave_id: int, db: Session):
    try:
        leave = action(db, leave_id)
    except service.LeaveRequestError as error:
        raise HTTPException(status_code=409, detail=str(error))
    if leave is None:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave
