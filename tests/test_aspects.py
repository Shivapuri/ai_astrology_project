import pytest
from jyotish.baseline import ChartBaseline
from jyotish.aspects.aspects import (
    get_rasi_drishti,
    get_graha_drishti,
    get_all_graha_drishtis,
    get_all_rasi_drishtis,
    calculate_advanced_graha_aspects,
    calculate_aspect_matrices,
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


def test_bphs_sphuta_drishti_milestones():
    """
    Verifies BPHS 26.6–12 Sphuṭa Dṛṣṭi Exact Milestones:
    - Standard planet (Sun) yields:
      0.0 at 30°, 15.0 at 60°, 45.0 at 90°, 30.0 at 120°,
      0.0 at 150°, 60.0 at 180°, 30.0 at 240°, and 0.0 at 300°.
    - Special aspects peak at 60.0 Virūpas:
      Saturn at 60° (3rd) and 270° (10th);
      Jupiter at 120° (5th) and 240° (9th);
      Mars at 90° (4th) and across the entire 180°–210° span (सदाऽङ्गभे रूपं per BPHS 26.11).
    """
    # 1. Standard planet (Sun) milestones per BPHS 26.6-9
    assert get_graha_drishti("Sun", 0.0, 30.0) == 0.0
    assert get_graha_drishti("Sun", 0.0, 60.0) == 15.0
    assert get_graha_drishti("Sun", 0.0, 90.0) == 45.0
    assert get_graha_drishti("Sun", 0.0, 120.0) == 30.0
    assert get_graha_drishti("Sun", 0.0, 150.0) == 0.0
    assert get_graha_drishti("Sun", 0.0, 180.0) == 60.0
    assert get_graha_drishti("Sun", 0.0, 240.0) == 30.0
    assert get_graha_drishti("Sun", 0.0, 300.0) == 0.0

    # 2. Saturn special aspects (60° and 270°) per BPHS 26.10
    assert get_graha_drishti("Saturn", 0.0, 60.0) == 60.0
    assert get_graha_drishti("Saturn", 0.0, 270.0) == 60.0

    # 3. Jupiter special aspects (120° and 240°) per BPHS 26.12
    assert get_graha_drishti("Jupiter", 0.0, 120.0) == 60.0
    assert get_graha_drishti("Jupiter", 0.0, 240.0) == 60.0

    # 4. Mars special aspects (90° and continuous 180°–210° span) per BPHS 26.11
    assert get_graha_drishti("Mars", 0.0, 90.0) == 60.0
    for deg in [180.0, 185.0, 190.0, 195.0, 200.0, 205.0, 210.0]:
        assert get_graha_drishti("Mars", 0.0, deg) == 60.0, f"Mars at {deg}° must be 60.0 Virūpas"


def test_moon_dynamic_benefic_malefic_parity():
    """
    Verifies that a dark/waning Moon (e.g. moon_lon = 320.0, sun_lon = 0.0, diff = 320.0°)
    is classified as malefic (minus) in calculate_advanced_graha_aspects, matching calculate_aspect_matrices.
    """
    # In calculate_advanced_graha_aspects:
    planets_data = {
        "Sun": {"longitude": 0.0, "sign": "Aries"},
        "Moon": {"longitude": 320.0, "sign": "Aquarius"},  # diff = 320°, waning/dark Moon
        "Jupiter": {"longitude": 140.0, "sign": "Leo"},     # receives 180° opposition from Moon
    }
    # Test without passing shadbala_data to verify default parameter hygiene
    res_adv = calculate_advanced_graha_aspects(planets_data)
    jup_from_moon = res_adv["planets"]["Jupiter"]["Moon"]
    assert jup_from_moon["raw"] == 60.0
    assert jup_from_moon["plus"] == 0.0
    assert jup_from_moon["minus"] == 60.0
    assert jup_from_moon["net"] == -60.0

    # In calculate_aspect_matrices (Native Kailash has dark/waning Moon with elongation 338.96°):
    kailash = ChartBaseline("Kailash", 1987, 11, 19, 16, 0, 0, 52.20296, 8.0448, 1.0)
    res_mat = calculate_aspect_matrices(kailash)
    assert res_mat["benefic_malefic_totals"]["classification"]["Moon"] is False
    # And check that passing kailash.coordinates to calculate_advanced_graha_aspects produces exact parity
    adv_kailash = calculate_advanced_graha_aspects(kailash.coordinates)
    assert adv_kailash["planets"]["Jupiter"]["Moon"]["plus"] == 0.0
    assert adv_kailash["planets"]["Jupiter"]["Moon"]["minus"] > 0.0


def test_mercury_dynamic_malefic_conjunction_and_cross_border_combustion():
    """
    Verifies that Mercury becomes a functional malefic per BPHS 3.11 & Phaladīpikā 2.27 when:
    1. Conjoined in the same sign with a dark/waning Moon (Kṣīṇendu).
    2. Combust across a sign border (e.g. Sun at 29° Aries, Mercury at 4° Taurus within 14° orb).
    """
    # 1. Mercury conjoined with dark/waning Moon in the same sign (Sun is distant so Mercury is not combust)
    planets_dark_moon = {
        "Sun": {"longitude": 60.0, "sign": "Gemini"},
        "Moon": {"longitude": 320.0, "sign": "Aquarius"},   # diff from Sun = (320 - 60)%360 = 260° (waning Krishna paksha, <50% illumination)
        "Mercury": {"longitude": 315.0, "sign": "Aquarius"},# in Aquarius with dark Moon! (distance from Sun is 105° -> not combust)
        "Jupiter": {"longitude": 135.0, "sign": "Leo"},     # receives 180° opposition from Mercury
    }
    res_dark_moon = calculate_advanced_graha_aspects(planets_dark_moon)
    jup_from_merc = res_dark_moon["planets"]["Jupiter"]["Mercury"]
    assert jup_from_merc["raw"] == 60.0
    assert jup_from_merc["plus"] == 0.0
    assert jup_from_merc["minus"] == 60.0
    assert jup_from_merc["net"] == -60.0

    # 2. Cross-border combustion: Sun at 29.0° (Aries), Mercury at 34.0° (4° Taurus) -> separation 5.0° <= 14.0°
    planets_combust_cross_border = {
        "Sun": {"longitude": 29.0, "sign": "Aries"},
        "Moon": {"longitude": 180.0, "sign": "Libra"},       # bright/full Moon
        "Mercury": {"longitude": 34.0, "sign": "Taurus"},     # 4° Taurus, combust across border from Sun at 29° Aries
        "Jupiter": {"longitude": 214.0, "sign": "Scorpio"},   # receives 180° opposition from Mercury
    }
    res_combust = calculate_advanced_graha_aspects(planets_combust_cross_border)
    jup_from_merc_comb = res_combust["planets"]["Jupiter"]["Mercury"]
    assert jup_from_merc_comb["raw"] == 60.0
    assert jup_from_merc_comb["plus"] == 0.0
    assert jup_from_merc_comb["minus"] == 60.0
    assert jup_from_merc_comb["net"] == -60.0

    # Verify cross-border combustion in calculate_aspect_matrices via real baseline (2021-04-19):
    # Sun is in Aries (29.65°), Mercury is in Taurus (30.13°)
    b_combust = ChartBaseline("CrossBorderCombust", 2021, 4, 19, 12, 0, 0, 0.0, 0.0, 0.0)
    mat_combust = calculate_aspect_matrices(b_combust)
    assert b_combust.coordinates["Sun"]["sign"] == "Aries"
    assert b_combust.coordinates["Mercury"]["sign"] == "Taurus"
    assert b_combust.combustion_status["Mercury"]["is_combust"] is True
    assert mat_combust["benefic_malefic_totals"]["classification"]["Mercury"] is False


def test_unequal_cusp_sign_lord_protection():
    """
    Verifies that in calculate_advanced_graha_aspects, when an unequal house_cusps entry
    has cusp longitude in Scorpio (215.0°), Mars's aspect on that cusp is scored as plus
    (protective house lord) even if ascendant_lon is None.
    """
    planets_data = {
        "Mars": {"longitude": 35.0, "sign": "Taurus"},  # 180° opposition to 215.0° = 60.0 Virūpas
        "Sun": {"longitude": 0.0, "sign": "Aries"},
    }
    house_cusps = [
        {"longitude": 215.0}  # House 1 cusp at 215.0° (Scorpio, ruled by Mars)
    ]
    res = calculate_advanced_graha_aspects(
        planets_data=planets_data,
        house_cusps=house_cusps,
        ascendant_lon=None  # Explicitly None to test unequal / Bhāva Chalita mode without Lagna
    )
    cusp1_mars = res["cusps"][1]["Mars"]
    assert cusp1_mars["raw"] == 60.0
    assert cusp1_mars["plus"] == 60.0
    assert cusp1_mars["minus"] == 0.0
    assert cusp1_mars["net"] == 60.0
    assert res["totals"]["cusps"][1]["plus"] == 60.0


def test_phaladipika_15_1_qualification():
    """
    Verifies that in calculate_aspect_matrices:
    - Default unattenuated envelope (totals_cusps) counts a malefic house lord's aspect on its own cusp as plus.
    - DPK 15.1 qualified envelope (cusps_dpk_qualified via नीचमूढारिहीनैः) classifies a natural malefic
      house lord's aspect on its own cusp as benefic_virupas ONLY when unafflicted, but as malefic_virupas
      when that lord is debilitated, combust, or in an enemy sign.
    """
    # 1. Impaired malefic house lord: Native Shivapuri
    # Lagna is Leo. H9 is Aries, ruled by Mars. Mars in Virgo is in an enemy sign (Mercury is enemy of Mars).
    shivapuri = ChartBaseline(
        name="Shivapuri",
        year=1983, month=11, day=10, hour=22, minute=20, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0,
        nakshatra_system="ERNST_DHRUVA"
    )
    aspects = calculate_aspect_matrices(shivapuri)
    h9_default = aspects["benefic_malefic_totals"]["cusps"][9]
    h9_dpk = aspects["benefic_malefic_totals"]["cusps_dpk_qualified"][9]

    # Under default unattenuated rule: Mars (60.0) is added to benefic_virupas (173.51)
    assert pytest.approx(h9_default["benefic_virupas"], abs=0.01) == 173.51
    assert h9_default["malefic_virupas"] < 60.0

    # Under DPK 15.1 qualified rule: Mars in Virgo is in enemy sign, so 60.0 is transferred to malefic_virupas
    assert pytest.approx(h9_dpk["benefic_virupas"], abs=0.01) == 113.51
    assert pytest.approx(h9_dpk["malefic_virupas"], abs=0.01) == 111.48

    # When enforce_dpk_lord_qualifications=True, cusps uses the qualified envelope directly
    aspects_enforced = calculate_aspect_matrices(shivapuri, enforce_dpk_lord_qualifications=True)
    assert aspects_enforced["benefic_malefic_totals"]["cusps"][9] == h9_dpk

    # 2. Unafflicted malefic house lord:
    unafflicted_chart = ChartBaseline(
        name="UnafflictedMarsLord",
        year=1985, month=1, day=15, hour=12, minute=0, second=0,
        latitude=0.0, longitude=0.0, timezone_offset=0.0
    )
    res_unafflicted = calculate_aspect_matrices(unafflicted_chart)
    dpk_qual = res_unafflicted["benefic_malefic_totals"]["cusps_dpk_qualified"]
    # Check that cusps_dpk_qualified is present for all 12 houses
    assert len(dpk_qual) == 12
    for h in range(1, 13):
        assert "benefic_virupas" in dpk_qual[h]
        assert "malefic_virupas" in dpk_qual[h]
        assert "net_virupas" in dpk_qual[h]

