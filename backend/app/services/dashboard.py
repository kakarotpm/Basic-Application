"""Dashboard numbers, written as plain SQL so they're easy to read and check.

Rule: Inactive employees are left out of every calculation, except the
"total employees" count, which shows everyone.

To try any of these queries yourself, from the backend folder:
    .\\.venv\\Scripts\\python.exe -m app.sql_playground "SELECT ..."
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

TOTAL_EMPLOYEES = """
    SELECT COUNT(*)
    FROM employees
"""

ACTIVE_EMPLOYEES = """
    SELECT COUNT(*)
    FROM employees
    WHERE status = 'Active'
"""

DEPARTMENT_COUNT = """
    SELECT COUNT(DISTINCT department)
    FROM employees
    WHERE status = 'Active'
"""

AVERAGE_SALARY = """
    SELECT ROUND(AVG(salary))
    FROM employees
    WHERE status = 'Active'
"""

PENDING_LEAVE_REQUESTS = """
    SELECT COUNT(*)
    FROM leave_requests
    WHERE status = 'Pending'
"""

EMPLOYEES_BY_DEPARTMENT = """
    SELECT department, COUNT(*) AS employee_count
    FROM employees
    WHERE status = 'Active'
    GROUP BY department
    ORDER BY employee_count DESC, department
"""

AVERAGE_SALARY_BY_DEPARTMENT = """
    SELECT department, ROUND(AVG(salary)) AS average_salary
    FROM employees
    WHERE status = 'Active'
    GROUP BY department
    ORDER BY average_salary DESC
"""


def get_dashboard(db: Session) -> dict:
    """All the numbers the dashboard needs, in one go."""

    def single_number(sql: str) -> float:
        return db.execute(text(sql)).scalar() or 0  # "or 0": AVG of no rows is empty, show 0 instead

    def rows(sql: str) -> list[dict]:
        return [dict(row) for row in db.execute(text(sql)).mappings()]

    return {
        "total_employees": single_number(TOTAL_EMPLOYEES),
        "active_employees": single_number(ACTIVE_EMPLOYEES),
        "department_count": single_number(DEPARTMENT_COUNT),
        "average_salary": single_number(AVERAGE_SALARY),
        "pending_leave_requests": single_number(PENDING_LEAVE_REQUESTS),
        "employees_by_department": rows(EMPLOYEES_BY_DEPARTMENT),
        "average_salary_by_department": rows(AVERAGE_SALARY_BY_DEPARTMENT),
    }
