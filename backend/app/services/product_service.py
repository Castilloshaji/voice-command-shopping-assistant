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

    @staticmethod
    def resolve_product(db: Session, item_name: str) -> dict:
        """
        Validates item_name against the Product catalog.
        Returns:
        {
            "exact_match": Product | None,
            "suggestions": List[Product]
        }
        """
        import difflib

        clean_name = item_name.strip().lower()
        if not clean_name:
            return {"exact_match": None, "suggestions": []}

        all_products = db.query(Product).all()
        if not all_products:
            return {"exact_match": None, "suggestions": []}

        # 1. Exact match (case & whitespace insensitive)
        for prod in all_products:
            if prod.name.strip().lower() == clean_name:
                return {"exact_match": prod, "suggestions": []}

        # 2. Strong catalog match:
        # Check token / substring containment between item_name and catalog product names
        norm_item = clean_name.replace("yoghurt", "yogurt")

        strong_matches = []
        for prod in all_products:
            p_name_lower = prod.name.strip().lower()
            if norm_item == p_name_lower:
                return {"exact_match": prod, "suggestions": []}

            tokens = [t for t in norm_item.split() if len(t) > 2]
            p_tokens = p_name_lower.split()

            # Direct containment or token match
            if norm_item in p_name_lower or p_name_lower in norm_item:
                strong_matches.append(prod)
            elif tokens and any(t in p_tokens for t in tokens):
                strong_matches.append(prod)

        if strong_matches:
            # Sort deterministically by shortest name length difference, name ascending, id
            strong_matches.sort(key=lambda p: (abs(len(p.name) - len(item_name)), p.name.strip().lower(), p.id))
            return {"exact_match": strong_matches[0], "suggestions": []}

        # 3. No strong catalog match found (e.g. "minutes" or "unknownproduct")
        # Candidate suggestions search using difflib.SequenceMatcher
        scored_candidates = []
        for prod in all_products:
            ratio = difflib.SequenceMatcher(None, norm_item, prod.name.strip().lower()).ratio()
            # Also evaluate ratio per token in product name
            for p_word in prod.name.strip().lower().split():
                w_ratio = difflib.SequenceMatcher(None, norm_item, p_word).ratio()
                if w_ratio > ratio:
                    ratio = w_ratio

            # Only suggest products with reasonable similarity (threshold >= 0.5)
            if ratio >= 0.5:
                scored_candidates.append((ratio, prod))

        scored_candidates.sort(key=lambda x: (-x[0], x[1].name.strip().lower(), x[1].id))
        suggestions = [prod for _, prod in scored_candidates[:3]]

        return {
            "exact_match": None,
            "suggestions": suggestions
        }

