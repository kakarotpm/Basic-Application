"""The shape of data going in and out of the API, with validation rules.

If a request breaks a rule here (missing name, bad email, negative salary...),
FastAPI rejects it automatically with a clear error message.
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class EmployeeIn(BaseModel):
    """What the client sends when adding or editing an employee."""

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    department: str = Field(min_length=1, max_length=100)
    job_title: str = Field(min_length=1, max_length=100)
    salary: float = Field(gt=0)
    join_date: date
    status: Literal["Active", "Inactive"] = "Active"

    # Trim stray spaces so "  " doesn't count as a valid name.
    model_config = ConfigDict(str_strip_whitespace=True)


class EmployeeOut(EmployeeIn):
    """What the API sends back: the same fields plus the database id."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class LeaveRequestIn(BaseModel):
    """What the client sends when applying for leave."""

    employee_id: int
    leave_type: Literal["Sick", "Casual", "Annual"]
    start_date: date
    end_date: date
    reason: str = Field(min_length=1, max_length=500)

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def end_not_before_start(self):
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date.")
        return self


class LeaveRequestOut(LeaveRequestIn):
    """What the API sends back: the request plus its id, status and some handy extras."""

    id: int
    status: Literal["Pending", "Approved", "Rejected"]
    employee_name: str
    days: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentCount(BaseModel):
    department: str
    employee_count: int


class DepartmentSalary(BaseModel):
    department: str
    average_salary: float


class DashboardOut(BaseModel):
    """Summary numbers and chart data for the dashboard (Active employees only, except total)."""

    total_employees: int
    active_employees: int
    department_count: int
    average_salary: float
    pending_leave_requests: int
    employees_by_department: list[DepartmentCount]
    average_salary_by_department: list[DepartmentSalary]


class PolicyPassage(BaseModel):
    """One passage from an HR policy document, as found by search."""

    text: str
    source: str = Field(description="PDF file name")
    pages: str = Field(description='Page number, or a range like "2-3"')
    score: float = Field(description="How closely it matches the question, from 0 to 1")
