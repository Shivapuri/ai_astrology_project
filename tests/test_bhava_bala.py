"""
tests/test_bhava_bala.py
Unit and regression tests for Bhava Bala and Yuddha Bala engines.
"""

import pytest
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.shadbala.bhava_bala import (
    get_sign_genus,
    calculate_bhava_dig_bala,
    calculate_bhava_drishti_bala,
    calculate_bhava_bala
)
from jyotish.shadbala.shadbala import calculate_yuddha_bala, BIMBA_PARIMANAS

def test_sign_genus_classification():
    # Nara (Human)
    assert get_sign_genus("Gemini", 10.0) == "Nara"
    assert get_sign_genus("Virgo", 25.0) == "Nara"
    assert get_sign_genus("Libra", 12.0) == "Nara"
    assert get_sign_genus("Aquarius", 5.0) == "Nara"
    assert get_sign_genus("Sagittarius", 14.9) == "Nara"
    assert get_sign_genus("Sagittarius", 15.1) == "Chathushpada"

    # Jalachara (Watery)
    assert get_sign_genus("Cancer", 10.0) == "Jalachara"
    assert get_sign_genus("Pisces", 20.0) == "Jalachara"
    assert get_sign_genus("Capricorn", 15.1) == "Jalachara"
    assert get_sign_genus("Capricorn", 14.9) == "Chathushpada"

    # Keeta (Insect)
    assert get_sign_genus("Scorpio", 10.0) == "Keeta"

    # Chathushpada (Quadruped)
    assert get_sign_genus("Aries", 5.0) == "Chathushpada"
    assert get_sign_genus("Taurus", 15.0) == "Chathushpada"
    assert get_sign_genus("Leo", 20.0) == "Chathushpada"

def test_bhava_dig_bala_extremes():
    # Nara sign (Gemini at 75°): Zero house is 7, Max house is 1
    assert calculate_bhava_dig_bala(1, 75.0) == 60.0
    assert calculate_bhava_dig_bala(7, 75.0) == 0.0
    assert calculate_bhava_dig_bala(4, 75.0) == 30.0

    # Jalachara sign (Cancer at 105°): Zero house is 10, Max house is 4
    assert calculate_bhava_dig_bala(4, 105.0) == 60.0
    assert calculate_bhava_dig_bala(10, 105.0) == 0.0

    # Keeta sign (Scorpio at 225°): Zero house is 1, Max house is 7
    assert calculate_bhava_dig_bala(7, 225.0) == 60.0
    assert calculate_bhava_dig_bala(1, 225.0) == 0.0

def test_calculate_yuddha_bala_mechanics():
    # Mock Planetary War: Mars (280.5°) and Saturn (281.2°) in Capricorn (both in same sign, diff = 0.7° <= 1.0°)
    pre_war = {"Mars": 400.0, "Saturn": 350.0}
    longitudes = {"Mars": 280.5, "Saturn": 281.2}
    latitudes = {"Mars": 1.5, "Saturn": -0.5}

    adj = calculate_yuddha_bala(pre_war, longitudes, latitudes, use_latitude=True)
    
    # Mars has higher northern latitude (1.5 > -0.5) -> Mars is Winner, Saturn is Loser
    # Bala diff = |400 - 350| = 50.0
    # Bimba diff = |9.4 - 158.0| = 148.6
    expected_pts = round(50.0 / 148.6, 2)  # 0.34
    assert adj["Mars"] == expected_pts
    assert adj["Saturn"] == -expected_pts

def test_calculate_yuddha_bala_venus_invariance():
    # Venus vs Mars within 0.5°: Venus must ALWAYS win regardless of latitude or longitude
    pre_war = {"Venus": 300.0, "Mars": 400.0}
    longitudes = {"Venus": 50.5, "Mars": 50.2}
    latitudes = {"Venus": -1.5, "Mars": 2.0}

    adj = calculate_yuddha_bala(pre_war, longitudes, latitudes, use_latitude=True)
    assert adj["Venus"] > 0.0
    assert adj["Mars"] < 0.0

def test_bhava_bala_full_chart_integration():
    chart = generate_kala_chart(
        name="Angelina Jolie", year=1975, month=6, day=4,
        hour=9, minute=9, latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )
    d1 = chart["vargas"]["D1"]
    bhavas = d1.get("bhavas", [])
    bhava_madhyas = [b["cusp"] for b in bhavas]
    
    planet_positions = {p: d1["grahas"][p]["longitude"] for p in d1["grahas"]}
    shadbala_results = chart["shadbala"]

    bhava_bala = calculate_bhava_bala(bhava_madhyas, shadbala_results, planet_positions)
    assert len(bhava_bala) == 12

    for h in range(1, 13):
        res = bhava_bala[h]
        assert "house" in res
        assert "lord" in res
        assert "bhavadhipathi_bala" in res
        assert "bhava_digbala" in res
        assert "bhava_drishti_bala" in res
        assert res["total_virupas"] > 0
        assert res["total_rupas"] == round(res["total_virupas"] / 60.0, 2)
