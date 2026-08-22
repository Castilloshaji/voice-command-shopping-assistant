from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.product import Product

GENERIC_SEARCH_TERMS = {"product", "products", "item", "items", "anything", "all", "grocery", "groceries"}

class ProductService:
    @staticmethod
    def search_products(
        db: Session,
        query: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        availability: Optional[bool] = None
    ) -> List[Product]:
        """
        Executes local catalog search with optional item/query, category, brand, min_price, max_price, and availability filters.
        Case-insensitive, whitespace tolerant, and deterministically ranked.
        """
        stmt = db.query(Product)

        clean_query: Optional[str] = None
        is_generic_query = False

        if query and query.strip():
            stripped_q = query.strip().lower()
            if stripped_q in GENERIC_SEARCH_TERMS:
                is_generic_query = True
            else:
                clean_query = stripped_q

        if clean_query:
            like_pattern = f"%{clean_query}%"
            stmt = stmt.filter(
                func.lower(Product.name).like(like_pattern) |
                func.lower(Product.category).like(like_pattern)
            )

        if category and category.strip():
            clean_cat = f"%{category.strip().lower()}%"
            stmt = stmt.filter(func.lower(Product.category).like(clean_cat))

        if brand and brand.strip():
            clean_b = brand.strip().lower()
            stmt = stmt.filter(func.lower(Product.brand) == clean_b)

        if min_price is not None:
            stmt = stmt.filter(Product.price >= min_price)

        if max_price is not None:
            stmt = stmt.filter(Product.price <= max_price)

        if availability is not None:
            stmt = stmt.filter(Product.is_available == availability)

        products = stmt.all()

        # Deterministic Ranking
        # 1. Exact product-name match (rank 1)
        # 2. Product-name substring match (rank 2)
        # 3. Category match (rank 3)
        # 4. Other matches (rank 4)
        # Secondary ordering: product name ascending
        def get_rank(prod: Product) -> int:
            if not clean_query:
                return 4
            p_name = prod.name.strip().lower()
            p_cat = prod.category.strip().lower()

            if p_name == clean_query:
                return 1
            if clean_query in p_name:
                return 2
            if clean_query in p_cat:
                return 3
            return 4

        products.sort(key=lambda p: (get_rank(p), p.name.strip().lower(), p.id))
        return products

    @staticmethod
    def get_substitutes_for_product(db: Session, product: Product) -> List[Product]:
        """
        For an unavailable product, inspects its substitute names, resolves them against
        the Product catalog, retains only available substitutes, and returns them.
        """
        if not product or not product.substitutes:
            return []

        subs_list = product.substitutes
        if isinstance(subs_list, str):
            import json
            try:
                subs_list = json.loads(subs_list)
            except Exception:
                subs_list = [subs_list]

        if not isinstance(subs_list, list):
            return []

        clean_sub_names = [str(s).strip().lower() for s in subs_list if s and str(s).strip()]
        if not clean_sub_names:
            return []

        result = []
        seen_ids = set()

        for sub_name in clean_sub_names:
            # 1. Exact name match for available catalog product
            matched = (
                db.query(Product)
                .filter(Product.is_available == True, func.lower(Product.name) == sub_name)
                .first()
            )
            # 2. Substring match fallback for available catalog product
            if not matched:
                matched = (
                    db.query(Product)
                    .filter(Product.is_available == True, func.lower(Product.name).like(f"%{sub_name}%"))
                    .first()
                )

            if matched and matched.id != product.id and matched.id not in seen_ids:
                result.append(matched)
                seen_ids.add(matched.id)

        # Sort substitutes deterministically by name ascending
        result.sort(key=lambda p: p.name.strip().lower())
        return result

