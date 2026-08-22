import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_db
from app.models import Base
from app.core.seed_data import seed_products

# Use StaticPool so all threads/sessions share the exact same SQLite in-memory DB instance
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def client():
    # Re-create all tables in the in-memory database for an isolated test environment
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Seed product catalog into testing DB
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


def test_1_get_empty_shopping_list(client):
    """1. GET empty shopping list"""
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    assert response.json() == []


def test_2_add_item(client):
    """2. Add item (basic)"""
    response = client.post("/api/v1/items", json={"item_name": "milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["item_name"] == "milk"
    assert data["category"] == "dairy"
    assert data["quantity"] == 1.0
    assert data["is_completed"] is False


def test_3_add_item_with_quantity_and_unit(client):
    """3. Add item with quantity and unit"""
    payload = {
        "item_name": "orange juice",
        "quantity": 3.5,
        "unit": "cartons"
    }
    response = client.post("/api/v1/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["item_name"] == "orange juice"
    assert data["quantity"] == 3.5
    assert data["unit"] == "cartons"
    assert data["category"] == "beverages"


def test_4_automatic_categorization(client):
    """4. Automatic categorization (fallback dictionary without exact product catalog match)"""
    # 'bread' matches keyword in dictionary -> bakery
    resp1 = client.post("/api/v1/items", json={"item_name": "bread"})
    assert resp1.status_code == 201
    assert resp1.json()["category"] == "bakery"

    # 'chips' matches keyword in dictionary -> snacks
    resp2 = client.post("/api/v1/items", json={"item_name": "potato chips"})
    assert resp2.status_code == 201
    assert resp2.json()["category"] == "snacks"


def test_5_product_matching(client):
    """5. Product matching (associates product_id and inherits category from catalog)"""
    # 'Whole Milk' is in seed product catalog
    response = client.post("/api/v1/items", json={"item_name": "Whole Milk", "quantity": 2, "unit": "bottles"})
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] is not None
    assert data["category"] == "dairy"
    assert data["quantity"] == 2.0
    assert data["unit"] == "bottles"

    # Arbitrary non-catalog item
    response_unknown = client.post("/api/v1/items", json={"item_name": "mysterious item 123"})
    assert response_unknown.status_code == 201
    data_unknown = response_unknown.json()
    assert data_unknown["product_id"] is None
    assert data_unknown["category"] == "general"


def test_6_update_quantity(client):
    """6. Update quantity"""
    create_res = client.post("/api/v1/items", json={"item_name": "apples", "quantity": 1})
    assert create_res.status_code == 201
    item_id = create_res.json()["id"]

    update_res = client.put(f"/api/v1/items/{item_id}", json={"quantity": 5.0})
    assert update_res.status_code == 200
    assert update_res.json()["quantity"] == 5.0
    assert update_res.json()["item_name"] == "apples"


def test_7_update_completion_status(client):
    """7. Update completion status"""
    create_res = client.post("/api/v1/items", json={"item_name": "paper towels"})
    assert create_res.status_code == 201
    item_id = create_res.json()["id"]
    assert create_res.json()["is_completed"] is False

    update_res = client.put(f"/api/v1/items/{item_id}", json={"is_completed": True})
    assert update_res.status_code == 200
    assert update_res.json()["is_completed"] is True


def test_8_delete_item(client):
    """8. Delete item"""
    create_res = client.post("/api/v1/items", json={"item_name": "bananas"})
    assert create_res.status_code == 201
    item_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/items/{item_id}")
    assert del_res.status_code == 200
    assert del_res.json()["id"] == item_id

    # Verify list is empty
    get_res = client.get("/api/v1/items")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 0


def test_9_request_validation(client):
    """9. Request validation"""
    # Empty item_name
    res_empty_name = client.post("/api/v1/items", json={"item_name": "   "})
    assert res_empty_name.status_code == 422

    # Negative quantity
    res_neg_qty = client.post("/api/v1/items", json={"item_name": "milk", "quantity": -2})
    assert res_neg_qty.status_code == 422

    # Zero quantity
    res_zero_qty = client.post("/api/v1/items", json={"item_name": "milk", "quantity": 0})
    assert res_zero_qty.status_code == 422


def test_10_item_not_found_behavior(client):
    """10. Item-not-found behavior"""
    res_update_404 = client.put("/api/v1/items/99999", json={"quantity": 10})
    assert res_update_404.status_code == 404
    assert "not found" in res_update_404.json()["detail"].lower()

    res_delete_404 = client.delete("/api/v1/items/99999")
    assert res_delete_404.status_code == 404
    assert "not found" in res_delete_404.json()["detail"].lower()


def test_11_no_duplicate_history_on_redundant_completion(client):
    """11. Verify duplicate completion updates (True -> True) do not create duplicate ShoppingHistory events."""
    from app.models.history import ShoppingHistory

    create_res = client.post("/api/v1/items", json={"item_name": "organic apples"})
    item_id = create_res.json()["id"]

    # First completion update (False -> True)
    up1 = client.put(f"/api/v1/items/{item_id}", json={"is_completed": True})
    assert up1.status_code == 200

    # Second completion update (True -> True)
    up2 = client.put(f"/api/v1/items/{item_id}", json={"is_completed": True})
    assert up2.status_code == 200

    # Verify directly from DB session via override
    db = TestingSessionLocal()
    history_records = db.query(ShoppingHistory).filter(ShoppingHistory.item_name == "organic apples").all()
    assert len(history_records) == 1
    db.close()

