from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.shopping_list import ListItem
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.history import ShoppingHistory
from app.services.product_service import ProductService
from app.schemas.checkout import (
    CheckoutPreviewResponse,
    CheckoutItemResponse,
    OrderResponse,
    OrderItemResponse
)

def utc_now():
    return datetime.now(timezone.utc)

class CheckoutService:
    @staticmethod
    def get_cart_hash(db: Session) -> Tuple[Tuple[int, float], ...]:
        """Returns a tuple snapshot of active cart items and quantities to detect stale checkout context."""
        active_items = db.query(ListItem).filter(ListItem.is_completed == False).order_by(ListItem.id).all()
        return tuple((item.id, float(item.quantity)) for item in active_items)

    @staticmethod
    def preview_checkout(db: Session) -> CheckoutPreviewResponse:
        """
        Calculates non-mutating checkout totals, line items, prices, and availability from database catalog.
        """
        active_items = db.query(ListItem).filter(ListItem.is_completed == False).order_by(ListItem.id).all()

        preview_items: List[CheckoutItemResponse] = []
        subtotal = 0.0
        has_unavailable = False

        for item in active_items:
            product = None
            if item.product_id:
                product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                res = ProductService.resolve_product(db, item.item_name)
                product = res.get("exact_match")

            if product:
                unit_price = float(product.price)
                brand = product.brand
                is_available = bool(product.is_available)
                prod_id = product.id
                substitute_objs = ProductService.get_substitutes_for_product(db, product) if not is_available else []
                substitutes = [{"product_id": s.id, "name": s.name, "brand": s.brand, "price": s.price} for s in substitute_objs]
            else:
                unit_price = 0.0
                brand = None
                is_available = False
                prod_id = None
                substitutes = []

            if not is_available:
                has_unavailable = True

            qty = float(item.quantity) if item.quantity > 0 else 1.0
            line_total = round(qty * unit_price, 2)
            subtotal += line_total

            preview_items.append(
                CheckoutItemResponse(
                    product_id=prod_id,
                    name=product.name if product else item.item_name,
                    brand=brand,
                    quantity=qty,
                    unit=item.unit,
                    unit_price=unit_price,
                    line_total=line_total,
                    is_available=is_available,
                    substitutes=substitutes
                )
            )

        subtotal = round(subtotal, 2)
        total = subtotal

        return CheckoutPreviewResponse(
            items=preview_items,
            subtotal=subtotal,
            discount=0.0,
            total=total,
            item_count=len(preview_items),
            has_unavailable=has_unavailable
        )

    @staticmethod
    def place_order(db: Session) -> Order:
        """
        Executes atomic checkout transaction.
        Validates all items, creates Order and OrderItem records, marks active list items completed.
        If ANY validation fails, rolls back completely without mutating database.
        """
        active_items = db.query(ListItem).filter(ListItem.is_completed == False).order_by(ListItem.id).all()

        if not active_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Shopping list is empty."
            )

        validated_order_items = []
        subtotal = 0.0

        for item in active_items:
            if item.quantity <= 0:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Item '{item.item_name}' has an invalid quantity ({item.quantity})."
                )

            product = None
            if item.product_id:
                product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                res = ProductService.resolve_product(db, item.item_name)
                product = res.get("exact_match")

            if not product:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Item '{item.item_name}' is not in the catalog. Cannot checkout."
                )

            if not product.is_available:
                prod_name = product.name
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Item '{prod_name}' is currently unavailable. Replace or remove it to complete checkout."
                )

            qty = float(item.quantity)
            unit_price = float(product.price)
            line_total = round(qty * unit_price, 2)
            subtotal += line_total

            validated_order_items.append({
                "product_id": product.id,
                "product_name_snapshot": product.name,
                "brand_snapshot": product.brand,
                "quantity": qty,
                "unit": item.unit,
                "unit_price": unit_price,
                "line_total": line_total,
                "list_item": item
            })

        subtotal = round(subtotal, 2)
        total = subtotal

        # Generate unique order number
        today_str = datetime.now().strftime("%Y%m%d")
        existing_today_count = db.query(Order).filter(Order.order_number.like(f"ORD-{today_str}-%")).count()
        order_num = f"ORD-{today_str}-{(existing_today_count + 1):04d}"

        try:
            order = Order(
                order_number=order_num,
                status="COMPLETED",
                subtotal=subtotal,
                discount=0.0,
                total=total,
                created_at=utc_now()
            )
            db.add(order)
            db.flush()

            for item_data in validated_order_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data["product_id"],
                    product_name_snapshot=item_data["product_name_snapshot"],
                    brand_snapshot=item_data["brand_snapshot"],
                    quantity=item_data["quantity"],
                    unit=item_data["unit"],
                    unit_price=item_data["unit_price"],
                    line_total=item_data["line_total"]
                )
                db.add(order_item)

                # Mark list item completed and add to ShoppingHistory
                list_item = item_data["list_item"]
                list_item.is_completed = True

                hist = ShoppingHistory(
                    item_name=item_data["product_name_snapshot"],
                    category=list_item.category,
                    quantity=item_data["quantity"],
                    purchased_at=utc_now()
                )
                db.add(hist)

            db.commit()
            db.refresh(order)
            return order

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to place order: {str(e)}"
            )

    @staticmethod
    def get_orders(db: Session) -> List[Order]:
        return db.query(Order).order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Order:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order #{order_id} not found."
            )
        return order
