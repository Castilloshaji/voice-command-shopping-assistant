from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.checkout import CheckoutPreviewResponse, OrderResponse
from app.services.checkout_service import CheckoutService

router = APIRouter(
    prefix="/checkout",
    tags=["checkout"]
)

@router.get("/preview", response_model=CheckoutPreviewResponse, status_code=status.HTTP_200_OK)
def get_checkout_preview(db: Session = Depends(get_db)) -> CheckoutPreviewResponse:
    """
    Returns a non-mutating preview of active cart checkout totals, items, prices, and availability.
    """
    return CheckoutService.preview_checkout(db)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def place_order(db: Session = Depends(get_db)) -> OrderResponse:
    """
    Executes atomic checkout transaction. Converts active list items into an Order record.
    """
    order = CheckoutService.place_order(db)
    return OrderResponse.model_validate(order)
