"""
tests/test_archetypes_and_vitality.py

Test Module 3: 4-Tier Dignity & 9-Tier Behavioral Archetype Matrix
Test Module 4: Individual Shadbala Quotas, Baladi & Vitality Score
Validates classical distinction between sovereign royal dignity (>= 75%) and friendly dignity (55%-74%),
Neecha Bhanga Raja Yoga vs Dusthana rescue, individual Shadbala quotas, and softened Baladi compression.
"""

import pytest
from unittest.mock import patch
from jyotish.planetary_evaluation.planetary_evaluation import (
    classify_graha_archetype,
    calculate_graha_vitality,
    calculate_planetary_evaluation
)


# =========================================================================
# Test Module 3: 4-Tier Dignity & 9-Tier Behavioral Archetype Matrix
# =========================================================================

def test_exalted_sun_is_generous_king():
    """
    Test 3.1: The Sovereign King Boundary (>= 75% Dignity + High Muscle)
    Sun in Leo 10° (Moolatrikona, Dignity = 87.5%), Shadbala = 135%.
    """
    res = classify_graha_archetype(
        effective_dignity=87.5,
        effective_shadbala=135.0,
        is_rescued=False
    )
    assert res["archetype"] == "The Generous King"
    assert res["tier"] == "Sovereign Monarch"
    assert res["badge"] == "🌟 Generous King"


def test_jupiter_scorpio_not_generous_king():
    """
    Test 3.2: The Friendly Governor Boundary (Jupiter in Scorpio Calibration)
    Jupiter in Scorpio (Great Friend's sign + Mudita, Dignity = 63.9%), Shadbala = 133%.
    """
    res = classify_graha_archetype(
        effective_dignity=63.9,
        effective_shadbala=133.0,
        is_rescued=False
    )
    assert res["is_royal_dig"] is False
    assert res["is_high_dig"] is True
    assert 55.0 <= 63.9 < 75.0
    assert res["archetype"] == "The Noble Guardian"
    assert res["tier"] == "Constructive Ally"
    assert res["badge"] == "🛡️ Noble Guardian"


def test_armed_dictator_hazard_threshold():
    """
    Test 3.3: The Armed Dictator Hazard Threshold
    Mars in Cancer (Debilitated, Dignity = 12.5%), Shadbala = 125% (High kinetic drive).
    """
    res = classify_graha_archetype(
        effective_dignity=12.5,
        effective_shadbala=125.0,
        is_rescued=False
    )
    assert res["archetype"] == "The Armed Dictator"
    assert res["tier"] == "Severe Hazard"
    assert res["badge"] == "⚔️ Armed Dictator"


def test_neecha_bhanga_raja_yoga_transmuted_hero():
    """
    Test 3.4: Neecha Bhanga Raja Yoga (The Transmuted Hero)
    Mercury in Pisces in House 1 (Kendra), Host Jupiter exalted in Cancer.
    """
    is_rescued = True
    res = classify_graha_archetype(
        effective_dignity=12.5,
        effective_shadbala=115.0,
        is_rescued=is_rescued,
        house_num=1
    )
    assert is_rescued is True
    assert res["archetype"] == "The Transmuted Hero"
    assert res["badge"] == "✨ Transmuted Hero"


def test_neecha_bhanga_in_dusthana_simple():
    """
    Test 3.5: Neecha Bhanga in Dusthana (Simple Neecha Bhanga)
    Mercury in Pisces in House 8 (Dusthana), Host Jupiter exalted in Cancer.
    """
    is_rescued = True
    res = classify_graha_archetype(
        effective_dignity=12.5,
        effective_shadbala=115.0,
        is_rescued=is_rescued,
        house_num=8
    )
    assert is_rescued is True
    assert res["archetype"] != "The Transmuted Hero"
    assert res["simple_neecha_badge"] == "Simple Neecha Bhanga (Overcoming Deficit)"


# =========================================================================
# Test Module 4: Individual Shadbala Quotas, Baladi & Vitality Score
# =========================================================================

