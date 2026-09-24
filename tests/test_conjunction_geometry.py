"""
tests/test_conjunction_geometry.py

Test Module 2: Conjunction Geometry, Border Limits & Nodal Yogas
Validates physical sign boundaries, distance calculations, false wrap-around avoidance,
and classical nodal yoga triggers.
"""

import pytest
import jyotish.aspects.aspects as aspects
from jyotish.planetary_evaluation.planetary_evaluation import (
    get_aspect_direction_vector,
    calculate_graha_vitality,
    calculate_baladi_avastha,
    calculate_planetary_evaluation
)


def test_no_false_wraparound_conjunction():
    """
    Test 2.1: Prevention of the 15° Conjunction Wrap-Around Bug
    Zodiac signs are flat 0° to 30° slices. Planets at 2° and 29° of the same sign
    are separated by 27°, NOT 3°.
    """
    d1_grahas = {
        "Sun": {"sign": "Leo", "degree_0_to_30": 2.0, "longitude": 122.0},
        "Rahu": {"sign": "Leo", "degree_0_to_30": 29.0, "longitude": 149.0}
    }
    diff = abs(d1_grahas["Sun"]["degree_0_to_30"] - d1_grahas["Rahu"]["degree_0_to_30"])
    assert diff == 27.0
    band = "Exact (Intimate)" if diff <= (10.0 / 3.0) else ("Moderate" if diff <= 10.0 else "Wide")
    assert band == "Wide"

    # Evaluate in vitality engine
    baladi = calculate_baladi_avastha("Leo", 2.0)
    vit_res = calculate_graha_vitality(
        planet="Sun",
        sign="Leo",
        degree_in_sign=2.0,
        dignity_name="Own Sign",
        dignity_pct=75.0,
        functional_dignity_pct=75.0,
        host_planet="Sun",
        host_dignity_pct=75.0,
        host_shadbala_pct=100.0,
        planet_shadbala_pct=110.0,
        conjunctions=["Rahu"],
        conjunction_details=[{"planet": "Rahu", "degree_diff": 27.0, "orb_band": "Wide", "shadbala_pct": 100.0, "commands": False}],
        is_retrograde=False,
        is_combust=False,
        is_node=False,
        lagna_sign="Leo",
        lagna_lord="Sun"
    )

    assert vit_res["is_grahan"] is False
    assert vit_res["node_mod"] != -0.25  # Never the intimate penalty
    assert vit_res["node_mod"] == 0.0
    # Efficiency remains unpenalized (not multiplied by 0.80)
    assert vit_res["calculation_receipt"]["efficiency_pct"] == baladi["efficiency_pct"]


def test_grahan_yoga_intimate_separation():
    """
    Test 2.2: Grahan Yoga at Intimate Separation (<= 3°20')
    Input: Sun at 14.0° Aries, Ketu at 15.5° Aries (deg_diff = 1.5°).
    """
    deg_diff = abs(15.5 - 14.0)
    assert deg_diff <= (10.0 / 3.0)
    orb_band = "Exact (Intimate)" if deg_diff <= (10.0 / 3.0) else "Moderate"
    assert orb_band == "Exact (Intimate)"

    baladi = calculate_baladi_avastha("Aries", 14.0)
    expected_eff = int(round(baladi["efficiency_pct"] * 0.80))

    vit_res = calculate_graha_vitality(
        planet="Sun",
        sign="Aries",
        degree_in_sign=14.0,
        dignity_name="Exalted",
        dignity_pct=100.0,
        functional_dignity_pct=100.0,
        host_planet="Mars",
        host_dignity_pct=75.0,
        host_shadbala_pct=100.0,
        planet_shadbala_pct=120.0,
        conjunctions=["Ketu"],
        conjunction_details=[{"planet": "Ketu", "degree_diff": 1.5, "orb_band": "Exact (Intimate)", "shadbala_pct": 100.0, "commands": False}],
        is_retrograde=False,
        is_combust=False,
        is_node=False,
        lagna_sign="Aries",
        lagna_lord="Mars"
    )

    assert vit_res["is_grahan"] is True
    assert "🌑 Grahan Yoga (Sun Eclipsed by Ketu)" in vit_res["affliction_badges"]
    assert vit_res["node_mod"] == -0.25
    assert vit_res["calculation_receipt"]["efficiency_pct"] == expected_eff


