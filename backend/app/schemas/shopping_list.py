from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ListItemBase(BaseModel):
    item_name: str
    product_id: Optional[int] = None
    category: Optional[str] = None
    quantity: float = 1.0
    unit: Optional[str] = None
    is_completed: bool = False

class ListItemCreate(ListItemBase):
    pass

class ListItemUpdate(BaseModel):
    quantity: Optional[float] = None
    unit: Optional[str] = None
    is_completed: Optional[bool] = None

class ListItemResponse(ListItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
