import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from tests.conftest import TestingSessionLocal
from app.models.product import Product
from app.models.shopping_list import ListItem
from app.models.order import Order, OrderItem
from app.models.history import ShoppingHistory

def get_test_db():
    return TestingSessionLocal()

# ============================================================
# PART 7 — ENGLISH TEST MATRIX
# ============================================================

def test_1_empty_checkout_rejected(client: TestClient):
    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 400
    assert "empty" in resp.json()["detail"].lower()

def test_2_add_milk_checkout_success(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})
    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_number"].startswith("ORD-")
    assert data["total"] > 0
    assert len(data["items"]) == 1
    assert data["items"][0]["product_name_snapshot"] == "Whole Milk"

def test_3_add_eggs_checkout_success(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "eggs", "quantity": 1.0})
    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["product_name_snapshot"] == "Eggs"

def test_4_add_milk_eggs_bread_3_item_checkout(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})
    client.post("/api/v1/items", json={"item_name": "eggs", "quantity": 1.0})
    client.post("/api/v1/items", json={"item_name": "whole wheat bread", "quantity": 1.0})

    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    names = {i["product_name_snapshot"] for i in data["items"]}
    assert names == {"Whole Milk", "Eggs", "Whole Wheat Bread"}

def test_5_quantity_2_bottles_of_milk(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 2.0, "unit": "bottles"})
    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 200
    data = resp.json()
    item = data["items"][0]
    assert item["quantity"] == 2.0
    assert item["unit"] == "bottles"
    assert item["line_total"] == round(2.0 * item["unit_price"], 2)

def test_6_quantity_3_eggs(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "eggs", "quantity": 3.0})
    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 200
    data = resp.json()
    item = data["items"][0]
    assert item["quantity"] == 3.0
    assert item["line_total"] == round(3.0 * item["unit_price"], 2)

def test_7_multiple_quantities_milk_and_apples(client: TestClient):
    client.post("/api/v1/voice/execute", json={"text": "add 2 bottles of milk and 3 apples"})
    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    for item in data["items"]:
        assert item["line_total"] == round(item["quantity"] * item["unit_price"], 2)

def test_8_duplicate_merging_checkout(client: TestClient):
    client.post("/api/v1/voice/execute", json={"text": "add milk"})
    client.post("/api/v1/voice/execute", json={"text": "add 2 milk"})

    # Check list has single merged item with qty 3
    list_items = client.get("/api/v1/items").json()
    assert len(list_items) == 1
    assert list_items[0]["quantity"] == 3.0

    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 3.0

def test_10_13_price_validation_and_preview(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 2.0})
    client.post("/api/v1/items", json={"item_name": "eggs", "quantity": 1.0})

    prev = client.get("/api/v1/checkout/preview").json()
    assert prev["item_count"] == 2
    assert prev["has_unavailable"] is False
    subtotal = sum(i["line_total"] for i in prev["items"])
    assert prev["subtotal"] == round(subtotal, 2)
    assert prev["total"] == prev["subtotal"]

    # Verify preview does not mutate DB
    assert len(client.get("/api/v1/orders").json()) == 0

def test_14_17_checkout_unavailable_product_rejected(client: TestClient):
    # Greek Yogurt is marked is_available=False in SEED_PRODUCTS
    client.post("/api/v1/items", json={"item_name": "greek yogurt", "quantity": 1.0})

    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 400
    assert "unavailable" in resp.json()["detail"].lower()

    # Verify zero orders created and shopping list unchanged
    assert len(client.get("/api/v1/orders").json()) == 0
    assert len([i for i in client.get("/api/v1/items").json() if not i.get("is_completed")]) == 1

def test_19_21_valid_and_unavailable_mixed_atomicity(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})
    client.post("/api/v1/items", json={"item_name": "sparkling water", "quantity": 1.0})

    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 400

    # Zero order records created
    assert len(client.get("/api/v1/orders").json()) == 0

def test_22_28_successful_transaction_snapshots(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 2.0})
    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 200

    assert len(client.get("/api/v1/orders").json()) == 1
    assert len([i for i in client.get("/api/v1/items").json() if not i.get("is_completed")]) == 0

def test_31_32_order_history_endpoints(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})
    placed = client.post("/api/v1/checkout").json()

    orders = client.get("/api/v1/orders").json()
    assert len(orders) == 1
    assert orders[0]["order_number"] == placed["order_number"]

    order_details = client.get(f"/api/v1/orders/{placed['id']}").json()
    assert order_details["id"] == placed["id"]
    assert len(order_details["items"]) == 1


