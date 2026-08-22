from typing import Optional
from pydantic import BaseModel, model_validator

class SuggestionResponse(BaseModel):
    product_id: Optional[int] = None
    item_name: str
    product: Optional[str] = None
    category: Optional[str] = None
    reason: str
    score: float
    is_substitute: bool = False
    substitute_for: Optional[str] = None

    @model_validator(mode="after")
    def populate_product_name(self):
        if not self.product:
            self.product = self.item_name
        return self

