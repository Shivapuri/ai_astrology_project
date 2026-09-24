"""
tests/test_lagna_vitality_engine.py

Test Module 5: Lagna Vitality Engine & Lajjitādi Deduplication
Validates that multiple friendly or malefic contacts do not stack additively out of bounds
in Ascendant Lord evaluation, verifies Saturn starvation detection, and validates Pillar score boundaries.
"""

import pytest
from jyotish.planetary_evaluation.lagna_evaluation import evaluate_lagna_vitality


def test_lagna_evaluation_mudita_deduplication():
    """
    Test 5.1: Prevention of Multi-Mudita Runaway Score Inflation
    Ascendant Lord aspected by 3 friends (Moon, Mercury, Venus), producing three
    Mudita entries with effective_intensity = 1.0, 0.8, 0.5.
    Asserts max_delighted == 0.40, p1_score increments by exactly +0.40, and
    audit_trail['p1_captain'] contains exactly one Mudita entry.
    """
    vargas_data = {
        "D1": {
            "lagna": {"sign": "Aries", "degree_0_to_30": 15.0},
            "grahas": {
                "Mars": {
                    "sign": "Leo",
                    "degree_0_to_30": 10.0,
                    "dignity_breakdown": {"final_dignity": "Friend's Sign"},
                    "avasthas": {
                        "calibrated_lajjitadi": [
                            {"state": "Mudita", "condition": "Sun aspect", "effective_intensity": 1.0},
                            {"state": "Mudita", "condition": "Moon aspect", "effective_intensity": 0.8},
                            {"state": "Mudita", "condition": "Jupiter aspect", "effective_intensity": 0.5}
                        ]
                    }
                }
            }
        }
    }
    res = evaluate_lagna_vitality(vargas_data)
    mudita_notes = [n for n in res["audit_trail"]["p1_captain"] if "Mudita" in n]
    assert len(mudita_notes) == 1
    assert "(+0.40)" in mudita_notes[0]

    # Without Lajjitadi: Friend's sign gives +0.25, adequate shadbala gives +0.20 -> base p1 = 0.45
    # With deduplicated Mudita: 0.45 + 0.40 = 0.85 (NOT +1.20 which would give 1.65)
    assert res["pillar_scores"]["pillar_1_captain"] == 0.85


def test_multi_source_saturn_starvation_detection():
    """
    Test 5.2: Multi-Source Saturn Starvation Detection
    Saturn starves the Ascendant Lord. The word 'Saturn' is only present in item['state']
    (e.g., 'Kshudhita (via ♄ Saturn)'), and item['condition'] is empty.
    Engine must detect Saturn via badge glyph (♄) or state string, apply -0.80 penalty
    (not generic 0.50), and output 'Lord Starved by Saturn (Kshudhita) (-0.80)' in audit trail.
    """
    vargas_data = {
        "D1": {
            "lagna": {"sign": "Aries", "degree_0_to_30": 15.0},
            "grahas": {
                "Mars": {
                    "sign": "Leo",
                    "degree_0_to_30": 10.0,
                    "dignity_breakdown": {"final_dignity": "Friend's Sign"},
                    "avasthas": {
                        "calibrated_lajjitadi": [
                            {
                                "state": "Kshudhita (via ♄ Saturn)",
                                "condition": "",  # Condition explicitly empty
                                "badge": "⚠️ Kshudhita (via ♄ Saturn)",
                                "effective_intensity": 1.0
                            }
                        ]
                    }
                }
            }
        }
    }
    res = evaluate_lagna_vitality(vargas_data)
    starved_notes = [n for n in res["audit_trail"]["p1_captain"] if "Starved" in n]
    assert len(starved_notes) == 1
    # Must explicitly state "by Saturn" and (-0.80)
    assert "Lord Starved by Saturn (Kshudhita) (-0.80)" in starved_notes[0]

    # Base p1: Friend sign (+0.25) + adequate shadbala (+0.20) - 0.80 = -0.35
    assert res["pillar_scores"]["pillar_1_captain"] == -0.35


def test_pillar_caps_and_clamped_range():
    """
    Verify that total vitality score is strictly clamped to [1.0, 10.0] even under
    extreme positive or extreme negative configurations.
    """
    # Extreme benefic setup
    extreme_positive = {
        "D1": {
            "lagna": {"sign": "Aries", "degree_0_to_30": 15.0},
            "grahas": {
                "Mars": {
                    "sign": "Capricorn",
                    "degree_0_to_30": 28.0,
                    "dignity_breakdown": {"final_dignity": "Exalted"},
                    "is_retrograde": True
                },
                "Jupiter": {
                    "sign": "Aries",
                    "degree_0_to_30": 15.0,
                    "dignity_breakdown": {"final_dignity": "Friend's Sign"}
                },
                "Venus": {
                    "sign": "Aries",
                    "degree_0_to_30": 16.0,
                    "dignity_breakdown": {"final_dignity": "Neutral"}
                }
            }
        }
    }
    res_pos = evaluate_lagna_vitality(extreme_positive)
    assert 1.0 <= res_pos["vitality_score"] <= 10.0

    # Extreme malefic setup
    extreme_negative = {
        "D1": {
            "lagna": {"sign": "Aries", "degree_0_to_30": 15.0},
            "grahas": {
                "Mars": {
                    "sign": "Cancer",
                    "degree_0_to_30": 28.0,
                    "dignity_breakdown": {"final_dignity": "Debilitated"},
                    "is_combust": True,
                    "sun_distance": 1.0,
                    "avasthas": {
                        "calibrated_lajjitadi": [
                            {"state": "Kshudhita (via ♄ Saturn)", "effective_intensity": 1.0},
                            {"state": "Lajjita (Ashamed)", "effective_intensity": 1.0},
                            {"state": "Kshobhita (Agitated)", "effective_intensity": 1.0}
                        ]
                    }
                },
                "Saturn": {
                    "sign": "Aries",
                    "degree_0_to_30": 15.0,
                    "dignity_breakdown": {"final_dignity": "Debilitated"}
                },
                "Rahu": {
                    "sign": "Aries",
                    "degree_0_to_30": 14.0,
                    "dignity_breakdown": {"final_dignity": "Enemy"}
                }
            }
        }
    }
    res_neg = evaluate_lagna_vitality(extreme_negative)
    assert 1.0 <= res_neg["vitality_score"] <= 10.0
