from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

class CheckoutItemResponse(BaseModel):
    product_id: Optional[int] = None
    name: str
    brand: Optional[str] = None
    quantity: float
    unit: Optional[str] = None
    unit_price: float
    line_total: float
    is_available: bool = True
    substitutes: List[Dict[str, Any]] = Field(default_factory=list)


class CheckoutPreviewResponse(BaseModel):
    items: List[CheckoutItemResponse]
    subtotal: float
    discount: float = 0.0
    total: float
    item_count: int
    has_unavailable: bool = False


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: Optional[int] = None
    product_name_snapshot: str
    brand_snapshot: Optional[str] = None
    quantity: float
    unit: Optional[str] = None
    unit_price: float
    line_total: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    status: str
    subtotal: float
    discount: float
    total: float
    created_at: datetime
    items: List[OrderItemResponse]
