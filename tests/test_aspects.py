import pytest
from jyotish.aspects.aspects import (
    get_rasi_drishti,
    get_graha_drishti,
    get_all_graha_drishtis,
    get_all_rasi_drishtis,
    calculate_advanced_graha_aspects,
)

def test_rasi_drishti_cardinal():
    """Moveable signs aspect Fixed signs EXCEPT the adjacent one."""
    aries_aspects = get_rasi_drishti("Aries")
    assert "Leo" in aries_aspects
    assert "Scorpio" in aries_aspects
    assert "Aquarius" in aries_aspects
    assert "Taurus" not in aries_aspects # Adjacent fixed sign

def test_rasi_drishti_fixed():
    """Fixed signs aspect Moveable signs EXCEPT the adjacent one."""
    taurus_aspects = get_rasi_drishti("Taurus")
    assert "Cancer" in taurus_aspects
    assert "Libra" in taurus_aspects
    assert "Capricorn" in taurus_aspects
    assert "Aries" not in taurus_aspects # Adjacent cardinal sign

def test_rasi_drishti_dual():
    """Dual signs aspect all other Dual signs."""
    gemini_aspects = get_rasi_drishti("Gemini")
    assert "Virgo" in gemini_aspects
    assert "Sagittarius" in gemini_aspects
    assert "Pisces" in gemini_aspects
    assert "Gemini" not in gemini_aspects # Cannot aspect itself

def test_graha_drishti_standard():
    """Test the basic fractional strength of Graha Drishti."""
    # 180 degrees should be full strength (60 virupas)
    assert get_graha_drishti("Sun", 0.0, 180.0) == 60.0
    
    # 150 degrees should be 0 strength
    assert get_graha_drishti("Sun", 0.0, 150.0) == 0.0
    
    # 120 degrees should be 30 strength
    assert get_graha_drishti("Sun", 0.0, 120.0) == 30.0
    
    # < 30 degrees should be 0
    assert get_graha_drishti("Sun", 0.0, 15.0) == 0.0

def test_graha_drishti_special():
    """Test the special aspect bonuses for Mars, Jupiter, Saturn."""
    # Saturn gets a bonus at 3rd (60 deg) and 10th (270 deg)
    assert get_graha_drishti("Saturn", 0.0, 60.0) == 60.0
    assert get_graha_drishti("Saturn", 0.0, 270.0) == 60.0
    
    # Jupiter gets a bonus at 5th (120 deg) and 9th (240 deg)
    assert get_graha_drishti("Jupiter", 0.0, 120.0) == 60.0
    assert get_graha_drishti("Jupiter", 0.0, 240.0) == 60.0
    
    # Mars gets a bonus at 4th (90 deg) and 8th (210 deg)
    assert get_graha_drishti("Mars", 0.0, 90.0) == 60.0
    assert get_graha_drishti("Mars", 0.0, 210.0) == 60.0
    
    # Standard planets do not get these bonuses
    assert get_graha_drishti("Venus", 0.0, 75.0) < 60.0
    assert get_graha_drishti("Mercury", 0.0, 135.0) < 60.0

def test_graha_drishti_non_casting_bodies():
    """Rahu, Ketu, Lagna, and MC do not cast Graha Drishti."""
    assert get_graha_drishti("Rahu", 0.0, 180.0) == 0.0
    assert get_graha_drishti("Ketu", 0.0, 180.0) == 0.0
    assert get_graha_drishti("Lagna", 0.0, 180.0) == 0.0
    assert get_graha_drishti("MC", 0.0, 180.0) == 0.0

def test_all_graha_drishtis():
    """Test the batch calculation for all planets."""
    planets_data = {
        "Sun": {"longitude": 0.0},
        "Moon": {"longitude": 180.0},
        "Jupiter": {"longitude": 135.0}
    }
    
    results = get_all_graha_drishtis(planets_data)
    
    # Sun aspects Moon (180 deg) fully
    assert results["Moon"]["Sun"] == 60.0
    
    # Moon aspects Sun (180 deg) fully
    assert results["Sun"]["Moon"] == 60.0
    
    # Jupiter aspects Sun (approx 225 deg from Jupiter to Sun -> (0 - 135)%360 = 225)
    # Jupiter at 225 has base value.
    assert "Jupiter" in results["Sun"]
    assert results["Sun"]["Jupiter"] > 0.0

def test_all_rasi_drishtis():
    """Test the batch calculation for all Rasi aspects."""
    planets_data = {
        "Sun": {"sign": "Aries"},
        "Moon": {"sign": "Leo"},
        "Mars": {"sign": "Taurus"} # Adjacent to Aries
    }
    
    results = get_all_rasi_drishtis(planets_data)
    
    # Aries aspects Leo, so Sun aspects Moon
    assert "Sun" in results["Moon"]
    
    # Leo aspects Aries, so Moon aspects Sun
    assert "Moon" in results["Sun"]
    
    # Aries does not aspect Taurus (adjacent), so Sun does not aspect Mars
    assert "Sun" not in results["Mars"]


def test_advanced_graha_aspects_yutis_bidirectional_nodes():
    """
    Rahu and Ketu do not cast Graha Drishti rays, but they form two-way Yutis (conjunctions)
    with physical planets in the same sign, while mathematical points (Lagna, MC) are excluded.
    """
    planets_data = {
        "Jupiter": {"longitude": 125.0, "sign": "Leo"},
        "Rahu": {"longitude": 128.0, "sign": "Leo"},
        "Lagna": {"longitude": 122.0, "sign": "Leo"},
        "MC": {"longitude": 129.0, "sign": "Leo"},
        "Saturn": {"longitude": 215.0, "sign": "Scorpio"},
    }
    shadbala_data = {}
    res = calculate_advanced_graha_aspects(planets_data, shadbala_data)

    # Jupiter and Rahu are in the same sign (Leo)
    assert "Rahu" in res["yutis"]["Jupiter"], "Jupiter's yutis must include Rahu"
    assert "Jupiter" in res["yutis"]["Rahu"], "Rahu's yutis must include Jupiter"

    # Non-planetary sensitive points (Lagna, MC) must not appear in yutis
    assert "Lagna" not in res["yutis"]["Jupiter"]
    assert "MC" not in res["yutis"]["Jupiter"]
    assert "Lagna" not in res["yutis"]["Rahu"]
    assert "MC" not in res["yutis"]["Rahu"]

