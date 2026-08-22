from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.suggestion import SuggestionResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(
    prefix="/suggestions",
    tags=["suggestions"]
)

@router.get("", response_model=List[SuggestionResponse], status_code=status.HTTP_200_OK)
def get_suggestions(
    limit: int = 5,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
) -> List[SuggestionResponse]:
    """
    Read-only endpoint to retrieve shopping recommendations.
    """
    return RecommendationService.get_suggestions(db, limit=limit, month=month)
