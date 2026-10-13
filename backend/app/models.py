"""Database tables. Each class here becomes one table in the database."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    department: Mapped[str] = mapped_column(String(100))
    job_title: Mapped[str] = mapped_column(String(100))
    salary: Mapped[float] = mapped_column(Float)
    join_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="Active")  # "Active" or "Inactive"

    # Deleting an employee also deletes their leave requests.
    leave_requests: Mapped[list["LeaveRequest"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    leave_type: Mapped[str] = mapped_column(String(20))  # "Sick", "Casual" or "Annual"
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    reason: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="Pending")  # "Pending", "Approved" or "Rejected"
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    employee: Mapped[Employee] = relationship(back_populates="leave_requests")

    @property
    def employee_name(self) -> str:
        return self.employee.name

    @property
    def days(self) -> int:
        """Number of calendar days, counting both the start and end date."""
        return (self.end_date - self.start_date).days + 1
