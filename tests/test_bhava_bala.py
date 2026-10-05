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
    calculate_harsha_bala,
    calculate_house_atmosphere,
    _evaluate_karako_bhava_nasaya,
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


def test_combust_lord_aspect_protection_mitigated():
    """Verify that a combust or debilitated lord does not cast full +1.0 aspect protection."""
    # Saturn owning Capricorn (House 10), but combust the Sun
    res = calculate_bhava_drishti_bala(
        bhava_madhya_lon=285.0,
        planet_positions={"Saturn": 15.0, "Sun": 16.0},
        target_house_lord="Saturn",
        combustion_map={"Saturn": True}
    )
    # Fallback aspect from Aries (15°) to Capricorn (285°) is 10th-house aspect (~60 Virupas).
    # Combust scale (0.25) -> ~15.0 Virupas, NOT full 60.0.
    assert res < 30.0


def test_malefic_in_own_sign_not_penalized_in_atmosphere(calibrated_shadbala):
    """Verify that Saturn in Capricorn in House 1 is NOT treated as a hostile malefic occupant."""
    baseline = MockChartBaseline(
        ascendant=275.0,
        planets={"Saturn": {"lon": 285.0, "is_combust": False}}
    )
    bhavas = calculate_bhava_bala(baseline, calibrated_shadbala, house_system="whole_sign")
    atmosphere = calculate_house_atmosphere(baseline, bhavas)
    
    h1_atm = atmosphere[1]
    auspicious_text = " ".join(h1_atm["auspicious_influences"])
    inauspicious_text = " ".join(h1_atm["inauspicious_influences"])
    
    assert "House lord Saturn resident in own sign Capricorn" in auspicious_text
    assert "Malefic occupant Saturn in non-upacaya H1" not in inauspicious_text


def test_karako_bhava_nasaya_living_vs_non_living():
    """Verify Jupiter in 5th triggers affliction, but Jupiter solitary in 11th does NOT."""
    res_h5 = _evaluate_karako_bhava_nasaya(5, [{"name": "Jupiter"}])
    assert res_h5["is_afflicted"] is True

    res_h11 = _evaluate_karako_bhava_nasaya(11, [{"name": "Jupiter"}])
    assert res_h11["is_afflicted"] is False


def test_saturn_in_8th_longevity_exception():
    """Verify Saturn solitary in 8th house does NOT trigger Karako Bhava Nasaya."""
    res_h8 = _evaluate_karako_bhava_nasaya(8, [{"name": "Saturn"}])
    assert res_h8["is_afflicted"] is False
    assert "Āyuṣkāraka" in res_h8["details"]


def test_bhavat_bhavam_6th_displacement_collision_resolved(calibrated_shadbala):
    """
    Certifies that when a house lord is displaced into the 6th from its own sign
    (bhavat_dist == 6), it receives the dusthana penalty and is NOT awarded
    the Upacaya bonus (which is restricted to {3, 10, 11}).
    """
    # Aries Ascendant (0.0°). House 1 lord is Mars.
    # Place Mars in Virgo (160.0°), which is House 6.
    # bhavat_dist = (6 - 1) % 12 + 1 = 6.
    baseline = MockChartBaseline(
        ascendant=0.0,
        planets={"Mars": {"lon": 160.0, "is_combust": False}}
    )
    bhavas = calculate_bhava_bala(baseline, calibrated_shadbala, house_system="whole_sign")
    atmosphere = calculate_house_atmosphere(baseline, bhavas)
    
    h1_lord_status = bhavas[1]["lord_status"]
    assert h1_lord_status["bhavat_bhavam_distance"] == 6
    assert h1_lord_status["is_in_upacaya_from_bhava"] is False
    
    h1_atm = atmosphere[1]
    inauspicious_text = " ".join(h1_atm["inauspicious_influences"])
    auspicious_text = " ".join(h1_atm["auspicious_influences"])
    assert "displaced into 6/8/12 from its own sign (+6h)" in inauspicious_text
    assert "Bhavāt Bhavam Upacaya (+6h)" not in auspicious_text


