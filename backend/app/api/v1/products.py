from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.product import ProductResponse
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("", response_model=List[ProductResponse], status_code=status.HTTP_200_OK)
def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    availability: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> List[ProductResponse]:
    """
    Read-only endpoint to search catalog products with filters and substitute attachments.
    """
    products = ProductService.search_products(
        db,
        query=query,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        availability=availability
    )

    results = []
    for p in products:
        prod_resp = ProductResponse.model_validate(p)
        if not p.is_available:
            sub_objs = ProductService.get_substitutes_for_product(db, p)
            if sub_objs:
                prod_resp.substitute_products = [ProductResponse.model_validate(sub) for sub in sub_objs]
        results.append(prod_resp)

    return results
