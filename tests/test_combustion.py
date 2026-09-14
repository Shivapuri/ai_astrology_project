"""
Unit and regression tests for Planetary Combustion (Asta / Astangata) calculations.
Validates:
1. Surya Siddhanta / Varaha Mihira combustion orbs with retrograde contraction.
2. Angular distance calculation from the Sun.
3. Telemetry export: sun_distance, combustion_orb, combustion_severity, combustion_range, ruled_houses.
4. Immunity of Sun, Rahu, and Ketu from combustion.
5. Integration with Angelina Jolie's chart where retrograde Mercury is combust within 12° orb.
"""

import pytest
from jyotish.generate_jyotish import generate_kala_chart

def test_angelina_jolie_mercury_combustion():
    chart = generate_kala_chart(
        name="Angelina Jolie",
        year=1975, month=6, day=4, hour=9, minute=9,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )
    d1_grahas = chart["vargas"]["D1"]["grahas"]
    
    # Sun cannot be combust
    assert d1_grahas["Sun"]["is_combust"] is False
    assert d1_grahas["Sun"].get("sun_distance") is None
    
    # Rahu / Ketu cannot be combust
    assert d1_grahas["Rahu"]["is_combust"] is False
    assert d1_grahas["Ketu"]["is_combust"] is False
    
    # Mercury is retrograde and within ~8.91° of the Sun (Sun ~73.42°, Mercury ~82.33°)
    merc = d1_grahas["Mercury"]
    assert merc["is_retrograde"] is True
    assert merc["is_combust"] is True
    assert merc["combustion_orb"] == 12.0  # Surya Siddhanta retrograde orb
    assert 8.8 < merc["sun_distance"] < 9.0
    assert merc["combustion_severity"] == "Moderate"
    assert merc["combustion_range"] == "2° - 14°"
    
    # Ruled houses for Cancer Lagna: Mercury rules Gemini (H12) and Virgo (H3)
    assert set(merc["ruled_houses"]) == {3, 12}

def test_combustion_orbs_and_fields():
    # Test a chart and verify every physical planet has combustion telemetry populated
    chart = generate_kala_chart(
        name="Test Chart",
        year=1983, month=11, day=10, hour=22, minute=20,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0
    )
    d1_grahas = chart["vargas"]["D1"]["grahas"]
    
    for p in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        g = d1_grahas[p]
        assert "is_combust" in g
        assert isinstance(g["is_combust"], bool)
        assert g["sun_distance"] is not None
        assert g["combustion_orb"] is not None
        assert g["combustion_range"] is not None
        assert "ruled_houses" in g
        assert len(g["ruled_houses"]) in (1, 2)
        
        # Verify combustion condition matches distance < orb
        assert g["is_combust"] == (g["sun_distance"] < g["combustion_orb"])
