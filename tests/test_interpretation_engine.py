"""
tests/test_interpretation_engine.py
Unit tests for the Sequential Planetary Interpretation & Macro Canvas Synthesis Engine.
"""

import pytest
from typing import Dict, Any
from jyotish.report.interpretation_engine import (
    synthesize_background_canvas,
    decompose_planet_5_pillars,
    evaluate_semantic_dynamics,
    apply_macro_canvas_filter,
    modulate_tone_with_dignity,
    generate_planetary_interpretations,
    compute_harmonic_overlays
)


def test_synthesize_background_canvas():
    """Verify that background canvas synthesizes the 4 foundational spectrums."""
    mock_polarity_core = {
        "relationship": {"state": "Harmonic Flow", "friction_score": 15}
    }
    mock_operational_axis = {
        "is_vargottama": False
    }
    mock_env_tally = {
        "polarity": {
            "percentages": {"Active": 65.0, "Passive": 35.0}
        },
        "elements": {
            "percentages": {"Fire": 40.0, "Earth": 15.0, "Air": 30.0, "Water": 15.0}
        }
    }
    mock_nak_dominance = {
        "temperament_breakdown": [
            {"group": "Tikshna", "percentage": 25.0},
            {"group": "Ugra", "percentage": 25.0},
            {"group": "Mridu", "percentage": 10.0},
            {"group": "Chara", "percentage": 10.0},
            {"group": "Dhruva", "percentage": 15.0},
            {"group": "Laghu", "percentage": 15.0}
        ]
    }

    canvas = synthesize_background_canvas(
        mock_polarity_core, mock_operational_axis, mock_env_tally, mock_nak_dominance
    )

    # 1. Introversion vs Extroversion (Active 65.0% -> Extroverted)
    assert "Extroverted" in canvas["introversion_extroversion"]["state"]
    assert canvas["introversion_extroversion"]["active_percentage"] == 65.0

    # 2. Practicality vs Idealism (Fire 40 + Air 30 = 70.0% Idealistic)
    assert "Visionary" in canvas["practicality_idealism"]["state"]
    assert canvas["practicality_idealism"]["idealistic_percentage"] == 70.0

    # 3. Defiance vs Cooperation (Tikshna 25 + Ugra 25 = 50.0% vs Mridu 10 + Chara 10 = 20.0%)
    assert "Assertive" in canvas["defiance_cooperation"]["state"]
    assert canvas["defiance_cooperation"]["defiance_percentage"] == 50.0

    # 4. Intellectual vs Emotional (Air 30 > Water 15)
    assert "Intellectual" in canvas["intellectual_emotional"]["state"]

    assert len(canvas["narrative_overview"]) > 50


def test_decompose_planet_5_pillars():
    """Verify that a planet decomposes into all 5 architectural pillars."""
    d1_graha = {"sign": "Aries", "degree_0_to_30": 12.5}
    nak_data = {"nakshatra": "Ashwini", "pada": 4, "nakshatra_lord": "Ketu", "group": "Laghu"}
    ruled = [1, 8]
    house_num = 1

    pillars = decompose_planet_5_pillars("Mars", d1_graha, nak_data, ruled, house_num)

    assert pillars["pillar_1_symbolism"]["natural_element"] == "Fire"
    assert pillars["pillar_2_sign"]["sign"] == "Aries"
    assert pillars["pillar_2_sign"]["element"] == "Fire"
    assert pillars["pillar_3_house"]["house"] == 1
    assert pillars["pillar_4_nakshatra"]["name"] == "Ashwini"
    assert pillars["pillar_5_lordships"]["ruled_houses"] == [1, 8]


def test_semantic_dynamics_resonances_and_clashes():
    """
    Verify Commonalities (Resonances) and Clashes (Dissonances)
    evaluated strictly through Elements and Modalities.
    """
    # Case 1: Mars (Fire, Movable) in Aries (Fire, Movable) in 1st House (Fire, Movable)
    pillars_aligned = {
        "pillar_1_symbolism": {"natural_element": "Fire", "natural_modality": "Movable"},
        "pillar_2_sign": {"sign": "Aries", "element": "Fire", "modality": "Movable"},
        "pillar_3_house": {"house": 1, "house_element": "Fire", "house_modality": "Movable"}
    }
    res_aligned = evaluate_semantic_dynamics(pillars_aligned)
    assert res_aligned["resonance_count"] >= 2
    assert res_aligned["clash_count"] == 0
    assert res_aligned["balance_status"] == "Harmonic Gift Flow"

    # Case 2: Mars (Fire, Movable) in Cancer (Water, Movable) in 4th House (Water, Movable)
    pillars_clash = {
        "pillar_1_symbolism": {"natural_element": "Fire", "natural_modality": "Movable"},
        "pillar_2_sign": {"sign": "Cancer", "element": "Water", "modality": "Movable"},
        "pillar_3_house": {"house": 4, "house_element": "Water", "house_modality": "Movable"}
    }
    res_clash = evaluate_semantic_dynamics(pillars_clash)
    assert res_clash["clash_count"] >= 1
    assert any("Fire vs. Water" in c for c in res_clash["clashes"])


