"""Employee API endpoints. Each one is a thin wrapper around a service function."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import EmployeeIn, EmployeeOut
from app.services import employees as service

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=list[EmployeeOut])
def list_employees(search: str | None = None, department: str | None = None, db: Session = Depends(get_db)):
    """List employees. Optional: `search` by name/email/job title, filter by `department`."""
    return service.list_employees(db, search=search, department=department)


# Must come before "/{employee_id}", or FastAPI would treat "departments" as an id.
@router.get("/departments", response_model=list[str])
def list_departments(db: Session = Depends(get_db)):
    """All departments that currently have employees, alphabetically."""
    return service.list_departments(db)


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = service.get_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(data: EmployeeIn, db: Session = Depends(get_db)):
    try:
        return service.create_employee(db, data)
    except service.DuplicateEmailError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, data: EmployeeIn, db: Session = Depends(get_db)):
    try:
        employee = service.update_employee(db, employee_id, data)
    except service.DuplicateEmailError as error:
        raise HTTPException(status_code=409, detail=str(error))
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    if not service.delete_employee(db, employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
