from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

class ListItemCreate(BaseModel):
    item_name: str = Field(..., description="Name of the item to add")
    quantity: float = Field(default=1.0, gt=0, description="Quantity must be greater than 0")
    unit: Optional[str] = Field(default=None, description="Optional unit of measure (e.g. bottles, lbs)")

    @field_validator("item_name")
    @classmethod
    def validate_item_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("item_name cannot be empty or whitespace")
        return v.strip()

class ListItemUpdate(BaseModel):
    quantity: Optional[float] = Field(default=None, gt=0, description="Quantity must be greater than 0")
    unit: Optional[str] = Field(default=None, description="Unit of measure")
    is_completed: Optional[bool] = Field(default=None, description="Completion status")

class ListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: Optional[int] = None
    item_name: str
    category: Optional[str] = None
    quantity: float
    unit: Optional[str] = None
    is_completed: bool
    created_at: datetime
    updated_at: datetime
