from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.product import Product
from app.models.shopping_list import ListItem
from app.models.history import ShoppingHistory
from app.schemas.suggestion import SuggestionResponse
from app.services.product_service import ProductService

def get_season_for_month(month: int) -> str:
    """
    Resolves month (1-12) to season:
    December (12), January (1), February (2) -> 'winter'
    March (3), April (4), May (5) -> 'spring'
    June (6), July (7), August (8) -> 'summer'
    September (9), October (10), November (11) -> 'fall'
    """
    if month in (12, 1, 2):
        return "winter"
    elif month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    elif month in (9, 10, 11):
        return "fall"
    raise ValueError(f"Invalid month: {month}")

def get_current_season(override_month: Optional[int] = None) -> str:
    """
    Returns the current season name. Allows override_month for deterministic testing.
    """
    if override_month is not None:
        return get_season_for_month(override_month)
    return get_season_for_month(datetime.now().month)

class RecommendationService:
    """
    Deterministic, explainable recommendation engine.
    Scoring formula:
        historical_score = purchase_count * 2.0
        seasonal_score =
            2.0 if product season == current season
            1.0 if product season == "all"
            0.0 otherwise
        total_score = historical_score + seasonal_score

    Availability is a HARD FILTER for standard recommendations.
    Deterministic ordering:
        1. total_score DESC
        2. product name ASC (case-insensitive)
    Excludes items already present on active shopping list.
    Offers substitutes for unavailable high-preference items.
    """
    @staticmethod
    def get_suggestions(
        db: Session,
        limit: int = 5,
        month: Optional[int] = None
    ) -> List[SuggestionResponse]:
        current_season = get_current_season(override_month=month)

        # 1. Fetch active (uncompleted) shopping list items to exclude
        active_items = db.query(ListItem).filter(ListItem.is_completed == False).all()
        active_names = {item.item_name.strip().lower() for item in active_items if item.item_name}
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
        candidates_map: Dict[int, Dict[str, Any]] = {}

        for prod in all_products:
            prod_name_clean = prod.name.strip().lower()

            # Rule: Exclude products already on active shopping list
            if prod_name_clean in active_names or prod.id in active_product_ids:
                continue

            freq = history_freq_map.get(prod_name_clean, 0)

            # Rule: Unavailable products cannot be standard recommendations directly,
            # but if they have history/preference, offer available substitutes!
            if not prod.is_available:
                if freq > 0 or (prod.season and prod.season.lower() in [current_season, "all"]):
                    substitutes = ProductService.get_substitutes_for_product(db, prod)
                    for sub in substitutes:
                        sub_name_clean = sub.name.strip().lower()
                        if sub_name_clean in active_names or sub.id in active_product_ids or not sub.is_available:
                            continue

                        sub_freq = history_freq_map.get(sub_name_clean, 0)
                        effective_freq = max(freq, sub_freq)
                        sub_hist_score = float(effective_freq * 2.0)

                        sub_season_lower = sub.season.lower() if sub.season else ""
                        if sub_season_lower == current_season:
                            sub_season_score = 2.0
                        elif sub_season_lower == "all":
                            sub_season_score = 1.0
                        else:
                            sub_season_score = 0.0

                        sub_total_score = round(sub_hist_score + sub_season_score, 2)
                        reason = f"A substitute for unavailable {prod.name}."

                        sub_candidate = {
                            "product_id": sub.id,
                            "item_name": sub.name,
                            "product": sub.name,
                            "category": sub.category,
                            "reason": reason,
                            "score": sub_total_score,
                            "is_substitute": True,
                            "substitute_for": prod.name
                        }

                        if sub.id not in candidates_map or candidates_map[sub.id]["score"] < sub_total_score:
                            candidates_map[sub.id] = sub_candidate
                continue

            # Available catalog product standard scoring
            historical_score = float(freq * 2.0)

            prod_season_lower = prod.season.lower() if prod.season else ""
            if prod_season_lower == current_season:
                seasonal_score = 2.0
            elif prod_season_lower == "all":
                seasonal_score = 1.0
            else:
                seasonal_score = 0.0

            total_score = round(historical_score + seasonal_score, 2)

            if historical_score > 0 and seasonal_score == 2.0:
                reason = "You frequently purchase this item and it is in season."
            elif historical_score > 0:
                reason = "You frequently purchase this item."
            elif seasonal_score == 2.0:
                reason = "This item is in season."
            elif seasonal_score == 1.0:
                reason = "Year-round staple item."
            else:
                reason = "Popular essential item."

            candidate = {
                "product_id": prod.id,
                "item_name": prod.name,
                "product": prod.name,
                "category": prod.category,
                "reason": reason,
                "score": total_score,
                "is_substitute": False,
                "substitute_for": None
            }

            if prod.id not in candidates_map or candidates_map[prod.id]["score"] < total_score:
                candidates_map[prod.id] = candidate

        candidates = list(candidates_map.values())

        # Deterministic sorting: total_score DESC, product name ASC (case-insensitive)
        candidates.sort(key=lambda c: (-c["score"], c["item_name"].strip().lower()))

        top_candidates = candidates[:limit]
        return [SuggestionResponse(**c) for c in top_candidates]

