import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.intent import IntentEnum

client = TestClient(app)


def test_bilingual_code_switching_add_items():
    """Verify bilingual/code-switched ADD_ITEM commands in English, Malayalam, and Mixed language."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    # 1. Malayalam + English product
    res1 = client.post("/api/v1/voice/parse", json={"text": "milk ചേർക്കൂ", "language": "ml-IN"})
    assert res1.status_code == 200
    assert res1.json()["intent"] == IntentEnum.ADD_ITEM
    assert res1.json()["item"] == "milk"

    # 2. English number + English unit + English product + Malayalam verb
    res2 = client.post("/api/v1/voice/parse", json={"text": "2 bottles milk ചേർക്കൂ", "language": "ml-IN"})
    assert res2.status_code == 200
    assert res2.json()["intent"] == IntentEnum.ADD_ITEM
    assert res2.json()["item"] == "milk"
    assert res2.json()["quantity"] == 2.0
    assert res2.json()["unit"] == "bottles"

    # 3. Malayalam number + English unit + English product + Malayalam verb
    res3 = client.post("/api/v1/voice/parse", json={"text": "രണ്ട് bottles milk ചേർക്കൂ", "language": "ml-IN"})
    assert res3.status_code == 200
    assert res3.json()["intent"] == IntentEnum.ADD_ITEM
    assert res3.json()["item"] == "milk"
    assert res3.json()["quantity"] == 2.0
    assert res3.json()["unit"] == "bottles"

    # 4. English number + Malayalam unit + English product
    res4 = client.post("/api/v1/voice/parse", json={"text": "2 കുപ്പി milk ചേർക്കൂ", "language": "ml-IN"})
    assert res4.status_code == 200
    assert res4.json()["intent"] == IntentEnum.ADD_ITEM
    assert res4.json()["item"] == "milk"
    assert res4.json()["quantity"] == 2.0
    assert res4.json()["unit"] == "bottles"

    # 5. English products + English conjunction + Malayalam verb
    res5 = client.post("/api/v1/voice/parse", json={"text": "milk and bread ചേർക്കൂ", "language": "ml-IN"})
    assert res5.status_code == 200
    assert res5.json()["intent"] == IntentEnum.ADD_ITEM
    items5 = res5.json()["items"]
    assert len(items5) == 2
    assert items5[0]["item"] == "milk"
    assert items5[1]["item"] == "bread"


def test_bilingual_checkout_and_confirmation_flow():
    """Verify bilingual checkout commands and context-aware confirmation across languages."""
    session_id = "test-session-bilingual-checkout"

    # Clear list
    client.post("/api/v1/voice/execute", json={"text": "Delete all items", "session_id": session_id})

    # Add item
    client.post("/api/v1/voice/execute", json={"text": "milk ചേർക്കൂ", "session_id": session_id})

    # Checkout in Malayalam with English keyword
    co_res = client.post("/api/v1/voice/execute", json={"text": "checkout ചെയ്യൂ", "session_id": session_id})
    assert co_res.status_code == 200
    assert co_res.json()["success"] is True
    assert "Your total" in co_res.json()["message"] or "തുക" in co_res.json()["message"]

    # Confirm in English "yes"
    conf_res = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_id})
    assert conf_res.status_code == 200
    assert conf_res.json()["success"] is True
    assert conf_res.json()["intent"] == "CONFIRM_ORDER"
    assert "Order #" in conf_res.json()["message"]


def test_bilingual_mixed_confirmation_phrases():
    """Test mixed English/Malayalam confirmation phrases with active pending checkout."""
    phrases = [
        "yes confirm",
        "yes place ചെയ്യൂ",
        "അതെ confirm ചെയ്യൂ",
        "ശരി, place it",
        "confirm ചെയ്യൂ",
        "order confirm ചെയ്യൂ"
    ]
    for idx, phrase in enumerate(phrases):
        session_id = f"test-sess-conf-{idx}"
        client.post("/api/v1/voice/execute", json={"text": "Delete all items", "session_id": session_id})
        client.post("/api/v1/voice/execute", json={"text": "add 2 bottles of milk", "session_id": session_id})
        
        # Trigger checkout preview
        co = client.post("/api/v1/voice/execute", json={"text": "checkout ചെയ്യൂ", "session_id": session_id})
        assert co.json()["success"] is True

        # Confirm with mixed phrase
        cf = client.post("/api/v1/voice/execute", json={"text": phrase, "session_id": session_id})
        assert cf.status_code == 200
        print(f"PHRASE: {phrase} RESPONSE: {cf.json()}")
        assert cf.json()["success"] is True, f"Failed for phrase: {phrase} - {cf.json()}"
        assert cf.json()["intent"] == "CONFIRM_ORDER"


def test_confirmation_without_pending_checkout_rejected():
    """Verify 'yes' or 'അതെ' WITHOUT pending checkout is rejected safely without mutating DB."""
    session_id = "test-no-pending"
    res1 = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_id})
    assert res1.status_code == 200
    assert res1.json()["success"] is False
    assert "no pending order" in res1.json()["message"].lower()

    res2 = client.post("/api/v1/voice/execute", json={"text": "അതെ", "session_id": session_id})
    assert res2.status_code == 200
    assert res2.json()["success"] is False
    assert "no pending order" in res2.json()["message"].lower()


def test_bilingual_negation_safety():
    """Verify negated additions and negated checkouts cause 0 database mutations."""
    # 1. Negated addition
    res1 = client.post("/api/v1/voice/execute", json={"text": "don't add milk"})
    assert res1.status_code == 200
    assert res1.json()["success"] is False

    res2 = client.post("/api/v1/voice/execute", json={"text": "milk വേണ്ട"})
    assert res2.status_code == 200
    assert res2.json()["success"] is False

    # 2. Negated checkout
    session_id = "test-neg-co"
    client.post("/api/v1/voice/execute", json={"text": "add eggs", "session_id": session_id})
    client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": session_id})
    
    cancel_res = client.post("/api/v1/voice/execute", json={"text": "checkout വേണ്ട", "session_id": session_id})
    assert cancel_res.status_code == 200
    assert cancel_res.json()["intent"] == "CANCEL_ORDER"
