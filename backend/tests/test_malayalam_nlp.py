import unicodedata
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.intent import IntentEnum
from app.services.nlp_service import NLPService, contains_malayalam

client = TestClient(app)


def test_malayalam_detection_and_normalization():
    """Verify Malayalam Unicode detection and NFC normalization."""
    raw_text = "രണ്ട് കുപ്പി പാൽ ചേർക്കൂ"
    # Create NFD decomposed text
    decomposed = unicodedata.normalize("NFD", raw_text)
    
    assert contains_malayalam(decomposed) is True
    normalized = NLPService.normalize_text(decomposed)
    assert unicodedata.is_normalized("NFC", normalized) is True
    assert normalized == raw_text


def test_malayalam_add_item_exact():
    """Test exact requirement: 'രണ്ട് കുപ്പി പാൽ ചേർക്കൂ'."""
    res = client.post("/api/v1/voice/parse", json={"text": "രണ്ട് കുപ്പി പാൽ ചേർക്കൂ"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.ADD_ITEM
    assert data["item"] == "milk"
    assert data["quantity"] == 2.0
    assert data["unit"] == "bottles"


def test_malayalam_add_item_variations():
    """Test Malayalam ADD_ITEM variations and entity extractions."""
    # 1. "പാൽ വാങ്ങണം"
    res1 = client.post("/api/v1/voice/parse", json={"text": "പാൽ വാങ്ങണം"})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["intent"] == IntentEnum.ADD_ITEM
    assert d1["item"] == "milk"
    assert d1["quantity"] == 1.0
    assert d1["unit"] is None

    # 2. "പാൽ ചേർക്കൂ"
    res2 = client.post("/api/v1/voice/parse", json={"text": "പാൽ ചേർക്കൂ"})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["intent"] == IntentEnum.ADD_ITEM
    assert d2["item"] == "milk"
    assert d2["quantity"] == 1.0
    assert d2["unit"] is None

    # 3. "മൂന്ന് കുപ്പി പാൽ ചേർക്കൂ"
    res3 = client.post("/api/v1/voice/parse", json={"text": "മൂന്ന് കുപ്പി പാൽ ചേർക്കൂ"})
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["intent"] == IntentEnum.ADD_ITEM
    assert d3["item"] == "milk"
    assert d3["quantity"] == 3.0
    assert d3["unit"] == "bottles"


def test_malayalam_remove_item():
    """Test Malayalam REMOVE_ITEM intent recognition."""
    res = client.post("/api/v1/voice/parse", json={"text": "പാൽ നീക്കം ചെയ്യൂ"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.REMOVE_ITEM
    assert data["item"] == "milk"


def test_malayalam_update_quantity():
    """Test Malayalam UPDATE_QUANTITY intent recognition."""
    res = client.post("/api/v1/voice/parse", json={"text": "പാലിന്റെ അളവ് 5 ആക്കൂ"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.UPDATE_QUANTITY
    assert data["item"] == "milk"
    assert data["quantity"] == 5.0


def test_malayalam_show_list():
    """Test Malayalam SHOW_LIST intent recognition."""
    res = client.post("/api/v1/voice/parse", json={"text": "എന്റെ ഷോപ്പിംഗ് ലിസ്റ്റ് കാണിക്കൂ"})
    assert res.status_code == 200
    assert res.json()["intent"] == IntentEnum.SHOW_LIST


def test_malayalam_clear_list():
    """Test Malayalam CLEAR_LIST intent recognition."""
    res = client.post("/api/v1/voice/parse", json={"text": "ലിസ്റ്റ് ക്ലിയർ ചെയ്യൂ"})
    assert res.status_code == 200
    assert res.json()["intent"] == IntentEnum.CLEAR_LIST


def test_malayalam_get_suggestions():
    """Test Malayalam GET_SUGGESTIONS intent recognition."""
    res = client.post("/api/v1/voice/parse", json={"text": "എന്തൊക്കെ വാങ്ങണം?"})
    assert res.status_code == 200
    assert res.json()["intent"] == IntentEnum.GET_SUGGESTIONS


def test_malayalam_unknown_sentence():
    """Test UNKNOWN intent for random Malayalam sentence."""
    res = client.post("/api/v1/voice/parse", json={"text": "പാരീസിൽ ഇന്നത്തെ കാലാവസ്ഥ എന്താണ്?"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == IntentEnum.UNKNOWN
    assert data["confidence"] == 0.0


def test_malayalam_api_execution_and_database_verification():
    """Verify parse, execute, and database state for Malayalam voice command."""
    # 1. Clear shopping list first
    client.post("/api/v1/voice/execute", json={"text": "Clear my list"})

    # 2. Parse command
    text = "രണ്ട് കുപ്പി പാൽ ചേർക്കൂ"
    parse_res = client.post("/api/v1/voice/parse", json={"text": text})
    assert parse_res.status_code == 200
    p_data = parse_res.json()
    assert p_data["intent"] == IntentEnum.ADD_ITEM
    assert p_data["item"] == "milk"
    assert p_data["quantity"] == 2.0
    assert p_data["unit"] == "bottles"

    # 3. Execute command
    exec_res = client.post("/api/v1/voice/execute", json={"text": text})
    assert exec_res.status_code == 200
    e_data = exec_res.json()
    assert e_data["success"] is True
    assert e_data["intent"] == IntentEnum.ADD_ITEM

    # 4. Verify database state via GET /api/v1/items
    items_res = client.get("/api/v1/items")
    assert items_res.status_code == 200
    items = items_res.json()
    assert len(items) == 1
    item = items[0]
    assert item["item_name"] == "milk"
    assert item["quantity"] == 2.0
    assert item["unit"] == "bottles"
    assert item["category"] == "dairy"

    # 5. Verify duplicate merging behavior: Execute "പാൽ ചേർക്കൂ" (+1 milk)
    exec_res2 = client.post("/api/v1/voice/execute", json={"text": "പാൽ ചേർക്കൂ"})
    assert exec_res2.status_code == 200
    
    items_res2 = client.get("/api/v1/items")
    items2 = items_res2.json()
    assert len(items2) == 1
    assert items2[0]["item_name"] == "milk"
    assert items2[0]["quantity"] == 3.0
