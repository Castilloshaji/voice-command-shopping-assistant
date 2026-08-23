import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.product import Product
from app.models.shopping_list import ListItem
from app.models.history import ShoppingHistory
from app.models.order import Order, OrderItem
from app.models import Base
from app.main import app
from app.core.database import get_db
from app.core.seed_data import seed_products

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


persistent_connection = engine.connect()

@pytest.fixture(scope="function")
def client():
    Base.metadata.drop_all(bind=persistent_connection)
    Base.metadata.create_all(bind=persistent_connection)

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
