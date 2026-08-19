from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.product import Product

class ProductService:
    @staticmethod
    def search_products(
        db: Session,
        query: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Product]:
        """
        Executes local catalog search with optional item/query, brand, min_price, and max_price filters.
        Case-insensitive and deterministic.
        """
        stmt = db.query(Product)

        if query and query.strip():
            clean_q = f"%{query.strip().lower()}%"
            stmt = stmt.filter(
                func.lower(Product.name).like(clean_q) |
                func.lower(Product.category).like(clean_q)
            )

        if brand and brand.strip():
            clean_b = brand.strip().lower()
            stmt = stmt.filter(func.lower(Product.brand) == clean_b)

        if min_price is not None:
            stmt = stmt.filter(Product.price >= min_price)

        if max_price is not None:
            stmt = stmt.filter(Product.price <= max_price)

        return stmt.order_by(Product.name.asc()).all()
