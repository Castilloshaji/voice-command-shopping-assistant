from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.product import Product
from app.models.shopping_list import ListItem
from app.models.history import ShoppingHistory
from app.schemas.suggestion import SuggestionResponse

class RecommendationService:
    """
    Deterministic recommendation engine.
    Scoring formula:
    score = purchase_frequency + seasonal_relevance + availability
    Excludes active shopping list items and unavailable products.
    """
    @staticmethod
    def get_suggestions(db: Session, limit: int = 5) -> List[SuggestionResponse]:
        # 1. Fetch active (uncompleted) shopping list items to exclude
        active_items = db.query(ListItem).filter(ListItem.is_completed == False).all()
        active_names = {item.item_name.strip().lower() for item in active_items}
        active_product_ids = {item.product_id for item in active_items if item.product_id is not None}

        # 2. Query purchase frequency counts from ShoppingHistory
        history_counts = (
            db.query(func.lower(ShoppingHistory.item_name), func.count(ShoppingHistory.id))
            .group_by(func.lower(ShoppingHistory.item_name))
            .all()
        )
        history_freq_map = {name: count for name, count in history_counts}

        # 3. Score catalog products
        all_products = db.query(Product).all()
        candidates = []

        for prod in all_products:
            prod_name_clean = prod.name.strip().lower()

            # Rule: Exclude products already on the active shopping list
            if prod_name_clean in active_names or prod.id in active_product_ids:
                continue

            # Rule: Exclude unavailable products unless offering substitutes
            if not prod.is_available:
                continue

            freq = history_freq_map.get(prod_name_clean, 0)
            freq_score = float(freq * 2.0)

            # Seasonal relevance score
            seasonal_score = 2.0 if prod.season in ["summer", "all", "fall", "winter", "spring"] else 1.0
            avail_score = 1.0 if prod.is_available else 0.0

            total_score = round(freq_score + seasonal_score + avail_score, 2)

            if freq > 0:
                reason = f"Frequently Bought ({freq}x)"
            elif prod.season and prod.season != "all":
                reason = f"Seasonal ({prod.season.capitalize()})"
            else:
                reason = "Popular Essential"

            candidates.append({
                "product_id": prod.id,
                "item_name": prod.name,
                "category": prod.category,
                "reason": reason,
                "score": total_score
            })

        # Sort by total_score descending, fallback to item_name ascending
        candidates.sort(key=lambda c: (-c["score"], c["item_name"]))

        top_candidates = candidates[:limit]
        return [SuggestionResponse(**c) for c in top_candidates]
