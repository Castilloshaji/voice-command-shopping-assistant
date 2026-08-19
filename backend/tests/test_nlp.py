import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.intent import IntentEnum

client = TestClient(app)

def test_nlp_add_item_variations():
    """Test ADD_ITEM parsing variations and entity extractions."""
    # 1. Basic add item
    res1 = client.post("/api/v1/voice/parse", json={"text": "Add milk"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["intent"] == IntentEnum.ADD_ITEM
    assert d1["item"] == "milk"
    assert d1["quantity"] == 1.0
    assert d1["unit"] is None

    # 2. "I need milk"
    res2 = client.post("/api/v1/voice/parse", json={"text": "I need milk"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["intent"] == IntentEnum.ADD_ITEM
    assert d2["item"] == "milk"
    assert d2["quantity"] == 1.0

    # 3. "I want to buy bananas"
    res3 = client.post("/api/v1/voice/parse", json={"text": "I want to buy bananas"})
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["intent"] == IntentEnum.ADD_ITEM
    assert d3["item"] == "bananas"

    # 4. "Add 2 bottles of milk"
    res4 = client.post("/api/v1/voice/parse", json={"text": "Add 2 bottles of milk"})
    assert res4.status_code == 200
    d4 = res4.json()
    assert d4["intent"] == IntentEnum.ADD_ITEM
    assert d4["item"] == "milk"
    assert d4["quantity"] == 2.0
    assert d4["unit"] == "bottles"

    # 5. "Add 5 oranges"
    res5 = client.post("/api/v1/voice/parse", json={"text": "Add 5 oranges"})
    assert res5.status_code == 200
    d5 = res5.json()
    assert d5["intent"] == IntentEnum.ADD_ITEM
    assert d5["item"] == "oranges"
    assert d5["quantity"] == 5.0

    # 6. Number words: "three cartons of orange juice"
    res6 = client.post("/api/v1/voice/parse", json={"text": "Add three cartons of orange juice"})
    assert res6.status_code == 200
    d6 = res6.json()
    assert d6["intent"] == IntentEnum.ADD_ITEM
    assert d6["item"] == "orange juice"
    assert d6["quantity"] == 3.0
    assert d6["unit"] == "cartons"


def test_nlp_remove_item_variations():
    """Test REMOVE_ITEM parsing variations."""
    # 1. "Remove milk"
    res1 = client.post("/api/v1/voice/parse", json={"text": "Remove milk"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["intent"] == IntentEnum.REMOVE_ITEM
    assert d1["item"] == "milk"

    # 2. "Delete apples from my list"
    res2 = client.post("/api/v1/voice/parse", json={"text": "Delete apples from my list"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["intent"] == IntentEnum.REMOVE_ITEM
    assert d2["item"] == "apples"

    # 3. "I don't need milk anymore"
    res3 = client.post("/api/v1/voice/parse", json={"text": "I don't need milk anymore"})
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["intent"] == IntentEnum.REMOVE_ITEM
    assert d3["item"] == "milk"


def test_nlp_update_quantity_variations():
    """Test UPDATE_QUANTITY parsing variations."""
    # 1. "Change milk quantity to 3"
    res1 = client.post("/api/v1/voice/parse", json={"text": "Change milk quantity to 3"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["intent"] == IntentEnum.UPDATE_QUANTITY
    assert d1["item"] == "milk"
    assert d1["quantity"] == 3.0

    # 2. "Set apples to 5"
    res2 = client.post("/api/v1/voice/parse", json={"text": "Set apples to 5"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["intent"] == IntentEnum.UPDATE_QUANTITY
    assert d2["item"] == "apples"
    assert d2["quantity"] == 5.0

    # 3. "I need 6 oranges instead"
    res3 = client.post("/api/v1/voice/parse", json={"text": "I need 6 oranges instead"})
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["intent"] == IntentEnum.UPDATE_QUANTITY
    assert d3["item"] == "oranges"
    assert d3["quantity"] == 6.0


def test_nlp_search_product_variations():
    """Test SEARCH_PRODUCT parsing with price and brand filters."""
    # 1. "Find organic apples"
    res1 = client.post("/api/v1/voice/parse", json={"text": "Find organic apples"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["intent"] == IntentEnum.SEARCH_PRODUCT
    assert d1["item"] == "organic apples"

    # 2. "Find toothpaste under $5"
    res2 = client.post("/api/v1/voice/parse", json={"text": "Find toothpaste under $5"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["intent"] == IntentEnum.SEARCH_PRODUCT
    assert d2["item"] == "toothpaste"
    assert d2["max_price"] == 5.0

    # 3. "Find Coke under $3"
    res3 = client.post("/api/v1/voice/parse", json={"text": "Find Coke under $3"})
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["intent"] == IntentEnum.SEARCH_PRODUCT
    assert d3["item"] == "coke"
    assert d3["max_price"] == 3.0

    # 4. "Find Dove toothpaste"
    res4 = client.post("/api/v1/voice/parse", json={"text": "Find Dove toothpaste"})
    assert res4.status_code == 200
    d4 = res4.json()
    assert d4["intent"] == IntentEnum.SEARCH_PRODUCT
    assert d4["brand"] == "Dove"
    assert d4["item"] == "toothpaste"

    # 5. "toothpaste from Dove"
    res5 = client.post("/api/v1/voice/parse", json={"text": "Find toothpaste from Dove"})
    assert res5.status_code == 200
    d5 = res5.json()
    assert d5["intent"] == IntentEnum.SEARCH_PRODUCT
    assert d5["brand"] == "Dove"
    assert d5["item"] == "toothpaste"

    # 6. "Find products between $5 and $10"
    res6 = client.post("/api/v1/voice/parse", json={"text": "Find products between $5 and $10"})
    assert res6.status_code == 200
    d6 = res6.json()
    assert d6["intent"] == IntentEnum.SEARCH_PRODUCT
    assert d6["min_price"] == 5.0
    assert d6["max_price"] == 10.0


def test_nlp_show_list_variations():
    """Test SHOW_LIST intent recognition."""
    res1 = client.post("/api/v1/voice/parse", json={"text": "Show my list"})
    assert res1.status_code == 200
    assert res1.json()["intent"] == IntentEnum.SHOW_LIST

    res2 = client.post("/api/v1/voice/parse", json={"text": "What is on my shopping list?"})
    assert res2.status_code == 200
    assert res2.json()["intent"] == IntentEnum.SHOW_LIST


def test_nlp_clear_list_variations():
    """Test CLEAR_LIST intent recognition."""
    res1 = client.post("/api/v1/voice/parse", json={"text": "Clear my list"})
    assert res1.status_code == 200
    assert res1.json()["intent"] == IntentEnum.CLEAR_LIST

    res2 = client.post("/api/v1/voice/parse", json={"text": "Delete all items"})
    assert res2.status_code == 200
    assert res2.json()["intent"] == IntentEnum.CLEAR_LIST


def test_nlp_get_suggestions_variations():
    """Test GET_SUGGESTIONS intent recognition."""
    res1 = client.post("/api/v1/voice/parse", json={"text": "What should I buy?"})
    assert res1.status_code == 200
    assert res1.json()["intent"] == IntentEnum.GET_SUGGESTIONS

    res2 = client.post("/api/v1/voice/parse", json={"text": "Give me shopping suggestions"})
    assert res2.status_code == 200
    assert res2.json()["intent"] == IntentEnum.GET_SUGGESTIONS


def test_nlp_unknown_command():
    """Test UNKNOWN intent for random or ambiguous input."""
    res = client.post("/api/v1/voice/parse", json={"text": "What is the weather today in Paris?"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.UNKNOWN
    assert data["confidence"] == 0.0


def test_nlp_normalization_and_punctuation():
    """Test normalization with uppercase, extra spaces, and trailing punctuation."""
    res = client.post("/api/v1/voice/parse", json={"text": "  ADD   2   BOTTLES   OF   MILK!!!  "})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert data["item"] == "milk"
    assert data["quantity"] == 2.0
    assert data["unit"] == "bottles"
    assert data["normalized_text"] == "add 2 bottles of milk"


def test_nlp_endpoint_non_mutating():
    """Verify POST /api/v1/voice/parse performs parse only without mutating shopping list."""
    # Check shopping list before
    items_before = client.get("/api/v1/items").json()

    # Parse destructive command "Delete all items"
    parse_res = client.post("/api/v1/voice/parse", json={"text": "Delete all items"})
    assert parse_res.status_code == 200
    assert parse_res.json()["intent"] == IntentEnum.CLEAR_LIST

    # Check shopping list after - verify list was NOT modified/cleared
    items_after = client.get("/api/v1/items").json()
    assert len(items_after) == len(items_before)
