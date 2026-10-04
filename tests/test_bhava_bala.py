"""
tests/test_bhava_bala.py
========================
Verification suite for Stage 3 Bhāva Bala & Phaladeepika Synthesis Engine.
"""

import pytest
from jyotish.bhavas.bhava_bala import (
    calculate_bhava_bala,
    calculate_bhava_dig_bala,
    calculate_bhava_drishti_bala,
    get_sign_genus
)
from jyotish.generate_jyotish import generate_kala_chart


class MockChartBaseline:
    """Mock representing Stage 1 ChartBaseline."""
    def __init__(self, ascendant, planets, is_day_birth=True):
        self.astronomical_anchors = {
            "ascendant": ascendant,
            "ascendant_lon": ascendant,
            "asc_longitude": ascendant,
            "sensitive_cusp_degree": ascendant % 30.0,
            "is_day_birth": is_day_birth
        }
        self.planets = planets


@pytest.fixture
def calibrated_shadbala():
    return {
        "Sun": {"Total_Virupas": 395.2, "Total_Rupas": 6.59, "Dig_Bala": 45.0},
        "Moon": {"Total_Virupas": 412.5, "Total_Rupas": 6.88, "Paksha_Bala": 45.0, "Dig_Bala": 30.0},
        "Mars": {"Total_Virupas": 365.0, "Total_Rupas": 6.08, "Dig_Bala": 20.0},
        "Mercury": {"Total_Virupas": 380.0, "Total_Rupas": 6.33, "Dig_Bala": 50.0},
        "Jupiter": {"Total_Virupas": 485.0, "Total_Rupas": 8.08, "Dig_Bala": 55.0},
        "Venus": {"Total_Virupas": 420.0, "Total_Rupas": 7.00, "Dig_Bala": 40.0},
        "Saturn": {"Total_Virupas": 340.0, "Total_Rupas": 5.67, "Dig_Bala": 15.0}
    }


def test_sign_genus_classification():
    """Validates classical boundary classification for Sagittarius and Capricorn."""
    assert get_sign_genus("Gemini", 10.0) == "Nara"
    assert get_sign_genus("Scorpio", 12.0) == "Keeta"
    assert get_sign_genus("Aries", 5.0) == "Chathushpada"
    assert get_sign_genus("Cancer", 22.0) == "Jalachara"
    
    assert get_sign_genus("Sagittarius", 14.99) == "Nara"
    assert get_sign_genus("Sagittarius", 15.01) == "Chathushpada"
    
    assert get_sign_genus("Capricorn", 14.99) == "Chathushpada"
    assert get_sign_genus("Capricorn", 15.01) == "Jalachara"


def test_bhava_dig_bala_cardinal_peaks():
    """Ensures exact 0 to 60 Virūpas behavior across directional poles."""
    assert calculate_bhava_dig_bala(1, 65.0) == 60.0
    assert calculate_bhava_dig_bala(7, 65.0) == 0.0
    assert calculate_bhava_dig_bala(4, 65.0) == 30.0

    assert calculate_bhava_dig_bala(10, 130.0) == 60.0
    assert calculate_bhava_dig_bala(4, 130.0) == 0.0

    assert calculate_bhava_dig_bala(4, 95.0) == 60.0
    assert calculate_bhava_dig_bala(10, 95.0) == 0.0

    assert calculate_bhava_dig_bala(7, 215.0) == 60.0
    assert calculate_bhava_dig_bala(1, 215.0) == 0.0


def test_house_lord_protection_aspect(calibrated_shadbala):
    """
    Certifies Phaladeepika Ch. 15.1-3: Saturn aspecting Capricorn
    is treated as protective (+1.0) rather than malefic (-0.25).
    """
    aspect_matrices = {
        "cusp_drishti": {
            "Saturn": {1: 40.0}
        }
    }
    # Case A: Saturn is NOT lord of House 1 -> -10.0 Virūpas
    val_unprotected = calculate_bhava_drishti_bala(
        bhava_madhya_lon=15.0,
        planet_positions={"Saturn": 195.0},
        aspect_matrices=aspect_matrices,
        house_num=1,
        target_house_lord="Mars"
    )
    assert val_unprotected == -10.0

    # Case B: Saturn IS lord of House 1 -> +40.0 Virūpas (Protective!)
    val_protected = calculate_bhava_drishti_bala(
        bhava_madhya_lon=15.0,
        planet_positions={"Saturn": 195.0},
        aspect_matrices=aspect_matrices,
        house_num=1,
        target_house_lord="Saturn"
    )
    assert val_protected == 40.0