def test_guru_ketu_sagittarius_immunity():
    """
    Test 2.3: Ketu + Jupiter in Sagittarius (Universal Dispositor Immunity & Guru-Ketu Yoga)
    Input: Jupiter at 8.0° Sagittarius, Ketu at 9.5° Sagittarius.
    """
    vec = get_aspect_direction_vector("Ketu", "Jupiter", "Conjunction", "Neutral", host_dispositor="Jupiter")
    assert vec == 0.5

    vit_res = calculate_graha_vitality(
        planet="Jupiter",
        sign="Sagittarius",
        degree_in_sign=8.0,
        dignity_name="Own Sign",
        dignity_pct=75.0,
        functional_dignity_pct=75.0,
        host_planet="Jupiter",
        host_dignity_pct=75.0,
        host_shadbala_pct=120.0,
        planet_shadbala_pct=120.0,
        conjunctions=["Ketu"],
        conjunction_details=[{"planet": "Ketu", "degree_diff": 1.5, "orb_band": "Exact (Intimate)", "shadbala_pct": 100.0, "commands": False}],
        is_retrograde=False,
        is_combust=False,
        is_node=False,
        lagna_sign="Sagittarius",
        lagna_lord="Jupiter"
    )

    assert vit_res["is_guru_ketu"] is True
    assert "🕉️ Jñāna Catalyst (Spiritual Discernment)" in vit_res["affliction_badges"]
    # +0.15 for Guru-Ketu yoga and +0.20 for fortified dispositor protection = +0.35
    assert vit_res["node_mod"] == 0.35


def test_adjacent_sign_cross_border_separation():
    """
    Test 2.4: Adjacent Sign Cross-Border Separation
    Input: Mars at 29.5° Aries, Venus at 0.5° Taurus.
    Different signs (p_sign != o_sign) -> must NOT be added to conjunction_details.
    Calculated aspect virūpas between 29.5° and 30.5° evaluate to 0.0 virūpas (2nd house blind spot).
    Neither conjunction shift nor aspect shift is applied.
    """
    p_sign, o_sign = "Aries", "Taurus"
    assert p_sign != o_sign

    # 1. Vedic aspect from 30.5 to 29.5 (1.0 degree distance / 2nd house) is 0 virūpas
    drishti_forward = aspects.get_graha_drishti("Venus", 30.5, 29.5)
    drishti_backward = aspects.get_graha_drishti("Mars", 29.5, 30.5)
    assert drishti_forward == 0.0
    assert drishti_backward == 0.0

    # 2. Integration check in calculate_planetary_evaluation
    chart = {
        "D1": {
            "lagna": {"sign": "Leo", "degree_0_to_30": 15.0},
            "grahas": {
                "Mars": {"sign": "Aries", "degree_0_to_30": 29.5, "longitude": 29.5, "dignity": "Own Sign"},
                "Venus": {"sign": "Taurus", "degree_0_to_30": 0.5, "longitude": 30.5, "dignity": "Own Sign"},
                "Sun": {"sign": "Leo", "degree_0_to_30": 15.0, "longitude": 135.0, "dignity": "Own Sign"},
                "Moon": {"sign": "Cancer", "degree_0_to_30": 10.0, "longitude": 100.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Virgo", "degree_0_to_30": 10.0, "longitude": 160.0, "dignity": "Exalted"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 20.0, "longitude": 320.0, "dignity": "Moolatrikona"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }
    eval_res = calculate_planetary_evaluation(chart)
    mars_vit = eval_res["planets"]["Mars"]["vitality"]
    venus_vit = eval_res["planets"]["Venus"]["vitality"]

    # Venus should NOT be in Mars conjunction_details
    mars_conj = [c for c in mars_vit.get("conjunction_details", []) if c["planet"] == "Venus"]
    assert len(mars_conj) == 0

    # Venus should NOT be in Mars aspect_details (due to 0 virupas blind spot)
    mars_asp = [a for a in mars_vit.get("aspect_details", []) if a.get("from_planet") == "Venus"]
    assert len(mars_asp) == 0

    # Mars should NOT be in Venus conjunction_details
    venus_conj = [c for c in venus_vit.get("conjunction_details", []) if c["planet"] == "Mars"]
    assert len(venus_conj) == 0

    venus_asp = [a for a in venus_vit.get("aspect_details", []) if a.get("from_planet") == "Mars"]
    assert len(venus_asp) == 0
