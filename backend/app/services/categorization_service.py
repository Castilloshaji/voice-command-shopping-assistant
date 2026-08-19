from typing import Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.product import Product

DETERMINISTIC_CATEGORY_MAPPING = {
    # Dairy
    "milk": "dairy",
    "yogurt": "dairy",
    "yoghurt": "dairy",
    "cheese": "dairy",
    "butter": "dairy",
    "cream": "dairy",
    "curd": "dairy",

    # Produce
    "apple": "produce",
    "apples": "produce",
    "banana": "produce",
    "bananas": "produce",
    "strawberry": "produce",
    "strawberries": "produce",
    "spinach": "produce",
    "kale": "produce",
    "fruit": "produce",
    "vegetable": "produce",
    "tomato": "produce",
    "tomatoes": "produce",
    "potato": "produce",
    "potatoes": "produce",
    "onion": "produce",
    "onions": "produce",
    "berry": "produce",
    "berries": "produce",

    # Bakery
    "bread": "bakery",
    "loaf": "bakery",
    "croissant": "bakery",
    "bagel": "bakery",
    "bagels": "bakery",
    "muffin": "bakery",
    "muffins": "bakery",
    "pastry": "bakery",
    "cake": "bakery",
    "bun": "bakery",
    "buns": "bakery",

    # Beverages
    "juice": "beverages",
    "water": "beverages",
    "coffee": "beverages",
    "tea": "beverages",
    "soda": "beverages",
    "drink": "beverages",
    "cola": "beverages",

    # Snacks
    "chips": "snacks",
    "nuts": "snacks",
    "chocolate": "snacks",
    "popcorn": "snacks",
    "cracker": "snacks",
    "crackers": "snacks",
    "pretzel": "snacks",
    "pretzels": "snacks",

    # Personal Care
    "soap": "personal care",
    "toothpaste": "personal care",
    "shampoo": "personal care",
    "conditioner": "personal care",
    "lotion": "personal care",
    "deodorant": "personal care",

    # Household
    "towel": "household",
    "towels": "household",
    "paper": "household",
    "detergent": "household",
    "cleaner": "household",
    "napkin": "household",
    "napkins": "household",
    "tissue": "household",
    "tissues": "household"
}

class CategorizationService:
    @staticmethod
    def match_product_and_category(db: Session, item_name: str) -> Tuple[Optional[int], str]:
        """
        Attempts to match an item_name against the Product catalog first.
        If matched, returns (product.id, product.category).
        If not matched, falls back to deterministic keyword mapping.
        Defaults to 'general' if unknown.
        """
        clean_name = item_name.strip().lower()
        if not clean_name:
            return None, "general"

        # 1. Catalog Match: Exact lower-case match
        exact_match = db.query(Product).filter(func.lower(Product.name) == clean_name).first()
        if exact_match:
            return exact_match.id, exact_match.category

        # Catalog Match: Substring or containment match
        all_products = db.query(Product).all()
        for prod in all_products:
            prod_name_lower = prod.name.lower()
            if clean_name in prod_name_lower or prod_name_lower in clean_name:
                return prod.id, prod.category

        # 2. Deterministic keyword fallback mapping
        tokens = clean_name.split()
        for token in tokens:
            if token in DETERMINISTIC_CATEGORY_MAPPING:
                return None, DETERMINISTIC_CATEGORY_MAPPING[token]

        for keyword, category in DETERMINISTIC_CATEGORY_MAPPING.items():
            if keyword in clean_name:
                return None, category

        # 3. Default category
        return None, "general"
