"""Dashboard API endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import DashboardOut
from app.services import dashboard as service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db)):
    """Summary cards and chart data. Inactive employees are excluded, except from the total count."""
    return service.get_dashboard(db)
