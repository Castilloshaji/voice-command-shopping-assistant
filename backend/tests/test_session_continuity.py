import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.order import Order
from app.schemas.intent import IntentEnum
from app.ai.conversation_manager import conversation_manager

client = TestClient(app)


def reset_db_items_and_orders():
    """Helper to reset items and orders table for isolated test execution."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})


def count_db_orders() -> int:
    db = SessionLocal()
    try:
        return db.query(Order).count()
    finally:
        db.close()


def test_checkout_then_yes_same_session():
    """Verify 'checkout' followed by 'yes' on the same session places exactly one order."""
    reset_db_items_and_orders()
    session_id = "test-session-1"

    # Add item
    client.post("/api/v1/voice/execute", json={"text": "add 2 bottles of milk", "session_id": session_id})
    initial_orders = count_db_orders()

    # Step 1: Checkout preview
    res1 = client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": session_id})
    assert res1.status_code == 200
    assert res1.json()["success"] is True
    assert res1.json()["intent"] == IntentEnum.CHECKOUT
    assert "Your total" in res1.json()["message"]

    # Step 2: Confirm order with 'yes' on SAME session
    res2 = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_id})
    assert res2.status_code == 200
    assert res2.json()["success"] is True
    assert res2.json()["intent"] == IntentEnum.CONFIRM_ORDER
    assert "Order #" in res2.json()["message"]

    assert count_db_orders() == initial_orders + 1


def test_checkout_then_malayalam_yes_same_session():
    """Verify 'checkout' followed by Malayalam confirmation 'അതെ' on same session places order."""
    reset_db_items_and_orders()
    session_id = "test-session-ml-yes"

    client.post("/api/v1/voice/execute", json={"text": "add milk", "session_id": session_id})
    initial_orders = count_db_orders()

    res1 = client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": session_id})
    assert res1.json()["success"] is True

    res2 = client.post("/api/v1/voice/execute", json={"text": "അതെ", "session_id": session_id})
    assert res2.status_code == 200
    assert res2.json()["success"] is True
    assert res2.json()["intent"] == IntentEnum.CONFIRM_ORDER
    assert count_db_orders() == initial_orders + 1


def test_malayalam_checkout_then_english_yes():
    """Verify Malayalam checkout prompt followed by English 'yes' on same session places order."""
    reset_db_items_and_orders()
    session_id = "test-session-ml-co-en-yes"

    client.post("/api/v1/voice/execute", json={"text": "milk ചേർക്കൂ", "session_id": session_id, "language": "ml-IN"})
    initial_orders = count_db_orders()

    res1 = client.post("/api/v1/voice/execute", json={"text": "checkout ചെയ്യൂ", "session_id": session_id, "language": "ml-IN"})
    assert res1.json()["success"] is True

    res2 = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_id, "language": "en-US"})
    assert res2.status_code == 200
    assert res2.json()["success"] is True
    assert count_db_orders() == initial_orders + 1


def test_english_checkout_then_malayalam_yes():
    """Verify English checkout followed by Malayalam 'അതെ' on same session places order."""
    reset_db_items_and_orders()
    session_id = "test-session-en-co-ml-yes"

    client.post("/api/v1/voice/execute", json={"text": "add bread", "session_id": session_id})
    initial_orders = count_db_orders()

    res1 = client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": session_id})
    assert res1.json()["success"] is True

    res2 = client.post("/api/v1/voice/execute", json={"text": "അതെ", "session_id": session_id, "language": "ml-IN"})
    assert res2.status_code == 200
    assert res2.json()["success"] is True
    assert count_db_orders() == initial_orders + 1


def test_yes_without_pending_checkout():
    """Verify 'yes' without a pending checkout fails safely and creates 0 orders."""
    reset_db_items_and_orders()
    session_id = "test-session-no-pending"
    initial_orders = count_db_orders()

    res = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_id})
    assert res.status_code == 200
    assert res.json()["success"] is False
    assert "no pending order" in res.json()["message"].lower()
    assert count_db_orders() == initial_orders


def test_yes_with_different_session_id():
    """Verify 'yes' on Session B fails when checkout preview was created on Session A."""
    reset_db_items_and_orders()
    session_a = "test-session-A"
    session_b = "test-session-B"

    client.post("/api/v1/voice/execute", json={"text": "add milk", "session_id": session_a})
    initial_orders = count_db_orders()

    # Checkout on Session A
    res_a = client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": session_a})
    assert res_a.json()["success"] is True

    # Try confirming on Session B
    res_b = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_b})
    assert res_b.status_code == 200
    assert res_b.json()["success"] is False
    assert "no pending order" in res_b.json()["message"].lower()
    assert count_db_orders() == initial_orders


def test_microphone_restart_preserves_session():
    """Simulate microphone start/stop/restart reusing the exact same session_id."""
    reset_db_items_and_orders()
    stable_session_id = "persistent-mic-session-123"

    client.post("/api/v1/voice/execute", json={"text": "add apples", "session_id": stable_session_id})
    initial_orders = count_db_orders()

    # Mic click 1: speak checkout
    res1 = client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": stable_session_id})
    assert res1.json()["success"] is True

    # Mic click 2 (restart mic, same session ID): speak yes
    res2 = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": stable_session_id})
    assert res2.json()["success"] is True
    assert count_db_orders() == initial_orders + 1


def test_cart_mutation_invalidates_confirmation():
    """Verify modifying cart after checkout preview invalidates pending checkout confirmation."""
    reset_db_items_and_orders()
    session_id = "test-session-cart-mutation"

    client.post("/api/v1/voice/execute", json={"text": "add milk", "session_id": session_id})
    initial_orders = count_db_orders()

    # Checkout preview
    res_co = client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": session_id})
    assert res_co.json()["success"] is True

    # Cart mutation: Add eggs after checkout preview
    client.post("/api/v1/voice/execute", json={"text": "add eggs", "session_id": session_id})

    # Confirmation attempt
    res_confirm = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_id})
    assert res_confirm.status_code == 200
    assert res_confirm.json()["success"] is False
    assert "no pending order" in res_confirm.json()["message"].lower() or "changed" in res_confirm.json()["message"].lower()
    assert count_db_orders() == initial_orders


def test_duplicate_confirmation():
    """Verify sending 'yes' twice only creates exactly 1 order, and the second 'yes' fails."""
    reset_db_items_and_orders()
    session_id = "test-session-dup-confirm"

    client.post("/api/v1/voice/execute", json={"text": "add eggs", "session_id": session_id})
    initial_orders = count_db_orders()

    res_co = client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": session_id})
    assert res_co.json()["success"] is True

    # First yes -> success
    res_c1 = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_id})
    assert res_c1.json()["success"] is True

    # Second yes -> fails (already confirmed & pending_checkout cleared)
    res_c2 = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_id})
    assert res_c2.json()["success"] is False

    assert count_db_orders() == initial_orders + 1


def test_expired_pending_checkout():
    """Verify expired pending checkout fails and produces 0 orders."""
    reset_db_items_and_orders()
    session_id = "test-session-expired"

    client.post("/api/v1/voice/execute", json={"text": "add milk", "session_id": session_id})
    initial_orders = count_db_orders()

    # Checkout preview
    res_co = client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": session_id})
    assert res_co.json()["success"] is True

    # Force expire the session in ConversationManager
    session = conversation_manager.get_or_create_session(session_id)
    assert session is not None and session.pending_checkout is not None
    session.pending_checkout["expires_at"] = time.time() - 10.0  # Set past timestamp

    # Confirm expired session
    res_exp = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_id})
    assert res_exp.status_code == 200
    assert res_exp.json()["success"] is False
    assert "expired" in res_exp.json()["message"].lower()
    assert count_db_orders() == initial_orders


def test_pending_checkout_survives_parse_then_execute():
    """Verify calling /voice/parse followed by /voice/execute with same session_id maintains valid pending state."""
    reset_db_items_and_orders()
    session_id = "test-session-parse-execute"

    client.post("/api/v1/voice/execute", json={"text": "add milk", "session_id": session_id})
    initial_orders = count_db_orders()

    # Parse checkout (non-mutating)
    parse_co = client.post("/api/v1/voice/parse", json={"text": "checkout", "session_id": session_id})
    assert parse_co.json()["intent"] == IntentEnum.CHECKOUT

    # Execute checkout (creates pending state)
    exec_co = client.post("/api/v1/voice/execute", json={"text": "checkout", "session_id": session_id})
    assert exec_co.json()["success"] is True

    # Parse yes (non-mutating)
    parse_yes = client.post("/api/v1/voice/parse", json={"text": "yes", "session_id": session_id})
    assert parse_yes.json()["intent"] == IntentEnum.CONFIRM_ORDER

    # Execute yes (places order)
    exec_yes = client.post("/api/v1/voice/execute", json={"text": "yes", "session_id": session_id})
    assert exec_yes.json()["success"] is True
    assert count_db_orders() == initial_orders + 1
