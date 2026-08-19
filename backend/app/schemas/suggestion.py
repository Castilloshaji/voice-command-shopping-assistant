from typing import Optional
from pydantic import BaseModel

class SuggestionResponse(BaseModel):
    product_id: Optional[int] = None
    item_name: str
    category: Optional[str] = None
    reason: str  # e.g., 'Frequently Bought', 'Seasonal (Summer)', 'Substitute'
    score: float
