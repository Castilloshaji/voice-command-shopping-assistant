import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.intent import IntentEnum

client = TestClient(app)


def test_conversational_add_to_then_packet_of_yoghurt():
    """
    Test 1: 'add to milk then add to strawberries then add a packet of yoghurt'
    Expected:
    [
        milk (1.0, None),
        strawberries (1.0, None),
        yoghurt (1.0, "packets")
    ]
    """
    text = "add to milk then add to strawberries then add a packet of yoghurt"
    res = client.post("/api/v1/voice/parse", json={"text": text})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert "items" in data and data["items"] is not None
    assert len(data["items"]) == 3

    assert data["items"][0]["item"] == "milk"
    assert data["items"][0]["quantity"] == 1.0
    assert data["items"][0]["unit"] is None

    assert data["items"][1]["item"] == "strawberries"
    assert data["items"][1]["quantity"] == 1.0
    assert data["items"][1]["unit"] is None

    assert data["items"][2]["item"] == "yoghurt"
    assert data["items"][2]["quantity"] == 1.0
    assert data["items"][2]["unit"] == "packets"


def test_conversational_then_boundary():
    """Test 2: 'add milk then add bread'."""
    res = client.post("/api/v1/voice/parse", json={"text": "add milk then add bread"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2
    assert [i["item"] for i in data["items"]] == ["milk", "bread"]


def test_conversational_and_then():
    """Test 3: 'add milk and then add bread'."""
    res = client.post("/api/v1/voice/parse", json={"text": "add milk and then add bread"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2
    assert [i["item"] for i in data["items"]] == ["milk", "bread"]


def test_conversational_add_to_and_then():
    """Test 4: 'add to milk and then add to bread'."""
    res = client.post("/api/v1/voice/parse", json={"text": "add to milk and then add to bread"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2
    assert [i["item"] for i in data["items"]] == ["milk", "bread"]


def test_conversational_quantities_then():
    """Test 5: 'add 2 bottles of milk then add 3 apples'."""
    res = client.post("/api/v1/voice/parse", json={"text": "add 2 bottles of milk then add 3 apples"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2

    assert data["items"][0]["item"] == "milk"
    assert data["items"][0]["quantity"] == 2.0
    assert data["items"][0]["unit"] == "bottles"

    assert data["items"][1]["item"] == "apples"
    assert data["items"][1]["quantity"] == 3.0
    assert data["items"][1]["unit"] is None


def test_conversational_buy_then():
    """Test 6: 'buy milk then buy bread'."""
    res = client.post("/api/v1/voice/parse", json={"text": "buy milk then buy bread"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2
    assert [i["item"] for i in data["items"]] == ["milk", "bread"]


def test_conversational_comma_then():
    """Test 7: 'add milk, then add strawberries'."""
    res = client.post("/api/v1/voice/parse", json={"text": "add milk, then add strawberries"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2
    assert [i["item"] for i in data["items"]] == ["milk", "strawberries"]


def test_existing_repeated_verbs():
    """Test 8: 'add milk add strawberries and yoghurt'."""
    res = client.post("/api/v1/voice/parse", json={"text": "add milk add strawberries and yoghurt"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 3
    assert [i["item"] for i in data["items"]] == ["milk", "strawberries", "yoghurt"]


def test_existing_add_two_items():
    """Test 9: 'add milk and bread'."""
    res = client.post("/api/v1/voice/parse", json={"text": "add milk and bread"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2
    assert [i["item"] for i in data["items"]] == ["milk", "bread"]


def test_existing_quantities_and_units():
    """Test 10: 'add 2 bottles of milk and 3 apples'."""
    res = client.post("/api/v1/voice/parse", json={"text": "add 2 bottles of milk and 3 apples"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 2
    assert data["items"][0]["item"] == "milk"
    assert data["items"][0]["quantity"] == 2.0
    assert data["items"][0]["unit"] == "bottles"
    assert data["items"][1]["item"] == "apples"
    assert data["items"][1]["quantity"] == 3.0
    assert data["items"][1]["unit"] is None


def test_malayalam_single_item():
    """Test 11: Malayalam single-item command 'രണ്ട് കുപ്പി പാൽ ചേർക്കൂ'."""
    res = client.post("/api/v1/voice/parse", json={"text": "രണ്ട് കുപ്പി പാൽ ചേർക്കൂ"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert data["item"] == "milk"
    assert data["quantity"] == 2.0
    assert data["unit"] == "bottles"


def test_malayalam_compound_command():
    """Test 12: Malayalam compound command 'പാൽ, ബ്രെഡ്, മുട്ട ചേർക്കൂ'."""
    res = client.post("/api/v1/voice/parse", json={"text": "പാൽ, ബ്രെഡ്, മുട്ട ചേർക്കൂ"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert len(data["items"]) == 3
    assert [i["item"] for i in data["items"]] == ["milk", "bread", "eggs"]


def test_conversational_execution_and_database_verification():
    """
    Verify POST /api/v1/voice/execute for problematic command:
    'add to milk then add to strawberries then add a packet of yoghurt'
    Verify database contains 3 clean items without filler words ('to milk then', etc.).
    """
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    text = "add to milk then add to strawberries then add a packet of yoghurt"
    exec_res = client.post("/api/v1/voice/execute", json={"text": text})
    assert exec_res.status_code == 200
    assert exec_res.json()["success"] is True

    items_res = client.get("/api/v1/items")
    assert items_res.status_code == 200
    items = items_res.json()
    assert len(items) == 3

    item_names = [i["item_name"] for i in items]
    assert "to milk then" not in item_names
    assert "to strawberries then" not in item_names
    assert "milk then" not in item_names
    assert set(item_names) == {"milk", "strawberries", "yoghurt"}

    items_map = {i["item_name"]: i for i in items}
    assert items_map["milk"]["quantity"] == 1.0
    assert items_map["milk"]["unit"] is None

    assert items_map["strawberries"]["quantity"] == 1.0
    assert items_map["strawberries"]["unit"] is None

    assert items_map["yoghurt"]["quantity"] == 1.0
    assert items_map["yoghurt"]["unit"] == "packets"


def test_conversational_duplicate_quantity_merging():
    """Verify duplicate quantity merging still works for conversational speech commands."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    client.post("/api/v1/voice/execute", json={"text": "add 2 bottles of milk"})
    client.post("/api/v1/voice/execute", json={"text": "add to milk and then add to bread"})

    items = client.get("/api/v1/items").json()
    assert len(items) == 2
    items_map = {i["item_name"]: i for i in items}
    assert items_map["milk"]["quantity"] == 3.0
    assert items_map["bread"]["quantity"] == 1.0


# =====================================================================
# Catalog-Aware Compound Voice Parsing Fallback Tests
# =====================================================================

def test_catalog_aware_compound_milk_strawberry_yoghurt():
    """
    Test 'add milk strawberry yoghurt':
    Verifies that catalog-aware segmentation splits the single clause into 3 items
    and adds all three cleanly to DB.
    """
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    exec_res = client.post("/api/v1/voice/execute", json={"text": "add milk strawberry yoghurt"})
    assert exec_res.status_code == 200
    assert exec_res.json()["success"] is True

    items = client.get("/api/v1/items").json()
    assert len(items) == 3
    names = {i["item_name"] for i in items}
    assert "milk" in names
    assert any(n in names for n in ["strawberries", "strawberry"])
    assert any(n in names for n in ["yoghurt", "yogurt"])


def test_catalog_aware_compound_milk_bread_bananas():
    """Test 'add milk bread bananas' creates 3 items."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    exec_res = client.post("/api/v1/voice/execute", json={"text": "add milk bread bananas"})
    assert exec_res.status_code == 200
    assert exec_res.json()["success"] is True

    items = client.get("/api/v1/items").json()
    assert len(items) == 3
    names = {i["item_name"] for i in items}
    assert names == {"milk", "bread", "bananas"}


def test_catalog_aware_compound_milk_and_strawberry_yoghurt():
    """Test 'add milk and strawberry yoghurt' creates 3 items."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    exec_res = client.post("/api/v1/voice/execute", json={"text": "add milk and strawberry yoghurt"})
    assert exec_res.status_code == 200
    assert exec_res.json()["success"] is True

    items = client.get("/api/v1/items").json()
    assert len(items) == 3


def test_catalog_aware_compound_quantities_without_conjunctions():
    """Test 'add 2 bottles of milk 3 apples' extracts quantities and units per item."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    exec_res = client.post("/api/v1/voice/execute", json={"text": "add 2 bottles of milk 3 apples"})
    assert exec_res.status_code == 200
    assert exec_res.json()["success"] is True

    items = client.get("/api/v1/items").json()
    assert len(items) == 2
    items_map = {i["item_name"]: i for i in items}
    assert items_map["milk"]["quantity"] == 2.0
    assert items_map["milk"]["unit"] == "bottles"
    assert items_map["apples"]["quantity"] == 3.0
    assert items_map["apples"]["unit"] is None


def test_catalog_aware_compound_atomicity_single_invalid():
    """
    CRITICAL ATOMICITY TEST:
    Verify 'add milk somethingrandom' fails completely (success=False) and creates ZERO items.
    """
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    exec_res = client.post("/api/v1/voice/execute", json={"text": "add milk somethingrandom"})
    assert exec_res.status_code == 200
    e_data = exec_res.json()

    assert e_data["success"] is False

    # Atomicity check: 0 items added
    items = client.get("/api/v1/items").json()
    assert len(items) == 0


def test_catalog_aware_compound_atomicity_multiple_invalid():
    """
    CRITICAL ATOMICITY TEST:
    Verify 'add milk strawberry unknownitem' creates ZERO items.
    """
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    exec_res = client.post("/api/v1/voice/execute", json={"text": "add milk strawberry unknownitem"})
    assert exec_res.status_code == 200
    assert exec_res.json()["success"] is False

    items = client.get("/api/v1/items").json()
    assert len(items) == 0


# =====================================================================
# Catalog Validation Safety Layer Tests
# =====================================================================

def test_catalog_validation_add_2_minutes():
    """
    CRITICAL REGRESSION TEST:
    Verify 'add 2 minutes' returns success=False, does NOT mutate DB,
    and returns a clean non-addition message.
    """
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})
    initial_items = client.get("/api/v1/items").json()
    assert len(initial_items) == 0

    exec_res = client.post("/api/v1/voice/execute", json={"text": "add 2 minutes"})
    assert exec_res.status_code == 200
    e_data = exec_res.json()

    assert e_data["success"] is False
    assert "I couldn't find 'minutes'" in e_data["message"] or "I couldn't identify" in e_data["message"]
    assert "data" in e_data and e_data["data"] is not None
    assert "unrecognized_items" in e_data["data"]
    assert e_data["data"]["unrecognized_items"] == ["minutes"]

    # Verify ZERO database mutation
    after_items = client.get("/api/v1/items").json()
    assert len(after_items) == 0
    item_names = [i["item_name"] for i in after_items]
    assert "minutes" not in item_names


def test_catalog_validation_compound_one_invalid():
    """
    Verify compound command 'add 2 bottles of milk and 3 minutes'
    fails atomically: NOTHING is added to DB.
    """
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    exec_res = client.post("/api/v1/voice/execute", json={"text": "add 2 bottles of milk and 3 minutes"})
    assert exec_res.status_code == 200
    e_data = exec_res.json()

    assert e_data["success"] is False
    assert "minutes" in e_data["data"]["unrecognized_items"]

    # Atomic validation: NO item created in DB
    items_after = client.get("/api/v1/items").json()
    assert len(items_after) == 0


def test_catalog_validation_compound_multiple_invalid():
    """Verify 'add unknownproduct and anotherunknown' fails atomically."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    exec_res = client.post("/api/v1/voice/execute", json={"text": "add unknownproduct and anotherunknown"})
    assert exec_res.status_code == 200
    e_data = exec_res.json()

    assert e_data["success"] is False
    items_after = client.get("/api/v1/items").json()
    assert len(items_after) == 0


def test_catalog_validation_valid_compound_command():
    """Verify 'add 2 bottles of milk and 3 apples' succeeds and adds both."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    exec_res = client.post("/api/v1/voice/execute", json={"text": "add 2 bottles of milk and 3 apples"})
    assert exec_res.status_code == 200
    assert exec_res.json()["success"] is True

    items = client.get("/api/v1/items").json()
    assert len(items) == 2
    names = {i["item_name"] for i in items}
    assert names == {"milk", "apples"}
