"""HR policy search API endpoint."""

from fastapi import APIRouter, HTTPException, Query

from app.schemas import PolicyPassage
from app.services import policies as service

router = APIRouter(prefix="/policies", tags=["HR Policies"])


@router.get("/search", response_model=list[PolicyPassage])
def search_policies(
    q: str = Query(min_length=2, max_length=500, description="The question or topic to search for"),
    top_k: int = Query(5, ge=1, le=10, description="How many passages to return"),
):
    """Find the HR policy passages closest in meaning to `q`, best match first."""
    try:
        return service.search_policies(q, top_k)
    except service.PolicyIndexMissingError as error:
        raise HTTPException(status_code=503, detail=str(error))
