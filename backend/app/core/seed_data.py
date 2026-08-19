from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.product import Product

SEED_PRODUCTS: List[Dict[str, Any]] = [
    # Dairy
    {
        "name": "Whole Milk",
        "category": "dairy",
        "brand": "Organic Valley",
        "price": 3.99,
        "size": "1 gallon",
        "is_available": True,
        "season": "all",
        "substitutes": ["Oat Milk", "Almond Milk"]
    },
    {
        "name": "Greek Yogurt",
        "category": "dairy",
        "brand": "Chobani",
        "price": 1.49,
        "size": "5.3 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cottage Cheese", "Plain Yogurt"]
    },
    {
        "name": "Cheddar Cheese",
        "category": "dairy",
        "brand": "Tillamook",
        "price": 4.29,
        "size": "8 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Swiss Cheese", "Mozzarella"]
    },
    {
        "name": "Unsalted Butter",
        "category": "dairy",
        "brand": "Land O'Lakes",
        "price": 4.99,
        "size": "16 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Margarine", "Salted Butter"]
    },
    # Produce
    {
        "name": "Fresh Bananas",
        "category": "produce",
        "brand": "Dole",
        "price": 0.59,
        "size": "1 lb",
        "is_available": True,
        "season": "all",
        "substitutes": ["Apples", "Pears"]
    },
    {
        "name": "Organic Strawberries",
        "category": "produce",
        "brand": "Driscoll's",
        "price": 4.99,
        "size": "1 lb",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Blueberries", "Raspberries"]
    },
    {
        "name": "Gala Apples",
        "category": "produce",
        "brand": "Washington Fresh",
        "price": 1.99,
        "size": "1 lb",
        "is_available": True,
        "season": "fall",
        "substitutes": ["Fuji Apples", "Honeycrisp Apples"]
    },
    {
        "name": "Baby Spinach",
        "category": "produce",
        "brand": "Organic Girl",
        "price": 3.49,
        "size": "5 oz",
        "is_available": True,
        "season": "spring",
        "substitutes": ["Kale", "Arugula"]
    },
    # Bakery
    {
        "name": "Whole Wheat Bread",
        "category": "bakery",
        "brand": "Nature's Own",
        "price": 2.89,
        "size": "20 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Multigrain Bread", "White Bread"]
    },
    {
        "name": "Sourdough Loaf",
        "category": "bakery",
        "brand": "Artisan Bakery",
        "price": 4.50,
        "size": "1 loaf",
        "is_available": True,
        "season": "all",
        "substitutes": ["Ciabatta", "French Baguette"]
    },
    {
        "name": "Butter Croissant",
        "category": "bakery",
        "brand": "Fresh Bakery",
        "price": 1.99,
        "size": "1 pc",
        "is_available": False,
        "season": "all",
        "substitutes": ["Chocolate Croissant", "Danish Pastry"]
    },
    # Beverages
    {
        "name": "Orange Juice",
        "category": "beverages",
        "brand": "Tropicana",
        "price": 3.79,
        "size": "52 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Apple Juice", "Grapefruit Juice"]
    },
    {
        "name": "Sparkling Water",
        "category": "beverages",
        "brand": "LaCroix",
        "price": 4.99,
        "size": "12 pack",
        "is_available": False,
        "season": "summer",
        "substitutes": ["Club Soda", "Flavored Water"]
    },
    {
        "name": "Dark Roast Coffee",
        "category": "beverages",
        "brand": "Starbucks",
        "price": 8.99,
        "size": "12 oz bag",
        "is_available": True,
        "season": "all",
        "substitutes": ["Medium Roast Coffee", "Espresso Beans"]
    },
    # Snacks
    {
        "name": "Classic Potato Chips",
        "category": "snacks",
        "brand": "Lay's",
        "price": 3.49,
        "size": "8 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Tortilla Chips", "Pretzels"]
    },
    {
        "name": "Mixed Nuts",
        "category": "snacks",
        "brand": "Planters",
        "price": 6.99,
        "size": "10 oz",
        "is_available": True,
        "season": "winter",
        "substitutes": ["Almonds", "Cashews"]
    },
    # Personal Care
    {
        "name": "Beauty Bar Soap",
        "category": "personal care",
        "brand": "Dove",
        "price": 4.29,
        "size": "4 pack",
        "is_available": True,
        "season": "all",
        "substitutes": ["Body Wash", "Liquid Soap"]
    },
    {
        "name": "Mint Toothpaste",
        "category": "personal care",
        "brand": "Crest",
        "price": 3.19,
        "size": "4.2 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Colgate Toothpaste", "Sensodyne"]
    },
    # Household
    {
        "name": "Paper Towels",
        "category": "household",
        "brand": "Bounty",
        "price": 8.99,
        "size": "6 rolls",
        "is_available": True,
        "season": "all",
        "substitutes": ["Napkins", "Microfiber Cloths"]
    },
    {
        "name": "Dish Soap",
        "category": "household",
        "brand": "Dawn",
        "price": 2.99,
        "size": "16 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Palmolive Dish Soap", "Hand Soap"]
    }
]

def seed_products(db: Session) -> None:
    """Seed default product catalog if table is empty."""
    existing_count = db.query(Product).count()
    if existing_count == 0:
        products = [Product(**data) for data in SEED_PRODUCTS]
        db.add_all(products)
        db.commit()
