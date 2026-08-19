from typing import Optional, List
from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    category: str
    brand: Optional[str] = None
    price: float
    size: Optional[str] = None
    is_available: bool = True
    season: Optional[str] = None
    substitutes: Optional[List[str]] = []

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True
