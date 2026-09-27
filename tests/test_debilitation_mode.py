import pytest
from jyotish.relationships.relationships import get_dignity
from jyotish.generate_jyotish import generate_kala_chart

def test_get_dignity_moon_scorpio():
    # Moon at 5.7° Scorpio (past 3°)
    assert get_dignity("Moon", "Scorpio", compound_rel="Friend", degree=5.7, debilitation_mode="kala_degree") == "Friend's Sign"
    assert get_dignity("Moon", "Scorpio", compound_rel="Friend", degree=5.7, debilitation_mode="whole_sign") == "Debilitated"
    assert get_dignity("Moon", "Scorpio", compound_rel="Friend", degree=5.7, debilitation_mode="traditional") == "Debilitated"
    
    # Moon at 2.0° Scorpio (within 3°)
    assert get_dignity("Moon", "Scorpio", compound_rel="Friend", degree=2.0, debilitation_mode="kala_degree") == "Debilitated"
    assert get_dignity("Moon", "Scorpio", compound_rel="Friend", degree=2.0, debilitation_mode="whole_sign") == "Debilitated"
    assert get_dignity("Moon", "Scorpio", compound_rel="Friend", degree=2.0, debilitation_mode="traditional") == "Debilitated"

def test_get_dignity_mercury_pisces():
    # Mercury at 18.0° Pisces (past 15°)
    assert get_dignity("Mercury", "Pisces", compound_rel="Neutral", degree=18.0, debilitation_mode="kala_degree") == "Neutral's Sign"
    assert get_dignity("Mercury", "Pisces", compound_rel="Neutral", degree=18.0, debilitation_mode="whole_sign") == "Debilitated"
    assert get_dignity("Mercury", "Pisces", compound_rel="Neutral", degree=18.0, debilitation_mode="traditional") == "Debilitated"
    
    # Mercury at 10.0° Pisces (within 15°)
    assert get_dignity("Mercury", "Pisces", compound_rel="Neutral", degree=10.0, debilitation_mode="kala_degree") == "Debilitated"
    assert get_dignity("Mercury", "Pisces", compound_rel="Neutral", degree=10.0, debilitation_mode="whole_sign") == "Debilitated"
    assert get_dignity("Mercury", "Pisces", compound_rel="Neutral", degree=10.0, debilitation_mode="traditional") == "Debilitated"

def test_integration_generate_kala_chart_debilitation_mode():
    # Kailash (sister) chart with Moon at 5°42' Scorpio
    chart_kala = generate_kala_chart(
        year=1987, month=11, day=19, hour=16, minute=0, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0,
        debilitation_mode="kala_degree"
    )
    chart_whole = generate_kala_chart(
        year=1987, month=11, day=19, hour=16, minute=0, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0,
        debilitation_mode="whole_sign"
    )

    # Verify calculation settings
    assert chart_kala["calculation_settings"]["debilitation_mode"] == "kala_degree"
    assert chart_whole["calculation_settings"]["debilitation_mode"] == "whole_sign"

    # Verify Moon in D1
    moon_kala = chart_kala["vargas"]["D1"]["grahas"]["Moon"]
    moon_whole = chart_whole["vargas"]["D1"]["grahas"]["Moon"]
    
    assert moon_kala["sign"] == "Scorpio"
    assert moon_whole["sign"] == "Scorpio"
    assert moon_kala["degree_0_to_30"] > 3.0
    assert moon_whole["degree_0_to_30"] > 3.0
    
    assert moon_kala["dignity_breakdown"]["final_dignity"] == "Friend's Sign"
    assert moon_whole["dignity_breakdown"]["final_dignity"] == "Debilitated"
