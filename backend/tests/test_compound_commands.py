import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.intent import IntentEnum

client = TestClient(app)


def test_compound_add_repeated_verbs():
    """Test 'add milk add strawberries and yoghurt' parses into 3 items."""
    res = client.post("/api/v1/voice/parse", json={"text": "add milk add strawberries and yoghurt"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert "items" in data and data["items"] is not None
    assert len(data["items"]) == 3
    item_names = [i["item"] for i in data["items"]]
    assert item_names == ["milk", "strawberries", "yoghurt"]


def test_compound_add_two_items():
    """Test 'add milk and bread' parses into 2 items."""
    res = client.post("/api/v1/voice/parse", json={"text": "add milk and bread"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2
    assert data["items"][0]["item"] == "milk"
    assert data["items"][1]["item"] == "bread"


def test_compound_add_comma_and():
    """Test 'add milk, bread and eggs' parses into 3 items."""
    res = client.post("/api/v1/voice/parse", json={"text": "add milk, bread and eggs"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 3
    assert [i["item"] for i in data["items"]] == ["milk", "bread", "eggs"]


def test_compound_add_quantities_and_units():
    """Test 'add 2 bottles of milk and 3 apples' isolates quantities and units correctly."""
    res = client.post("/api/v1/voice/parse", json={"text": "add 2 bottles of milk and 3 apples"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2
    
    # Item 1: 2 bottles of milk
    assert data["items"][0]["item"] == "milk"
    assert data["items"][0]["quantity"] == 2.0
    assert data["items"][0]["unit"] == "bottles"
    
    # Item 2: 3 apples
    assert data["items"][1]["item"] == "apples"
    assert data["items"][1]["quantity"] == 3.0
    assert data["items"][1]["unit"] is None


def test_compound_buy_verb_with_units():
    """Test 'buy 2 packets of chips and 1 bottle of milk'."""
    res = client.post("/api/v1/voice/parse", json={"text": "buy 2 packets of chips and 1 bottle of milk"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2
    
    assert data["items"][0]["item"] == "chips"
    assert data["items"][0]["quantity"] == 2.0
    assert data["items"][0]["unit"] == "packets"
    
    assert data["items"][1]["item"] == "milk"
    assert data["items"][1]["quantity"] == 1.0
    assert data["items"][1]["unit"] == "bottles"


def test_single_item_backward_compatibility():
    """Test single item commands 'add milk' and 'add 2 bottles of milk' preserve singular fields."""
    res1 = client.post("/api/v1/voice/parse", json={"text": "add milk"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["intent"] == IntentEnum.ADD_ITEM
    assert d1["item"] == "milk"
    assert d1["quantity"] == 1.0
    assert d1["unit"] is None

    res2 = client.post("/api/v1/voice/parse", json={"text": "add 2 bottles of milk"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["intent"] == IntentEnum.ADD_ITEM
    assert d2["item"] == "milk"
    assert d2["quantity"] == 2.0
    assert d2["unit"] == "bottles"


def test_malayalam_compound_and_single_commands():
    """Test Malayalam single and compound commands."""
    # Single item
    res1 = client.post("/api/v1/voice/parse", json={"text": "രണ്ട് കുപ്പി പാൽ ചേർക്കൂ"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["intent"] == IntentEnum.ADD_ITEM
    assert d1["item"] == "milk"
    assert d1["quantity"] == 2.0
    assert d1["unit"] == "bottles"

    # Compound items
    res2 = client.post("/api/v1/voice/parse", json={"text": "പാൽ, ബ്രെഡ്, മുട്ട ചേർക്കൂ"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["intent"] == IntentEnum.ADD_ITEM
    assert len(d2["items"]) == 3
    assert [i["item"] for i in d2["items"]] == ["milk", "bread", "eggs"]


def test_compound_execute_and_duplicate_merging():
    """Verify execution of compound commands and duplicate merging in DB."""
    # 1. Clear shopping list
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    # 2. Add 2 bottles of milk first
    client.post("/api/v1/voice/execute", json={"text": "add 2 bottles of milk"})
    
    items_before = client.get("/api/v1/items").json()
    assert len(items_before) == 1
    assert items_before[0]["item_name"] == "milk"
    assert items_before[0]["quantity"] == 2.0

    # 3. Execute compound command: "add milk and bread"
    exec_res = client.post("/api/v1/voice/execute", json={"text": "add milk and bread"})
    assert exec_res.status_code == 200
    e_data = exec_res.json()
    assert e_data["success"] is True
    assert "milk" in e_data["message"] and "bread" in e_data["message"]

    # 4. Verify DB state: milk quantity incremented to 3.0, bread created with quantity 1.0
    items_after = client.get("/api/v1/items").json()
    assert len(items_after) == 2
    
    items_dict = {i["item_name"]: i for i in items_after}
    assert items_dict["milk"]["quantity"] == 3.0
    assert items_dict["bread"]["quantity"] == 1.0


def test_compound_api_full_flow():
    """Verify POST /api/v1/voice/parse and execute for 'add milk add strawberries and yoghurt'."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    text = "add milk add strawberries and yoghurt"
    parse_res = client.post("/api/v1/voice/parse", json={"text": text})
    assert parse_res.status_code == 200
    p_data = parse_res.json()
    assert p_data["intent"] == IntentEnum.ADD_ITEM
    assert len(p_data["items"]) == 3

    exec_res = client.post("/api/v1/voice/execute", json={"text": text})
    assert exec_res.status_code == 200
    assert exec_res.json()["success"] is True

    items_res = client.get("/api/v1/items")
    assert items_res.status_code == 200
    items = items_res.json()
    assert len(items) == 3
    names = {i["item_name"] for i in items}
    assert names == {"milk", "strawberries", "yoghurt"}
