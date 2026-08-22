import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_db
from app.models import Base
from app.models.product import Product

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
    products = [
        Product(id=1, name="Dove Toothpaste", category="Personal Care", brand="Dove", price=4.50, is_available=True, season="all"),
        Product(id=2, name="Whole Milk", category="Dairy", brand="DairyPure", price=3.99, is_available=True, season="all"),
        Product(id=3, name="Butter Croissant", category="Bakery", brand="BakeryFresh", price=3.99, is_available=False, season="all", substitutes=["Chocolate Croissant"]),
        Product(id=4, name="Chocolate Croissant", category="Bakery", brand="BakeryFresh", price=4.25, is_available=True, season="all"),
    ]
    db.add_all(products)
    db.commit()
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

def test_get_products_endpoint(client):
    response = client.get("/api/v1/products?query=toothpaste")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Dove Toothpaste"

def test_get_products_endpoint_with_substitutes(client):
    response = client.get("/api/v1/products?query=croissant")
    assert response.status_code == 200
    data = response.json()
    butter = next(p for p in data if p["name"] == "Butter Croissant")
    assert butter["is_available"] is False
    assert len(butter["substitute_products"]) == 1
    assert butter["substitute_products"][0]["name"] == "Chocolate Croissant"

def test_get_suggestions_endpoint(client):
    response = client.get("/api/v1/suggestions?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_clear_items_endpoint(client):
    client.post("/api/v1/items", json={"item_name": "Test Milk", "quantity": 1.0})
    items_before = client.get("/api/v1/items").json()
    assert len(items_before) >= 1

    clear_resp = client.delete("/api/v1/items")
    assert clear_resp.status_code == 200
    assert "Cleared all" in clear_resp.json()["message"]

    items_after = client.get("/api/v1/items").json()
    assert len(items_after) == 0
