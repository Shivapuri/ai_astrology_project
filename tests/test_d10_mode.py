import pytest
from jyotish.generate_jyotish import generate_kala_chart
from app import app

TRUMP_DATA = {
    "name": "Donald Trump",
    "year": 1946,
    "month": 6,
    "day": 14,
    "hour": 10,
    "minute": 54,
    "lat": 40.6915,
    "lon": -73.8057,
    "tz": -4.0
}

def test_trump_d10_reverse_mode():
    """Verify D10 using Ernst Wilhelm's Kala default (Reverse for Even Rasis)."""
    chart = generate_kala_chart(
        name=TRUMP_DATA["name"],
        year=TRUMP_DATA["year"],
        month=TRUMP_DATA["month"],
        day=TRUMP_DATA["day"],
        hour=TRUMP_DATA["hour"],
        minute=TRUMP_DATA["minute"],
        latitude=TRUMP_DATA["lat"],
        longitude=TRUMP_DATA["lon"],
        timezone_offset=TRUMP_DATA["tz"],
        d10_mode="reverse"
    )
    d10 = chart["vargas"]["D10"]["grahas"]
    # In Kala reverse mode:
    assert d10["Mercury"]["sign"] == "Capricorn"
    assert d10["Saturn"]["sign"] == "Leo"
    assert d10["Venus"]["sign"] == "Cancer"
    # Odd signs are identical in both modes
    assert d10["Sun"]["sign"] == "Capricorn"
    assert d10["Mars"]["sign"] == "Aries"
    assert d10["Moon"]["sign"] == "Cancer"
    assert d10["Jupiter"]["sign"] == "Pisces"

def test_trump_d10_direct_mode():
    """Verify D10 using Contemporary Forward reckoning (Vic DiCara interpretation)."""
    chart = generate_kala_chart(
        name=TRUMP_DATA["name"],
        year=TRUMP_DATA["year"],
        month=TRUMP_DATA["month"],
        day=TRUMP_DATA["day"],
        hour=TRUMP_DATA["hour"],
        minute=TRUMP_DATA["minute"],
        latitude=TRUMP_DATA["lat"],
        longitude=TRUMP_DATA["lon"],
        timezone_offset=TRUMP_DATA["tz"],
        d10_mode="direct"
    )
    d10 = chart["vargas"]["D10"]["grahas"]
    # In contemporary direct mode (matches Vic DiCara's chart):
    assert d10["Mercury"]["sign"] == "Taurus"
    assert d10["Saturn"]["sign"] == "Libra"
    assert d10["Venus"]["sign"] == "Scorpio"
    # Odd signs are identical in both modes
    assert d10["Sun"]["sign"] == "Capricorn"
    assert d10["Mars"]["sign"] == "Aries"
    assert d10["Moon"]["sign"] == "Cancer"
    assert d10["Jupiter"]["sign"] == "Pisces"

def test_api_d10_mode_switch():
    """Verify that the Flask endpoint dynamically accepts d10_mode query param."""
    client = app.test_client()
    # Donald Trump chart ID from database/Charts.jsonl
    trump_id = "9bb691ba-c4fd-40f1-83eb-289b4e275ac8"
    
    # 1. Reverse mode
    res_rev = client.get(f"/api/chart/{trump_id}?d10_mode=reverse")
    assert res_rev.status_code == 200
    rev_data = res_rev.get_json()["data"]
    assert rev_data["vargas"]["D10"]["grahas"]["Mercury"]["sign"] == "Capricorn"
    
    # 2. Direct mode
    res_dir = client.get(f"/api/chart/{trump_id}?d10_mode=direct")
    assert res_dir.status_code == 200
    dir_data = res_dir.get_json()["data"]
    assert dir_data["vargas"]["D10"]["grahas"]["Mercury"]["sign"] == "Taurus"
