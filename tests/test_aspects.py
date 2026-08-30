import pytest
from jyotish.aspects.aspects import get_rasi_drishti, get_graha_drishti, get_all_graha_drishtis, get_all_rasi_drishtis

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
    # Saturn gets a bonus at 3rd (approx 75 deg) and 10th (approx 285 deg)
    assert get_graha_drishti("Saturn", 0.0, 75.0) == 60.0
    assert get_graha_drishti("Saturn", 0.0, 285.0) == 60.0
    
    # Jupiter gets a bonus at 5th (approx 135 deg) and 9th (approx 255 deg)
    assert get_graha_drishti("Jupiter", 0.0, 135.0) == 60.0
    assert get_graha_drishti("Jupiter", 0.0, 255.0) == 60.0
    
    # Mars gets a bonus at 4th (approx 105 deg) and 8th (approx 225 deg)
    assert get_graha_drishti("Mars", 0.0, 105.0) == 60.0
    assert get_graha_drishti("Mars", 0.0, 225.0) == 60.0
    
    # Standard planets do not get these bonuses
    assert get_graha_drishti("Venus", 0.0, 75.0) < 60.0
    assert get_graha_drishti("Mercury", 0.0, 135.0) < 60.0

def test_graha_drishti_nodes():
    """Rahu and Ketu do not cast Graha Drishti."""
    assert get_graha_drishti("Rahu", 0.0, 180.0) == 0.0
    assert get_graha_drishti("Ketu", 0.0, 180.0) == 0.0

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