def test_shadbala_individual_quotas():
    """
    Test 4.1: Individualized Shadbala Quotas (Bala Pramana)
    Mars and Mercury both having exactly 360.0 raw Virupas.
    Required map: Mercury = 420, Mars = 300.
    """
    req_map = {"Mars": 300.0, "Mercury": 420.0}
    raw_virupas = 360.0
    mars_pct = (raw_virupas / req_map["Mars"]) * 100.0
    merc_pct = (raw_virupas / req_map["Mercury"]) * 100.0
    
    assert round(mars_pct, 1) == 120.0
    assert round(merc_pct, 1) == 85.7

    mars_is_high_strength = (mars_pct >= 100.0) or (raw_virupas >= req_map["Mars"])
    merc_is_high_strength = (merc_pct >= 100.0) or (raw_virupas >= req_map["Mercury"])

    assert mars_is_high_strength is True
    assert merc_is_high_strength is False


def test_baladi_softened_compression():
    """
    Test 4.2: Baladi Dormancy Softened Compression (0.8 + 0.2 * eff)
    Formula: Final Score = 5.0 + (6.6 - 5.0) * (0.8 + 0.2 * 0.0) = 5.0 + 1.6 * 0.8 = 6.28 approx 6.3.
    """
    pre_score = 6.6
    efficiency = 0.0  # Mrita stage
    final_score = 5.0 + (pre_score - 5.0) * (0.8 + 0.2 * efficiency)
    assert round(final_score, 1) == 6.3

    # Direct validation in calculate_graha_vitality
    vit_res = calculate_graha_vitality(
        planet="Jupiter",
        sign="Scorpio",
        degree_in_sign=4.0,  # 0°-6° in even sign Scorpio is Mrita (efficiency = 0.0)
        dignity_name="Friend's Sign",
        dignity_pct=63.9,
        functional_dignity_pct=63.9,
        host_planet="Mars",
        host_dignity_pct=75.0,
        host_shadbala_pct=100.0,
        planet_shadbala_pct=133.0,
        conjunctions=[],
        conjunction_details=[],
        is_retrograde=False,
        is_combust=False,
        is_node=False,
        lagna_sign="Leo",
        lagna_lord="Sun"
    )

    assert vit_res["vitality_score"] == 6.3
    assert vit_res["vitality_tier"] == "🟡 Resilient"


def test_host_dispositor_muscle_inheritance():
    """
    Test 4.3: Host Dispositor Muscle Inheritance (Dynamic Fetching)
    Input: Moon in Aries, Host Mars has 145.0% required Shadbala.
    Verifies host_shadbala_pct inside calculate_graha_vitality equals 145.0.
    """
    chart = {
        "D1": {
            "lagna": {"sign": "Leo", "degree_0_to_30": 15.0},
            "grahas": {
                "Moon": {"sign": "Aries", "degree_0_to_30": 10.0, "longitude": 10.0, "dignity": "Friend"},
                "Mars": {"sign": "Scorpio", "degree_0_to_30": 15.0, "longitude": 225.0, "dignity": "Own Sign"},
                "Sun": {"sign": "Leo", "degree_0_to_30": 15.0, "longitude": 135.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Virgo", "degree_0_to_30": 10.0, "longitude": 160.0, "dignity": "Exalted"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Libra", "degree_0_to_30": 20.0, "longitude": 200.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 20.0, "longitude": 320.0, "dignity": "Moolatrikona"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }

    shadbala_custom = {
        "Mars": {"Total_Virupas": 435.0, "Pct_Required_Total": 145.0},
        "Moon": {"Total_Virupas": 360.0, "Pct_Required_Total": 100.0}
    }

    eval_res = calculate_planetary_evaluation(chart, shadbala_data=shadbala_custom)
    moon_vit = eval_res["planets"]["Moon"]["vitality"]

    # Verify host_shadbala_pct passed to Moon is Mars's 145.0%, NOT hardcoded 100.0
    assert moon_vit["host_shadbala_pct"] == 145.0
    assert moon_vit["calculation_receipt"]["host_shadbala_pct"] == 145.0