# ============================================================
# PART 8 — ENGLISH NATURAL VOICE TESTS & CONFIRMATION
# ============================================================

@pytest.mark.parametrize("phrase", [
    "checkout",
    "check out",
    "place my order",
    "I want to checkout",
    "buy everything on my list",
    "how much is my cart",
    "what's my total",
    "show me checkout"
])
def test_english_voice_checkout_requires_confirmation(client: TestClient, phrase: str):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})

    # Step 1: Trigger checkout prompt
    res1 = client.post("/api/v1/voice/execute", json={"text": phrase, "session_id": "sess-en-1"}).json()
    assert res1["success"] is True
    assert res1["intent"] == "CHECKOUT"
    assert ("total" in res1["message"].lower() or "order" in res1["message"].lower() or "cart" in res1["message"].lower() or "checkout" in res1["message"].lower())

    # Verify no order created yet
    assert len(client.get("/api/v1/orders").json()) == 0

    # Step 2: Confirm order
    res2 = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": "sess-en-1"}).json()
    assert res2["success"] is True
    assert res2["intent"] == "CONFIRM_ORDER"
    assert "Order #" in res2["message"]

    assert len(client.get("/api/v1/orders").json()) == 1

def test_english_voice_checkout_cancellation(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})

    client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": "sess-cancel-1"})
    res2 = client.post("/api/v1/voice/execute", json={"text": "no", "session_id": "sess-cancel-1"}).json()
    assert res2["success"] is True
    assert res2["intent"] == "CANCEL_ORDER"
    assert "cancelled" in res2["message"].lower()

    assert len(client.get("/api/v1/orders").json()) == 0

def test_voice_checkout_non_confirmation_does_not_place_order(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})

    client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": "sess-maybe-1"})
    res2 = client.post("/api/v1/voice/execute", json={"text": "maybe", "session_id": "sess-maybe-1"}).json()

    assert len(client.get("/api/v1/orders").json()) == 0

def test_cart_mutation_invalidates_pending_confirmation(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})
    client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": "sess-mutate-1"})

    # Mutate cart by adding eggs
    client.post("/api/v1/voice/execute", json={"text": "add eggs", "session_id": "sess-mutate-1"})

    # Attempting "yes" should reject stale confirmation
    res_confirm = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": "sess-mutate-1"}).json()
    assert res_confirm["success"] is False
    assert "changed" in res_confirm["message"].lower() or "no pending" in res_confirm["message"].lower()

    assert len(client.get("/api/v1/orders").json()) == 0


# ============================================================
# PART 9 & 10 — MALAYALAM TEST MATRIX
# ============================================================

def test_malayalam_voice_checkout_flow(client: TestClient):
    # Add Malayalam item "രണ്ട് കുപ്പി പാൽ ചേർക്കൂ"
    res_add = client.post("/api/v1/voice/execute", json={"text": "രണ്ട് കുപ്പി പാൽ ചേർക്കൂ", "language": "ml-IN"}).json()
    assert res_add["success"] is True

    # Checkout "checkout ചെയ്യൂ"
    res_chk = client.post("/api/v1/voice/execute", json={
        "text": "checkout ചെയ്യൂ",
        "language": "ml-IN",
        "session_id": "sess-ml-1"
    }).json()
    assert res_chk["success"] is True
    assert res_chk["intent"] == "CHECKOUT"

    # Confirm "അതെ"
    res_conf = client.post("/api/v1/voice/execute", json={
        "text": "അതെ",
        "language": "ml-IN",
        "session_id": "sess-ml-1"
    }).json()
    assert res_conf["success"] is True
    assert res_conf["intent"] == "CONFIRM_ORDER"

    assert len(client.get("/api/v1/orders").json()) == 1

def test_malayalam_compound_command_and_checkout(client: TestClient):
    # "പാൽ, ബ്രെഡ്, മുട്ട ചേർക്കൂ"
    client.post("/api/v1/voice/execute", json={"text": "പാൽ, ബ്രെഡ്, മുട്ട ചേർക്കൂ", "language": "ml-IN"})
    list_items = client.get("/api/v1/items").json()
    assert len(list_items) == 3

    resp = client.post("/api/v1/checkout")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 3


# ============================================================
# PART 12 — NEGATION SAFETY
# ============================================================

@pytest.mark.parametrize("negation_phrase", [
    "don't checkout",
    "do not place my order",
    "I don't want to buy these"
])
def test_negation_checkout_safety(client: TestClient, negation_phrase: str):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})
    res = client.post("/api/v1/voice/execute", json={"text": negation_phrase}).json()

    assert len(client.get("/api/v1/orders").json()) == 0


