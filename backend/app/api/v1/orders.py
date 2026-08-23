from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.checkout import OrderResponse
from app.services.checkout_service import CheckoutService

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.get("", response_model=List[OrderResponse], status_code=status.HTTP_200_OK)
def get_orders(db: Session = Depends(get_db)) -> List[OrderResponse]:
    """
    Returns order history.
    """
    orders = CheckoutService.get_orders(db)
    return [OrderResponse.model_validate(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def get_order_by_id(order_id: int, db: Session = Depends(get_db)) -> OrderResponse:
    """
    Returns details for a specific order by ID.
    """
    order = CheckoutService.get_order_by_id(db, order_id)
    return OrderResponse.model_validate(order)
