"""Load 15 sample employees and a few sample leave requests into the database.

Run from the backend folder:
    .\\.venv\\Scripts\\python.exe -m app.seed
"""

from datetime import date

from sqlalchemy import func, select

from app.database import Base, SessionLocal, engine
from app.models import Employee, LeaveRequest

SAMPLE_EMPLOYEES = [
    # Engineering (5)
    ("Priya Sharma", "priya.sharma@company.com", "Engineering", "Engineering Manager", 145000, date(2019, 3, 11), "Active"),
    ("Marcus Johnson", "marcus.johnson@company.com", "Engineering", "Senior Software Engineer", 128000, date(2020, 7, 1), "Active"),
    ("Elena Rossi", "elena.rossi@company.com", "Engineering", "Software Engineer", 102000, date(2022, 1, 17), "Active"),
    ("Kenji Tanaka", "kenji.tanaka@company.com", "Engineering", "DevOps Engineer", 115000, date(2021, 5, 24), "Active"),
    ("Aisha Bello", "aisha.bello@company.com", "Engineering", "QA Engineer", 88000, date(2023, 9, 4), "Inactive"),
    # Sales (4)
    ("David Kim", "david.kim@company.com", "Sales", "Sales Director", 132000, date(2018, 11, 5), "Active"),
    ("Sofia Martinez", "sofia.martinez@company.com", "Sales", "Account Executive", 85000, date(2021, 2, 15), "Active"),
    ("James O'Connor", "james.oconnor@company.com", "Sales", "Account Executive", 82000, date(2022, 6, 20), "Active"),
    ("Fatima Khan", "fatima.khan@company.com", "Sales", "Sales Development Rep", 62000, date(2024, 1, 8), "Active"),
    # Marketing (3)
    ("Olivia Brown", "olivia.brown@company.com", "Marketing", "Marketing Manager", 110000, date(2020, 4, 13), "Active"),
    ("Lucas Silva", "lucas.silva@company.com", "Marketing", "Content Strategist", 74000, date(2022, 10, 3), "Active"),
    ("Hannah Weber", "hannah.weber@company.com", "Marketing", "Digital Marketing Specialist", 70000, date(2023, 3, 27), "Inactive"),
    # HR (3)
    ("Grace Okafor", "grace.okafor@company.com", "HR", "HR Manager", 98000, date(2019, 8, 19), "Active"),
    ("Ravi Patel", "ravi.patel@company.com", "HR", "Recruiter", 68000, date(2021, 11, 29), "Active"),
    ("Emily Chen", "emily.chen@company.com", "HR", "HR Generalist", 64000, date(2024, 5, 6), "Active"),
]


# (employee email, leave type, start, end, reason, status)
SAMPLE_LEAVE_REQUESTS = [
    ("marcus.johnson@company.com", "Annual", date(2026, 11, 2), date(2026, 11, 6), "Family vacation", "Approved"),
    ("sofia.martinez@company.com", "Sick", date(2026, 10, 5), date(2026, 10, 6), "Flu", "Approved"),
    ("lucas.silva@company.com", "Casual", date(2026, 10, 20), date(2026, 10, 20), "Moving to a new apartment", "Pending"),
    ("ravi.patel@company.com", "Annual", date(2026, 12, 21), date(2026, 12, 31), "Year-end holidays", "Pending"),
    ("kenji.tanaka@company.com", "Casual", date(2026, 10, 16), date(2026, 10, 17), "Personal errands", "Rejected"),
]


def seed() -> None:
    """Each part only runs if its table is empty, so it's safe to run twice."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(Employee)) > 0:
            print("Employees already exist. Skipping employees.")
        else:
            for name, email, department, job_title, salary, join_date, status in SAMPLE_EMPLOYEES:
                db.add(Employee(name=name, email=email, department=department, job_title=job_title,
                                salary=salary, join_date=join_date, status=status))
            db.commit()
            print(f"Added {len(SAMPLE_EMPLOYEES)} sample employees.")

        if db.scalar(select(func.count()).select_from(LeaveRequest)) > 0:
            print("Leave requests already exist. Skipping leave requests.")
        else:
            added = 0
            for email, leave_type, start, end, reason, status in SAMPLE_LEAVE_REQUESTS:
                employee = db.scalar(select(Employee).where(Employee.email == email))
                if employee is None:  # sample employee was deleted; skip their request
                    continue
                db.add(LeaveRequest(employee_id=employee.id, leave_type=leave_type, start_date=start,
                                    end_date=end, reason=reason, status=status))
                added += 1
            db.commit()
            print(f"Added {added} sample leave requests.")


if __name__ == "__main__":
    seed()
