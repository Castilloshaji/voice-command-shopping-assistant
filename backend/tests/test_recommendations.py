import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.product import Product
from app.models.shopping_list import ListItem
from app.models.history import ShoppingHistory
from app.services.recommendation_service import RecommendationService

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    # Catalog Products
    products = [
        Product(id=1, name="Whole Milk", category="Dairy", price=3.99, is_available=True, season="all"),
        Product(id=2, name="Whole Wheat Bread", category="Bakery", price=2.49, is_available=True, season="all"),
        Product(id=3, name="Organic Strawberries", category="Produce", price=4.99, is_available=True, season="summer"),
        Product(id=4, name="Hot Cocoa Mix", category="Beverages", price=3.50, is_available=True, season="winter"),
        Product(id=5, name="Butter Croissant", category="Bakery", price=2.99, is_available=False, season="all", substitutes=["Chocolate Croissant"]),
        Product(id=6, name="Chocolate Croissant", category="Bakery", price=3.25, is_available=True, season="all"),
        Product(id=7, name="Alpha Item", category="Pantry", price=1.99, is_available=True, season="all"),
        Product(id=8, name="Beta Item", category="Pantry", price=1.99, is_available=True, season="all"),
    ]
    session.add_all(products)
    session.commit()

    yield session
    session.close()

def test_purchase_history_ranking(db):
    # Add history: Whole Milk x5, Whole Wheat Bread x2
    for _ in range(5):
        db.add(ShoppingHistory(item_name="Whole Milk", category="Dairy", quantity=1.0))
    for _ in range(2):
        db.add(ShoppingHistory(item_name="Whole Wheat Bread", category="Bakery", quantity=1.0))
    db.commit()

    suggestions = RecommendationService.get_suggestions(db, limit=5, month=1)
    names = [s.item_name for s in suggestions]

    assert "Whole Milk" in names
    assert "Whole Wheat Bread" in names
    assert names.index("Whole Milk") < names.index("Whole Wheat Bread")
    milk_sugg = next(s for s in suggestions if s.item_name == "Whole Milk")
    assert milk_sugg.score == 5 * 2.0 + 1.0  # history * 2 + season ("all" = 1.0)
    assert milk_sugg.reason == "You frequently purchase this item."

def test_active_list_exclusion(db):
    # Add history for Whole Milk
    for _ in range(5):
        db.add(ShoppingHistory(item_name="Whole Milk", category="Dairy", quantity=1.0))
    db.commit()

    # Add Whole Milk to active shopping list
    db.add(ListItem(item_name="Whole Milk", product_id=1, quantity=1.0, is_completed=False))
    db.commit()

    suggestions = RecommendationService.get_suggestions(db, limit=5, month=1)
    names = [s.item_name for s in suggestions]

    assert "Whole Milk" not in names

def test_unavailable_product_exclusion(db):
    # Butter Croissant is unavailable (id=5)
    suggestions = RecommendationService.get_suggestions(db, limit=10, month=1)
    names = [s.item_name for s in suggestions]

    assert "Butter Croissant" not in names

def test_seasonal_bonus_with_controlled_month(db):
    # July = Summer
    summer_suggs = RecommendationService.get_suggestions(db, limit=5, month=7)
    strawberries_summer = next(s for s in summer_suggs if s.item_name == "Organic Strawberries")
    assert strawberries_summer.score == 2.0  # seasonal bonus for summer
    assert strawberries_summer.reason == "This item is in season."

    # January = Winter
    winter_suggs = RecommendationService.get_suggestions(db, limit=5, month=1)
    cocoa_winter = next(s for s in winter_suggs if s.item_name == "Hot Cocoa Mix")
    assert cocoa_winter.score == 2.0  # seasonal bonus for winter
    assert cocoa_winter.reason == "This item is in season."

def test_deterministic_tie_breaking(db):
    # Alpha Item and Beta Item both have no history and season="all" -> score = 1.0
    suggestions = RecommendationService.get_suggestions(db, limit=10, month=1)
    items_with_1_score = [s.item_name for s in suggestions if s.score == 1.0]

    # Deterministic alphabetical ordering ASC: "Alpha Item" must come before "Beta Item"
    assert "Alpha Item" in items_with_1_score
    assert "Beta Item" in items_with_1_score
    assert items_with_1_score.index("Alpha Item") < items_with_1_score.index("Beta Item")

def test_substitute_recommendation(db):
    # Add history for unavailable product "Butter Croissant" x3
    for _ in range(3):
        db.add(ShoppingHistory(item_name="Butter Croissant", category="Bakery", quantity=1.0))
    db.commit()

    suggestions = RecommendationService.get_suggestions(db, limit=5, month=1)
    names = [s.item_name for s in suggestions]

    # Butter Croissant itself must be excluded
    assert "Butter Croissant" not in names

    # Chocolate Croissant should be suggested as substitute
    sub_sugg = next((s for s in suggestions if s.item_name == "Chocolate Croissant"), None)
    assert sub_sugg is not None
    assert sub_sugg.is_substitute is True
    assert sub_sugg.substitute_for == "Butter Croissant"
    assert "substitute for unavailable butter croissant" in sub_sugg.reason.lower()
