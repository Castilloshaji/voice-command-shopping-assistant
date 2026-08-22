import pytest
from app.services.recommendation_service import get_season_for_month, get_current_season

def test_season_resolution_for_months():
    # Winter: Dec (12), Jan (1), Feb (2)
    assert get_season_for_month(12) == "winter"
    assert get_season_for_month(1) == "winter"
    assert get_season_for_month(2) == "winter"

    # Spring: Mar (3), Apr (4), May (5)
    assert get_season_for_month(3) == "spring"
    assert get_season_for_month(4) == "spring"
    assert get_season_for_month(5) == "spring"

    # Summer: Jun (6), Jul (7), Aug (8)
    assert get_season_for_month(6) == "summer"
    assert get_season_for_month(7) == "summer"
    assert get_season_for_month(8) == "summer"

    # Fall: Sep (9), Oct (10), Nov (11)
    assert get_season_for_month(9) == "fall"
    assert get_season_for_month(10) == "fall"
    assert get_season_for_month(11) == "fall"

def test_invalid_month_raises():
    with pytest.raises(ValueError):
        get_season_for_month(0)
    with pytest.raises(ValueError):
        get_season_for_month(13)

def test_controlled_current_season_override():
    assert get_current_season(override_month=1) == "winter"
    assert get_current_season(override_month=4) == "spring"
    assert get_current_season(override_month=7) == "summer"
    assert get_current_season(override_month=10) == "fall"