def test_lord_in_own_dusthana_not_penalized_as_displaced(calibrated_shadbala):
    """
    Certifies that when the lord of a dusthana house (6, 8, or 12) resides in its own sign,
    it is Svastha (forming Viparita/Harsha/Sarala/Vimala Yoga) and NOT penalized with is_in_dusthana=True.
    """
    # Gemini Ascendant (70.0°). House 6 is Scorpio (ruled by Mars).
    # Place Mars in Scorpio (220.0°, House 6).
    baseline = MockChartBaseline(
        ascendant=70.0,
        planets={"Mars": {"lon": 220.0, "is_combust": False}}
    )
    bhavas = calculate_bhava_bala(baseline, calibrated_shadbala, house_system="whole_sign")
    h6_status = bhavas[6]["lord_status"]
    
    assert h6_status["placed_house"] == 6
    assert h6_status["is_in_dusthana"] is False  # Own-house exemption active!


def test_lagnesha_aspect_threshold_major_ray():
    """
    Certifies that Lagnesha aspect must be a major/palpable ray (>= 30.0 Virūpas)
    to trigger the DPK 15.9 flourishing flag.
    """
    # Subtle ray (< 30 Virūpas)
    aspect_matrices_subtle = {"cusp_drishti": {"Mars": {4: 15.0}}}
    baseline_subtle = MockChartBaseline(ascendant=0.0, planets={"Mars": {"lon": 160.0}})
    bhavas_subtle = calculate_bhava_bala(
        baseline_subtle,
        {"Mars": {"Total_Virupas": 350.0, "Dig_Bala": 20.0}},
        aspect_matrices=aspect_matrices_subtle,
        house_system="whole_sign"
    )
    assert bhavas_subtle[4]["lagnesha_aspecting"] is False

    # Major ray (>= 30 Virūpas)
    aspect_matrices_major = {"cusp_drishti": {"Mars": {4: 45.0}}}
    bhavas_major = calculate_bhava_bala(
        baseline_subtle,
        {"Mars": {"Total_Virupas": 350.0, "Dig_Bala": 20.0}},
        aspect_matrices=aspect_matrices_major,
        house_system="whole_sign"
    )
    assert bhavas_major[4]["lagnesha_aspecting"] is True


def test_no_double_counting_lagnesha_in_house_1(calibrated_shadbala):
    """
    Certifies that in House 1, if Lagnesha is resident, the +15.0 bonus is awarded once
    under 'resident in own sign', avoiding double-counting with 'lagnesha_present'.
    """
    baseline = MockChartBaseline(
        ascendant=0.0,  # Aries Lagna, lord Mars
        planets={"Mars": {"lon": 10.0, "is_combust": False}}
    )
    bhavas = calculate_bhava_bala(baseline, calibrated_shadbala, house_system="whole_sign")
    atmosphere = calculate_house_atmosphere(baseline, bhavas)
    
    h1_atm = atmosphere[1]
    auspicious = h1_atm["auspicious_influences"]
    
    own_sign_matches = [x for x in auspicious if "House lord Mars resident in own sign" in x]
    lagnesha_matches = [x for x in auspicious if "Lagnesha present in the house" in x]
    
    assert len(own_sign_matches) == 1
    assert len(lagnesha_matches) == 0  # Not double-counted!


def test_missing_mars_or_saturn_does_not_trigger_phantom_joy():
    """
    Certifies that missing Mars or Saturn in coordinate dict does NOT default to 0.0° Aries,
    which would falsely activate Mars Joy for Scorpio Ascendant or Saturn Joy for Taurus Ascendant.
    """
    # Scorpio Ascendant (asc_sign_idx = 7), Mars completely omitted
    harsha_scorpio = calculate_harsha_bala(
        baseline=None,
        planet_positions={},
        ascendant_lon=225.0,  # Scorpio
        is_day_birth=True
    )
    assert harsha_scorpio["dusthana_joy"][6]["karaka_joy_in_house"] is False
    assert harsha_scorpio["dusthana_joy"][6]["is_active"] is False

    # Taurus Ascendant (asc_sign_idx = 1), Saturn completely omitted
    harsha_taurus = calculate_harsha_bala(
        baseline=None,
        planet_positions={},
        ascendant_lon=45.0,  # Taurus
        is_day_birth=True
    )
    assert harsha_taurus["dusthana_joy"][12]["karaka_joy_in_house"] is False
    assert harsha_taurus["dusthana_joy"][12]["is_active"] is False


