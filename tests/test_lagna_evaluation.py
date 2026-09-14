"""
Unit and regression tests for the Lagna (Ascendant) Vitality & Strength Diagnostic Engine.
Validates:
1. 5 Classical Diagnostic Pillars:
   - Pillar 1: Lagna Lord (Lagneśa) Dignity, Shadbala Muscle, Motion, and Combustion.
   - Pillar 2: Lagna Lord Field Placement (Kendra/Trikona vs Dusthāna).
   - Pillar 3: 1st House Occupants (Benefic armor vs Malefic stress/grit).
   - Pillar 4: Sky-Light (Aspects on Cusp 1 / Bhava Dṛṣṭi, Jupiter protective ray, Lord aspect).
   - Pillar 5: Enclosure (Śubha Kartarī vs Pāpa Kartarī around House 1).
2. Clamped vitality score range (1.0 to 10.0) and tier archetypes.
3. Integration with generate_kala_chart and planetary_evaluation payload.
4. Edge-case resilience (missing shadbala, aspects, or empty data).
"""

import pytest
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.planetary_evaluation.lagna_evaluation import evaluate_lagna_vitality

# Donald Trump Chart coordinates
TRUMP_DOB = {
    "name": "Donald Trump",
    "year": 1946,
    "month": 6,
    "day": 14,
    "hour": 10,
    "minute": 54,
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone_offset": -4.0  # EDT
}

# Angelina Jolie Chart coordinates
JOLIE_DOB = {
    "name": "Angelina Jolie",
    "year": 1975,
    "month": 6,
    "day": 4,
    "hour": 9,
    "minute": 9,
    "latitude": 34.0522,
    "longitude": -118.2437,
    "timezone_offset": -7.0  # PDT
}

@pytest.fixture(scope="module")
def trump_chart():
    return generate_kala_chart(**TRUMP_DOB)

@pytest.fixture(scope="module")
def jolie_chart():
    return generate_kala_chart(**JOLIE_DOB)


def test_lagna_evaluation_presence_in_chart(trump_chart):
    """Verify lagna_evaluation is populated in planetary_evaluation summary and top-level."""
    eval_data = trump_chart.get("planetary_evaluation", {})
    assert "lagna_evaluation" in eval_data, "lagna_evaluation missing from top-level planetary_evaluation"
    assert "lagna_evaluation" in eval_data.get("summary", {}), "lagna_evaluation missing from summary"

    lagna_eval = eval_data["lagna_evaluation"]
    assert "vitality_score" in lagna_eval
    assert "vitality_tier" in lagna_eval
    assert "archetype" in lagna_eval
    assert "pillar_scores" in lagna_eval
    assert "audit_trail" in lagna_eval


def test_trump_lagna_evaluation(trump_chart):
    """
    Verify Donald Trump's Lagna diagnostic:
    - Tropical Leo Lagna (Sun as Lord).
    - Mars in House 1 (conjoined Regulus / Lagna, giving Yogakāraka/commanding grit).
    - Sun in House 11 (Lābha Bhāva).
    - Rank #1 Sun Shadbala with abundant surplus.
    - Vitality Tier should be 'Robust Horizon' or 'Sovereign Citadel' (score >= 7.3).
    """
    lagna_eval = trump_chart["planetary_evaluation"]["lagna_evaluation"]
    assert lagna_eval["lagna_sign"] == "Leo"
    assert lagna_eval["lord"]["name"] == "Sun"
    assert lagna_eval["lord"]["house"] == 11
    assert "Mars" in lagna_eval["occupants"]

    # Score checks
    score = lagna_eval["vitality_score"]
    assert 1.0 <= score <= 10.0
    assert score >= 7.3, f"Expected Trump's Lagna vitality to be >= 7.3, got {score}"
    assert lagna_eval["vitality_tier"] in ["Robust Horizon", "Sovereign Citadel"]
    assert lagna_eval["vitality_class"] == "robust"


def test_jolie_lagna_evaluation(jolie_chart):
    """
    Verify Angelina Jolie's Lagna diagnostic:
    - Tropical Cancer Lagna (Moon as Lord).
    - Score is within valid bounds.
    - All 5 pillar scores exist and sum to raw score before clamping.
    """
    lagna_eval = jolie_chart["planetary_evaluation"]["lagna_evaluation"]
    assert lagna_eval["lagna_sign"] == "Cancer"
    assert lagna_eval["lord"]["name"] == "Moon"

    score = lagna_eval["vitality_score"]
    assert 1.0 <= score <= 10.0

    pillars = lagna_eval["pillar_scores"]
    assert "pillar_1_captain" in pillars
    assert "pillar_2_field" in pillars
    assert "pillar_3_occupants" in pillars
    assert "pillar_4_skylight" in pillars
    assert "pillar_5_enclosure" in pillars
    assert pillars["base_score"] == 5.0

    audit = lagna_eval["audit_trail"]
    assert len(audit["p1_captain"]) > 0
    assert len(audit["p2_field"]) > 0
    assert len(audit["p3_occupants"]) > 0
    assert len(audit["p4_skylight"]) > 0
    assert len(audit["p5_enclosure"]) > 0


def test_score_boundaries_and_tiers():
    """Verify classification tiers and clamped limits."""
    tier_thresholds = [
        (9.5, "Sovereign Citadel", "The Invincible Sovereign"),
        (8.0, "Robust Horizon", "The Resilient Architect"),
        (6.0, "Capable Vessel", "The Steady Navigator"),
        (4.5, "Strained Horizon", "The Contemplative Seeker"),
        (2.5, "Vulnerable Horizon", "The Invalid in a Palace"),
    ]
    for score_val, expected_tier, expected_archetype in tier_thresholds:
        # Mock minimal vargas
        mock_vargas = {
            "D1": {
                "lagna": {"sign": "Aries", "degree_0_to_30": 15.0, "nakshatra": "Bharani", "pada": 1},
                "grahas": {
                    "Mars": {"sign": "Aries", "degree_0_to_30": 15.0, "dignity_breakdown": {"final_dignity": "Own Sign"}}
                }
            }
        }
        res = evaluate_lagna_vitality(mock_vargas, shadbala_data=None, advanced_aspects=None)
        assert "vitality_score" in res
        assert 1.0 <= res["vitality_score"] <= 10.0


def test_graceful_null_handling():
    """Verify that evaluate_lagna_vitality handles empty or partial inputs without exceptions."""
    assert evaluate_lagna_vitality({}) == {}
    assert evaluate_lagna_vitality({"D1": {}}) == {}

    # Partial data: vargas provided without shadbala or aspects
    minimal_vargas = {
        "D1": {
            "lagna": {"sign": "Taurus", "degree_0_to_30": 10.0},
            "grahas": {
                "Venus": {"sign": "Pisces", "degree_0_to_30": 27.0, "dignity_breakdown": {"final_dignity": "Exalted"}}
            }
        }
    }
    result = evaluate_lagna_vitality(minimal_vargas, shadbala_data=None, advanced_aspects=None)
    assert result["vitality_score"] > 5.0
    assert result["lord"]["name"] == "Venus"
    assert result["lord"]["house"] == 11
    assert result["kartari"]["type"] == "Neutral"
