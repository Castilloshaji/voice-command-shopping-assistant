import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_db
from app.models import Base
from app.models.shopping_list import ListItem
from app.models.history import ShoppingHistory
from app.models.product import Product
from app.core.seed_data import seed_products

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    seed_products(db)
    db.close()

    def override_get_db():
        test_db = TestingSessionLocal()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# 1. ADD_ITEM & Duplicate Merging
def test_cmd_add_item_and_duplicate_merging(client):
    # Add new item
    res1 = client.post("/api/v1/voice/execute", json={"text": "Add 2 bottles of milk"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["success"] is True
    assert d1["intent"] == "ADD_ITEM"
    assert d1["data"]["quantity"] == 2.0
    item_id = d1["data"]["id"]

    # Duplicate active item addition -> should merge quantity
    res2 = client.post("/api/v1/voice/execute", json={"text": "Add 1 bottle of milk"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["success"] is True
    assert d2["data"]["id"] == item_id
    assert d2["data"]["quantity"] == 3.0

    # Mark item completed
    client.put(f"/api/v1/items/{item_id}", json={"is_completed": True})

    # Add item again -> should NOT merge into completed item, should create a new active item
    res3 = client.post("/api/v1/voice/execute", json={"text": "Add 1 bottle of milk"})
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["success"] is True
    assert d3["data"]["id"] != item_id
    assert d3["data"]["quantity"] == 1.0


# 2. REMOVE_ITEM
def test_cmd_remove_item(client):
    client.post("/api/v1/voice/execute", json={"text": "Add milk"})

    # Existing item removal
    res1 = client.post("/api/v1/voice/execute", json={"text": "Remove milk"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["success"] is True
    assert "Removed" in d1["message"]

    # Nonexistent item removal failure
    res2 = client.post("/api/v1/voice/execute", json={"text": "Remove nonexistent product"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["success"] is False
    assert "not on your shopping list" in d2["message"]


# 3. UPDATE_QUANTITY
def test_cmd_update_quantity(client):
    client.post("/api/v1/voice/execute", json={"text": "Add apples"})

    # Update existing quantity
    res1 = client.post("/api/v1/voice/execute", json={"text": "Set apples to 5"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["success"] is True
    assert d1["data"]["quantity"] == 5.0

    # Nonexistent item update quantity failure
    res2 = client.post("/api/v1/voice/execute", json={"text": "Set nonexistent to 10"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["success"] is False
    assert "not on your shopping list" in d2["message"]


# 4. SHOW_LIST
def test_cmd_show_list(client):
    client.post("/api/v1/voice/execute", json={"text": "Add milk"})
    client.post("/api/v1/voice/execute", json={"text": "Add bananas"})

    res = client.post("/api/v1/voice/execute", json={"text": "Show my list"})
    assert res.status_code == 200
    d = res.json()
    assert d["success"] is True
    assert d["intent"] == "SHOW_LIST"
    assert len(d["data"]) == 2


# 5. CLEAR_LIST
def test_cmd_clear_list(client):
    client.post("/api/v1/voice/execute", json={"text": "Add milk"})
    client.post("/api/v1/voice/execute", json={"text": "Add bananas"})

    res = client.post("/api/v1/voice/execute", json={"text": "Clear my list"})
    assert res.status_code == 200
    d = res.json()
    assert d["success"] is True
    assert d["intent"] == "CLEAR_LIST"

    # Verify list is now empty
    items_res = client.get("/api/v1/items")
    assert len(items_res.json()) == 0


# 6. SEARCH_PRODUCT
def test_cmd_search_product(client):
    # Search query
    res1 = client.post("/api/v1/voice/execute", json={"text": "Find toothpaste"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["success"] is True
    assert len(d1["data"]) > 0

    # Search with max price filter
    res2 = client.post("/api/v1/voice/execute", json={"text": "Find toothpaste under $5"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["success"] is True
    for prod in d2["data"]:
        assert prod["price"] <= 5.0

    # Search with brand filter
    res3 = client.post("/api/v1/voice/execute", json={"text": "Find Dove toothpaste"})
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["success"] is True
    for prod in d3["data"]:
        assert prod["brand"] == "Dove"


# 7. GET_SUGGESTIONS
def test_cmd_get_suggestions(client):
    res = client.post("/api/v1/voice/execute", json={"text": "What should I buy?"})
    assert res.status_code == 200
    d = res.json()
    assert d["success"] is True
    assert d["intent"] == "GET_SUGGESTIONS"
    assert len(d["data"]) > 0


# 8. UNKNOWN
def test_cmd_unknown_intent(client):
    res = client.post("/api/v1/voice/execute", json={"text": "Random non-shopping sentence"})
    assert res.status_code == 200
    d = res.json()
    assert d["success"] is False
    assert d["intent"] == "UNKNOWN"

    # Verify database remains untouched
    items_res = client.get("/api/v1/items")
    assert len(items_res.json()) == 0


# 9. SHOPPING HISTORY TRANSITION RULES
def test_shopping_history_event_creation(client):
    # Adding item creates NO history event
    add_res = client.post("/api/v1/voice/execute", json={"text": "Add Whole Milk"})
    item_id = add_res.json()["data"]["id"]

    db = TestingSessionLocal()
    hist_count1 = db.query(ShoppingHistory).count()
    db.close()
    assert hist_count1 == 0

    # Quantity update creates NO history event
    client.put(f"/api/v1/items/{item_id}", json={"quantity": 4})
    db = TestingSessionLocal()
    hist_count2 = db.query(ShoppingHistory).count()
    db.close()
    assert hist_count2 == 0

    # Marking item completed (False -> True) creates EXACTLY ONE history event
    client.put(f"/api/v1/items/{item_id}", json={"is_completed": True})
    db = TestingSessionLocal()
    hist_count3 = db.query(ShoppingHistory).count()
    hist_event = db.query(ShoppingHistory).first()
    db.close()
    assert hist_count3 == 1
    assert hist_event.item_name.lower() == "whole milk"

    # Re-updating already completed item (True -> True) creates NO additional event
    client.put(f"/api/v1/items/{item_id}", json={"quantity": 5})
    db = TestingSessionLocal()
    hist_count4 = db.query(ShoppingHistory).count()
    db.close()
    assert hist_count4 == 1


# 10. API COMPARISON: /parse (non-mutating) vs /execute (mutating)
def test_api_parse_vs_execute_behavior(client):
    cmd = "Add 2 bottles of milk"

    # /parse should NEVER mutate database
    parse_res = client.post("/api/v1/voice/parse", json={"text": cmd})
    assert parse_res.status_code == 200
    assert parse_res.json()["intent"] == "ADD_ITEM"

    items_after_parse = client.get("/api/v1/items").json()
    assert len(items_after_parse) == 0

    # /execute SHOULD mutate database for valid commands
    exec_res = client.post("/api/v1/voice/execute", json={"text": cmd})
    assert exec_res.status_code == 200
    assert exec_res.json()["success"] is True

    items_after_exec = client.get("/api/v1/items").json()
    assert len(items_after_exec) == 1
    assert items_after_exec[0]["item_name"] == "milk"