def test_tone_modulation_via_read_only_dignity():
    """Verify that dignity scores set the psychological tone without modifying math."""
    dignity_high = {
        "expression_mode": "Constructive",
        "net_scale_score": 1.25,
        "deeptadi": {"state": "Pramudita"}
    }
    tone_high = modulate_tone_with_dignity(dignity_high)
    assert tone_high["mode"] == "Constructive"
    assert "Noble" in tone_high["tone_color"]

    dignity_low = {
        "expression_mode": "Challenging",
        "net_scale_score": -1.10,
        "deeptadi": {"state": "Khala"}
    }
    tone_low = modulate_tone_with_dignity(dignity_low)
    assert tone_low["mode"] == "Challenging"
    assert "Protective" in tone_low["tone_color"]


def test_generate_planetary_interpretations_order_and_commander():
    """
    Verify that interpretations follow the Prominence Leaderboard sequence,
    designating Rank 1 as #1 Chart Commander (Kārakādhipati).
    """
    mock_prominence = {
        "leaderboard": [
            {"planet": "Jupiter", "prominence_score": 2.45},
            {"planet": "Sun", "prominence_score": 1.80},
            {"planet": "Mars", "prominence_score": 1.20}
        ]
    }
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Sagittarius"},
            "grahas": {
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 15.0},
                "Sun": {"sign": "Leo", "degree_0_to_30": 10.0},
                "Mars": {"sign": "Aries", "degree_0_to_30": 5.0}
            }
        }
    }
    mock_nakshatras = {
        "Jupiter": {"nakshatra": "Mula", "pada": 1, "group": "Tikshna"},
        "Sun": {"nakshatra": "Magha", "pada": 2, "group": "Ugra"},
        "Mars": {"nakshatra": "Ashwini", "pada": 3, "group": "Laghu"}
    }
    mock_canvas = {
        "introversion_extroversion": {"state": "Extroverted"},
        "practicality_idealism": {"state": "Visionary"}
    }

    interpretations = generate_planetary_interpretations(
        mock_prominence, mock_vargas, mock_nakshatras, {}, mock_canvas
    )

    assert len(interpretations) == 3
    # First is Jupiter with Rank 1 and Chart Commander flag
    assert interpretations[0]["planet"] == "Jupiter"
    assert interpretations[0]["rank"] == 1
    assert interpretations[0]["is_chart_commander"] is True
    assert "Chart Commander" in interpretations[0]["role_designation"]

    # Second is Sun with Rank 2
    assert interpretations[1]["planet"] == "Sun"
    assert interpretations[1]["rank"] == 2
    assert interpretations[1]["is_chart_commander"] is False


def test_compute_harmonic_overlays():
    """
    Verify harmonic projection formula: (lon * N) % 360
    and detection of contacts <= 3°20' (3.33°).
    """
    # Suppose natal Sun is at 10.0° Aries (10.0° longitude).
    # D9 projection of Sun = (10.0 * 9) % 360 = 90.0° (0.0° Cancer).
    # Suppose natal Moon is at 91.5° (1.5° Cancer).
    # Distance between D9 Sun (90.0°) and natal Moon (91.5°) = 1.5° <= 3.33°.
    # This should trigger a D9 Sun conjoining natal Moon contact!
    mock_vargas = {"D1": {"lagna": {"longitude": 0.0}, "grahas": {}}}
    d1_lons = {
        "Sun": 10.0,
        "Moon": 91.5,
        "Mars": 200.0
    }

    overlays = compute_harmonic_overlays(mock_vargas, d1_longitudes=d1_lons)
    contacts = overlays["contacts"]

    sun_to_moon = [c for c in contacts if c["harmonic_planet"] == "Sun" and c["natal_target"] == "Moon" and c["harmonic_chart"] == "D9"]
    assert len(sun_to_moon) == 1
    assert sun_to_moon[0]["harmonic_degree"] == 90.0
    assert sun_to_moon[0]["orb_separation"] == 1.5