# ============================================================
# PART 18 — CATALOG REGRESSION ACROSS CATEGORIES
# ============================================================

@pytest.mark.parametrize("query,expected_category", [
    ("milk", "dairy"),
    ("eggs", "dairy"),
    ("apples", "fruits"),
    ("potatoes", "vegetables"),
    ("rice", "grains"),
    ("chickpeas", "pulses"),
    ("bread", "bakery"),
    ("chips", "snacks"),
    ("water", "beverages"),
    ("salt", "spices"),
    ("frozen", "frozen"),
    ("chicken", "meat"),
    ("soap", "personal care"),
    ("laundry", "household"),
    ("diapers", "baby"),
    ("dog food", "pet")
])
def test_catalog_category_search_regression(client: TestClient, query: str, expected_category: str):
    res = client.get(f"/api/v1/products?query={query}").json()
    assert len(res) > 0, f"Query '{query}' returned 0 products"


# ============================================================
# NATURAL CHECKOUT NLP VARIATIONS & CURRENCY TESTS
# ============================================================

@pytest.mark.parametrize("checkout_phrase", [
    "checkout",
    "check out",
    "place the order",
    "place my order",
    "place an order",
    "I want to place the order",
    "I want to place my order",
    "I want to checkout",
    "I'd like to place an order",
    "I would like to place an order",
    "please place the order",
    "please checkout",
    "can you place the order",
    "could you place my order",
    "proceed to checkout",
    "complete my order",
    "finish my order",
    "buy everything in my cart",
    "buy everything on my list",
    "order everything",
    "order my groceries",
    "let's checkout",
    "I'm ready to checkout"
])
def test_english_natural_checkout_phrases(client: TestClient, checkout_phrase: str):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})
    res = client.post("/api/v1/voice/execute", json={"text": checkout_phrase}).json()
    assert res["success"] is True
    assert res["intent"] == "CHECKOUT"
    assert "₹" in res["message"]
    assert "$" not in res["message"]


@pytest.mark.parametrize("ml_checkout_phrase", [
    "checkout ചെയ്യൂ",
    "checkout ചെയ്യണം",
    "order place ചെയ്യൂ",
    "എന്റെ order place ചെയ്യൂ",
    "എന്റെ ഓർഡർ പ്ലേസ് ചെയ്യൂ",
    "ഓർഡർ ചെയ്യൂ",
    "ഓർഡർ place ചെയ്യണം",
    "എന്റെ ഓർഡർ ഇടൂ",
    "എന്റെ cart checkout ചെയ്യൂ",
    "എന്റെ order place ചെയ്യണം",
    "എന്റെ groceries order ചെയ്യൂ"
])
def test_malayalam_natural_checkout_phrases(client: TestClient, ml_checkout_phrase: str):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})
    res = client.post("/api/v1/voice/execute", json={"text": ml_checkout_phrase, "language": "ml-IN"}).json()
    assert res["success"] is True
    assert res["intent"] == "CHECKOUT"
    assert "₹" in res["message"]


@pytest.mark.parametrize("neg_phrase", [
    "don't checkout",
    "do not checkout",
    "don't place the order",
    "do not place the order",
    "I don't want to checkout"
])
def test_negation_checkout_safety_extended(client: TestClient, neg_phrase: str):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})
    res = client.post("/api/v1/voice/execute", json={"text": neg_phrase}).json()
    assert len(client.get("/api/v1/orders").json()) == 0


def test_checkout_confirmation_separation_and_currency(client: TestClient):
    client.post("/api/v1/items", json={"item_name": "whole milk", "quantity": 1.0})

    # "place the order" returns CHECKOUT, not CONFIRM_ORDER
    res_chk = client.post("/api/v1/voice/execute", json={"text": "place the order", "session_id": "sess-sep-1"}).json()
    assert res_chk["intent"] == "CHECKOUT"
    assert "₹" in res_chk["message"]
    assert len(client.get("/api/v1/orders").json()) == 0

    # "yes" places order
    res_conf = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": "sess-sep-1"}).json()
    assert res_conf["intent"] == "CONFIRM_ORDER"
    assert "₹" in res_conf["message"]
    assert len(client.get("/api/v1/orders").json()) == 1

    # Repeat "yes" rejects duplicate placement
    res_repeat = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": "sess-sep-1"}).json()
    assert res_repeat["success"] is False
    assert len(client.get("/api/v1/orders").json()) == 1