def test_whole_sign_tropical_synthesis(calibrated_shadbala):
    """Tests full engine synthesis on tropical Ascendant with sensitive degree."""
    ascendant = 44.5  # 14°30' Taurus
    planets = {
        "Sun": {"lon": 74.5, "is_combust": False},
        "Moon": {"lon": 134.5, "is_combust": False},
        "Mars": {"lon": 194.5, "is_combust": False},
        "Mercury": {"lon": 78.0, "is_combust": False},
        "Jupiter": {"lon": 224.5, "is_combust": False},
        "Venus": {"lon": 44.5, "is_combust": False},
        "Saturn": {"lon": 29.5, "is_combust": False}  # Leaking into H1!
    }
    
    baseline = MockChartBaseline(ascendant, planets)
    res = calculate_bhava_bala(baseline, calibrated_shadbala, house_system="whole_sign")
    
    assert len(res) == 12
    for h in range(1, 13):
        assert "total_virupas" in res[h]
        assert "total_rupas" in res[h]
        assert "augmented_virupas" in res[h]
        assert "dpk_triad" in res[h]
        assert "three_focal_points" in res[h]
        assert res[h]["house"] == h

    # House 1 Taurus
    assert res[1]["sign"] == "Taurus"
    assert res[1]["bhava_madhya"] == 44.5
    assert res[1]["lord"] == "Venus"

    # Wall Leakage Check
    h12_sandhi = res[12]["sandhi_analysis"]
    assert len(h12_sandhi["wall_leakages"]) == 1
    assert h12_sandhi["wall_leakages"][0]["planet"] == "Saturn"
    assert h12_sandhi["wall_leakages"][0]["leakage_direction"] == "forward"
    assert h12_sandhi["wall_leakages"][0]["target_house"] == 1


def test_karako_bhava_nasaya_and_saturn_exception(calibrated_shadbala):
    """Certifies Karako Bhāva Nāśāya detection and Saturn's 8th-house longevity exception."""
    ascendant = 0.0  # Aries
    
    # Chart A: Solitary Jupiter in House 5
    planets_a = {"Jupiter": {"lon": 130.0}}
    res_a = calculate_bhava_bala(MockChartBaseline(ascendant, planets_a), calibrated_shadbala)
    assert res_a[5]["karaka_analysis"]["is_afflicted"] is True

    # Chart B: Solitary Saturn in House 8 (longevity exception)
    planets_b = {"Saturn": {"lon": 220.0}}
    res_b = calculate_bhava_bala(MockChartBaseline(ascendant, planets_b), calibrated_shadbala)
    assert res_b[8]["karaka_analysis"]["is_afflicted"] is False
    assert "promotes longevity" in res_b[8]["karaka_analysis"]["details"].lower()


def test_zero_regression_legacy_format(calibrated_shadbala):
    """Certifies 100% backwards compatibility when invoked with legacy list parameters."""
    cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
    planet_positions = {
        "Sun": 10.0, "Moon": 40.0, "Mars": 70.0, "Mercury": 100.0, 
        "Jupiter": 130.0, "Venus": 160.0, "Saturn": 190.0
    }
    
    res = calculate_bhava_bala(cusps, calibrated_shadbala, planet_positions)
    assert len(res) == 12
    assert res[1]["house"] == 1
    assert res[1]["lord"] == "Mars"
    assert res[1]["total_virupas"] > 0
    assert res[1]["total_rupas"] == round(res[1]["total_virupas"] / 60.0, 2)


def test_bhava_bala_full_chart_integration():
    """Verifies end-to-end integration with full chart generation."""
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
