import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.product import Product
from app.services.product_service import ProductService
from app.services.nlp_service import NLPService
from app.services.command_service import CommandService
from app.schemas.intent import IntentEnum, ParsedIntent

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    # Seed products
    products = [
        Product(id=1, name="Dove Toothpaste", category="Personal Care", brand="Dove", price=4.50, is_available=True, season="all"),
        Product(id=2, name="Crest Toothpaste", category="Personal Care", brand="Crest", price=3.50, is_available=True, season="all"),
        Product(id=3, name="Whole Milk", category="Dairy", brand="DairyPure", price=2.99, is_available=True, season="all"),
        Product(id=4, name="Butter Croissant", category="Bakery", brand="BakeryFresh", price=3.99, is_available=False, season="all", substitutes=["Chocolate Croissant", "Oat Milk"]),
        Product(id=5, name="Chocolate Croissant", category="Bakery", brand="BakeryFresh", price=4.25, is_available=True, season="all"),
        Product(id=6, name="Sparkling Water", category="Beverages", brand="Bubly", price=5.99, is_available=False, season="summer", substitutes=["Club Soda"]),
        Product(id=7, name="Club Soda", category="Beverages", brand="Canada Dry", price=2.49, is_available=True, season="all"),
    ]
    session.add_all(products)
    session.commit()

    yield session
    session.close()

def test_basic_search_and_case_insensitivity(db):
    results = ProductService.search_products(db, query="toothpaste")
    assert len(results) == 2

    results_upper = ProductService.search_products(db, query="TOOTHPASTE")
    assert len(results_upper) == 2
    assert [p.id for p in results] == [p.id for p in results_upper]

@pytest.mark.parametrize(
    ("command", "expected_ids"),
    [
        ("Find toothpaste", [2, 1]),
        ("Find toothpaste under $5", [2, 1]),
        ("Find toothpaste between $4 and $5", [1]),
        ("Find Dove toothpaste", [1]),
        ("Find toothpaste from Dove", [1]),
    ],
)
def test_natural_language_search_filters_flow_through_command_service(db, command, expected_ids):
    parsed = NLPService.parse_transcript(command)

    assert parsed.intent == IntentEnum.SEARCH_PRODUCT
    response = CommandService.execute_command(db, parsed)

    assert response.success is True
    assert [product["id"] for product in response.data] == expected_ids

def test_whitespace_tolerance(db):
    results = ProductService.search_products(db, query="   toothpaste   ")
    assert len(results) == 2

def test_brand_filter(db):
    results = ProductService.search_products(db, query="toothpaste", brand="Dove")
    assert len(results) == 1
    assert results[0].name == "Dove Toothpaste"

def test_min_and_max_price_filters(db):
    # Under $4.00
    under_4 = ProductService.search_products(db, max_price=4.00)
    assert all(p.price <= 4.00 for p in under_4)
    assert len(under_4) >= 3

    # Min price $4.00
    min_4 = ProductService.search_products(db, min_price=4.00)
    assert all(p.price >= 4.00 for p in min_4)

    # Range $3.00 to $5.00
    range_3_5 = ProductService.search_products(db, min_price=3.00, max_price=5.00)
    assert all(3.00 <= p.price <= 5.00 for p in range_3_5)

def test_category_filter(db):
    results = ProductService.search_products(db, category="Dairy")
    assert len(results) == 1
    assert results[0].name == "Whole Milk"

def test_availability_filter(db):
    avail_only = ProductService.search_products(db, availability=True)
    assert all(p.is_available is True for p in avail_only)

    unavail_only = ProductService.search_products(db, availability=False)
    assert all(p.is_available is False for p in unavail_only)
    assert len(unavail_only) == 2

def test_no_results_returns_empty_list_and_success(db):
    results = ProductService.search_products(db, query="NonExistentItem12345")
    assert results == []

    parsed = NLPService.parse_transcript("Find NonExistentItem12345")
    resp = CommandService.execute_command(db, parsed)
    assert resp.success is True
    assert resp.data == []
    assert "No products found" in resp.message

def test_unavailable_product_search_preserves_original_and_provides_substitutes(db):
    results = ProductService.search_products(db, query="Sparkling Water")
    assert len(results) == 1
    original = results[0]
    assert original.name == "Sparkling Water"
    assert original.is_available is False

    # Check substitutes resolution
    subs = ProductService.get_substitutes_for_product(db, original)
    assert len(subs) == 1
    assert subs[0].name == "Club Soda"
    assert subs[0].is_available is True

    # Test Command execution output
    parsed = ParsedIntent(
        intent=IntentEnum.SEARCH_PRODUCT,
        item="Sparkling Water",
        original_text="Find Sparkling Water"
    )
    resp = CommandService.execute_command(db, parsed)
    assert resp.success is True
    data = resp.data
    assert len(data) == 1
    assert data[0]["name"] == "Sparkling Water"
    assert data[0]["is_available"] is False
    assert len(data[0]["substitute_products"]) == 1
    assert data[0]["substitute_products"][0]["name"] == "Club Soda"
    assert data[0]["substitute_products"][0]["is_available"] is True

def test_generic_query_handling(db):
    parsed = NLPService.parse_transcript("Find products between $3 and $7")
    assert parsed.intent == IntentEnum.SEARCH_PRODUCT
    assert parsed.item is None
    assert parsed.min_price == 3.0
    assert parsed.max_price == 7.0

    resp = CommandService.execute_command(db, parsed)
    assert resp.success is True
    assert len(resp.data) > 0
    assert all(3.0 <= p["price"] <= 7.0 for p in resp.data)
