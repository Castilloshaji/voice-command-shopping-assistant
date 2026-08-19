from typing import List
from sqlalchemy.orm import Session
from app.schemas.suggestion import SuggestionResponse

class RecommendationService:
    """
    Interface & engine contract for deterministic recommendation algorithms.
    Computes suggestions based on:
    - Purchase history events & recency
    - Product seasonality
    - Product availability & substitutes
    Full recommendation engine implementation will be added in Phase 5.
    """
    @staticmethod
    def get_suggestions(db: Session, limit: int = 5) -> List[SuggestionResponse]:
        # Interface placeholder signature
        return []
