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

            # Direct containment: input item is substring of product name or product name equals input item
            if norm_item in p_name_lower:
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

    @staticmethod
    def resolve_compound_items(db: Session, text: str, initial_qty: Optional[float] = None, initial_unit: Optional[str] = None):
        """
        Attempts catalog-aware compound segmentation of a voice transcript clause into
        a list of IntentItem objects if the ENTIRE clause can be covered by valid catalog products.
        Returns None if any part of the clause contains unknown products.
        """
        from app.schemas.intent import IntentItem
        from app.services.nlp_service import UNITS_MAP, NLPService

        raw_text = text.strip().lower()
        if not raw_text:
            return None

        all_products = db.query(Product).all()
        if not all_products:
            return None

        # Build catalog product terms mapping
        catalog_terms = {}
        for p in all_products:
            p_name = p.name.strip()
            p_lower = p_name.lower()
            catalog_terms[p_lower] = p_lower

            words = p_lower.split()
            if "milk" in words:
                catalog_terms["milk"] = "milk"
            if "apples" in words or "apple" in words:
                catalog_terms["apples"] = "apples"
                catalog_terms["apple"] = "apples"
            if "bananas" in words or "banana" in words:
                catalog_terms["bananas"] = "bananas"
                catalog_terms["banana"] = "bananas"
            if "strawberries" in words or "strawberry" in words:
                catalog_terms["strawberries"] = "strawberries"
                catalog_terms["strawberry"] = "strawberries"
            if "bread" in words or "loaf" in words:
                catalog_terms["bread"] = "bread"
            if "cheese" in words:
                catalog_terms["cheese"] = "cheese"
            if "butter" in words:
                catalog_terms["butter"] = "butter"
            if "yogurt" in words or "yoghurt" in words:
                catalog_terms["yogurt"] = "yogurt"
                catalog_terms["yoghurt"] = "yoghurt"
            if "juice" in words:
                catalog_terms["juice"] = "juice"
            if "water" in words:
                catalog_terms["water"] = "water"
            if "coffee" in words:
                catalog_terms["coffee"] = "coffee"
            if "chips" in words:
                catalog_terms["chips"] = "chips"
            if "nuts" in words:
                catalog_terms["nuts"] = "nuts"
            if "soap" in words:
                catalog_terms["soap"] = "soap"
            if "toothpaste" in words:
                catalog_terms["toothpaste"] = "toothpaste"
            if "towels" in words or "towel" in words:
                catalog_terms["towels"] = "towels"
            if "detergent" in words:
                catalog_terms["detergent"] = "detergent"

        catalog_terms["eggs"] = "eggs"
        catalog_terms["egg"] = "eggs"

        filler_words = {"and", "then", "please", "add", "buy", "to", "the", "a", "an", "on", "my", "list", "get", "need", "put"}

        tokens = raw_text.split()
        if not tokens:
            return None

        result_items = []
        i = 0
        n = len(tokens)

        units_keys = set(UNITS_MAP.keys())

        while i < n:
            while i < n and tokens[i] in filler_words:
                i += 1
            if i >= n:
                break

            qty_val = None
            unit_val = None

            parsed_num = NLPService.parse_number(tokens[i])
            if parsed_num is not None:
                qty_val = parsed_num
                i += 1
                while i < n and tokens[i] in filler_words:
                    i += 1

                if i < n and tokens[i] in units_keys:
                    unit_val = UNITS_MAP[tokens[i]]
                    i += 1
                    if i < n and tokens[i] in ("of", "the"):
                        i += 1

            while i < n and tokens[i] in filler_words:
                i += 1
            if i >= n:
                break

            matched_item_name = None
            matched_len = 0

            max_k = min(n, i + 4)
            for k in range(max_k, i, -1):
                phrase = " ".join(tokens[i:k])
                if phrase in catalog_terms:
                    matched_item_name = catalog_terms[phrase]
                    matched_len = k - i
                    break
                else:
                    res = ProductService.resolve_product(db, phrase)
                    if res["exact_match"] is not None:
                        matched_item_name = res["exact_match"].name.strip().lower()
                        matched_len = k - i
                        break

            if matched_item_name is not None and matched_len > 0:
                final_qty = qty_val
                final_unit = unit_val
                if len(result_items) == 0 and final_qty is None and initial_qty is not None:
                    final_qty = initial_qty
                    final_unit = initial_unit

                result_items.append(IntentItem(
                    item=matched_item_name,
                    quantity=final_qty if final_qty is not None else 1.0,
                    unit=final_unit
                ))
                i += matched_len
            else:
                return None

        if result_items:
            return result_items
        return None

