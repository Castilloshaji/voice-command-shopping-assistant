import pytest
from app.models.product import Product
from app.services.language_profiles import SUPPORTED_LANGUAGES


def test_catalog_size_and_categories(client):
    """Verify expanded supermarket catalog has over 100 realistic products across categories."""
    res = client.get("/api/v1/products")
    assert res.status_code == 200
    products = res.json()
    assert len(products) >= 100

    categories = set(p["category"] for p in products)
    assert len(categories) >= 15

    brands = set(p["brand"] for p in products if p.get("brand"))
    assert len(brands) >= 15


def test_ambiguity_safety_and_unique_resolution(client):
    """
    Test ambiguity safety layer:
    - Specific query 'add green apples' resolves uniquely to Green Apples.
    """
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    res_green = client.post("/api/v1/voice/execute", json={"text": "add green apples"})
    assert res_green.status_code == 200
    assert res_green.json()["success"] is True

    items = client.get("/api/v1/items").json()
    assert len(items) == 1
    assert "green apples" in items[0]["item_name"].lower()


def test_malayalam_aliases_and_voice_commands(client):
    """Test Malayalam alias resolution and voice command execution."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    res1 = client.post("/api/v1/voice/execute", json={"text": "രണ്ട് കുപ്പി പാൽ ചേർക്കൂ", "language": "ml-IN"})
    assert res1.status_code == 200, res1.json()
    assert res1.json()["success"] is True, res1.json()

    res2 = client.post("/api/v1/voice/execute", json={"text": "അരി ചേർക്കൂ", "language": "ml-IN"})
    assert res2.status_code == 200, res2.json()
    assert res2.json()["success"] is True, res2.json()

    res3 = client.post("/api/v1/voice/execute", json={"text": "മുട്ട ചേർക്കൂ", "language": "ml-IN"})
    assert res3.status_code == 200, res3.json()
    assert res3.json()["success"] is True, res3.json()

    items = client.get("/api/v1/items").json()
    assert len(items) == 3
    item_names = [i["item_name"].lower() for i in items]
    assert any("milk" in n for n in item_names)
    assert any("rice" in n for n in item_names)
    assert any("egg" in n for n in item_names)


def test_mixed_code_switching_voice_commands(client):
    """Test mixed-language code switching."""
    client.post("/api/v1/voice/execute", json={"text": "Delete all items"})

    res = client.post("/api/v1/voice/execute", json={"text": "രണ്ട് bottles milk ചേർക്കൂ", "language": "ml-IN"})
    assert res.status_code == 200, res.json()
    assert res.json()["success"] is True, res.json()

    items = client.get("/api/v1/items").json()
    assert len(items) == 1
    assert items[0]["quantity"] == 2.0
    assert items[0]["unit"] == "bottles"


def test_no_hindi_references_in_backend_service():
    """Verify backend supported languages explicitly contains only English and Malayalam."""
    assert "en" in SUPPORTED_LANGUAGES
    assert "ml" in SUPPORTED_LANGUAGES
    assert "hi" not in SUPPORTED_LANGUAGES
    assert len(SUPPORTED_LANGUAGES) == 2
