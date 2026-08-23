import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.intent import IntentEnum, ParsedIntent, IntentItem
from app.ai.llm_client import MockLLMClient
from app.ai.intent_parser import AIIntentParser
from app.ai.response_generator import AIResponseGenerator
from app.ai.conversation_manager import conversation_manager

client = TestClient(app)


def test_mock_llm_simple_add_item():
    mock_json = json.dumps({
        "intent": "ADD_ITEM",
        "items": [{"item": "milk", "quantity": 2.0, "unit": "bottles"}],
        "confidence": 0.98,
        "clarification_required": False
    })
    mock_client = MockLLMClient(predefined_json=mock_json)

    parsed = AIIntentParser.parse_intent(
        transcript="Hey can you grab me two bottles of milk",
        llm_client=mock_client
    )

    assert parsed is not None
    assert parsed.intent == IntentEnum.ADD_ITEM
    assert parsed.item == "milk"
    assert parsed.quantity == 2.0
    assert parsed.unit == "bottles"


def test_mock_llm_compound_add_item():
    mock_json = json.dumps({
        "intent": "ADD_ITEM",
        "items": [
            {"item": "milk", "quantity": 2.0, "unit": "bottles"},
            {"item": "apples", "quantity": 3.0, "unit": None}
        ],
        "confidence": 0.99
    })
    mock_client = MockLLMClient(predefined_json=mock_json)

    parsed = AIIntentParser.parse_intent(
        transcript="Add 2 bottles of milk and 3 apples",
        llm_client=mock_client
    )

    assert parsed is not None
    assert parsed.intent == IntentEnum.ADD_ITEM
    assert parsed.items is not None
    assert len(parsed.items) == 2
    assert parsed.items[0].item == "milk"
    assert parsed.items[0].quantity == 2.0
    assert parsed.items[0].unit == "bottles"
    assert parsed.items[1].item == "apples"
    assert parsed.items[1].quantity == 3.0


def test_mock_llm_search_product():
    mock_json = json.dumps({
        "intent": "SEARCH_PRODUCT",
        "query": "toothpaste",
        "brand": "Dove",
        "max_price": 5.0,
        "confidence": 0.95
    })
    mock_client = MockLLMClient(predefined_json=mock_json)

    parsed = AIIntentParser.parse_intent(
        transcript="Find Dove toothpaste under 5 dollars",
        llm_client=mock_client
    )

    assert parsed is not None
    assert parsed.intent == IntentEnum.SEARCH_PRODUCT
    assert parsed.brand == "Dove"
    assert parsed.max_price == 5.0


def test_llm_invalid_json_fallback_to_nlp_service():
    """Verify malformed LLM output causes AIIntentParser to return None, falling back to NLPService."""
    mock_client = MockLLMClient(predefined_json="INVALID JSON STRUCTURE")

    parsed = AIIntentParser.parse_intent(
        transcript="add milk",
        llm_client=mock_client
    )
    assert parsed is None


def test_llm_unavailable_fallback_to_nlp_service():
    """Verify unavailable LLM client returns None, triggering deterministic fallback."""
    mock_client = MockLLMClient()
    mock_client.is_active = False

    parsed = AIIntentParser.parse_intent(
        transcript="add 2 bottles of milk",
        llm_client=mock_client
    )
    assert parsed is None


def test_catalog_validation_and_atomicity_with_unicorn_juice():
    """
    CRITICAL ATOMICITY ACCEPTANCE TEST:
    Command: 'add milk and unicorn juice'
    Since 'unicorn juice' is not in the store catalog, 0 DB mutations must occur!
    """
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    res = client.post("/api/v1/voice/execute", json={"text": "add milk and unicorn juice"})
    assert res.status_code == 200
    r_data = res.json()
    assert r_data["success"] is False

    # Verify zero items were added to DB
    items = client.get("/api/v1/items").json()
    assert len(items) == 0


def test_conversational_context_followup_make_that_two_bottles():
    """
    CONVERSATIONAL CONTEXT ACCEPTANCE TEST:
    Turn 1: 'Add milk' -> added milk (qty 1)
    Turn 2: Contextual update 'make that two bottles' resolves using LLMIntent to milk (qty=2, unit=bottles).
    """
    session_id = "test-session-ctx-1"
    client.post("/api/v1/voice/execute", json={"text": "Delete all items", "session_id": session_id})

    # Turn 1: Add milk
    res1 = client.post("/api/v1/voice/execute", json={"text": "add milk", "session_id": session_id})
    assert res1.status_code == 200
    assert res1.json()["success"] is True

    # Turn 2: Mock LLM resolving 'make that two bottles' using conversation context
    mock_json = json.dumps({
        "intent": "UPDATE_QUANTITY",
        "items": [{"item": "milk", "quantity": 2.0, "unit": "bottles"}],
        "confidence": 0.99
    })
    mock_client = MockLLMClient(predefined_json=mock_json)

    parsed = AIIntentParser.parse_intent(
        transcript="make that two bottles",
        session_id=session_id,
        llm_client=mock_client
    )
    assert parsed is not None
    assert parsed.intent == IntentEnum.UPDATE_QUANTITY

    # Execute validated intent
    from app.services.command_service import CommandService
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        exec_res = CommandService.execute_command(db, parsed)
        assert exec_res.success is True
    finally:
        db.close()

    items = client.get("/api/v1/items").json()
    assert len(items) == 1
    assert items[0]["item_name"] == "milk"
    assert items[0]["quantity"] == 2.0
    assert items[0]["unit"] == "bottles"


def test_conversational_context_followup_actually_remove_it():
    """
    CONVERSATIONAL CONTEXT TEST:
    Turn 1: 'Add bread'
    Turn 2: Contextual removal 'actually remove it' resolves using LLMIntent to REMOVE_ITEM bread.
    """
    session_id = "test-session-ctx-2"
    client.post("/api/v1/voice/execute", json={"text": "Delete all items", "session_id": session_id})

    res1 = client.post("/api/v1/voice/execute", json={"text": "add bread", "session_id": session_id})
    assert res1.status_code == 200
    assert res1.json()["success"] is True

    # Turn 2: Mock LLM resolving 'actually remove it' using context
    mock_json = json.dumps({
        "intent": "REMOVE_ITEM",
        "items": [{"item": "bread", "quantity": 1.0, "unit": None}],
        "confidence": 0.98
    })
    mock_client = MockLLMClient(predefined_json=mock_json)

    parsed = AIIntentParser.parse_intent(
        transcript="actually remove it",
        session_id=session_id,
        llm_client=mock_client
    )
    assert parsed is not None
    assert parsed.intent == IntentEnum.REMOVE_ITEM

    from app.services.command_service import CommandService
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        exec_res = CommandService.execute_command(db, parsed)
        assert exec_res.success is True
    finally:
        db.close()

    items = client.get("/api/v1/items").json()
    assert len(items) == 0


def test_response_generator_fallback():
    mock_client = MockLLMClient()
    mock_client.is_active = False

    parsed = ParsedIntent(intent=IntentEnum.ADD_ITEM, original_text="add milk")
    from app.schemas.command import CommandExecutionResponse
    exec_res = CommandExecutionResponse(success=True, intent=IntentEnum.ADD_ITEM, message="Added milk to your shopping list.")

    msg = AIResponseGenerator.generate_natural_response(parsed, exec_res, llm_client=mock_client)
    assert msg == "Added milk to your shopping list."
