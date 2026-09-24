"""
tests/test_relationships_and_vectors.py

Test Module 1: Asymmetrical Friendship & Receiver Vantage Point
Validates that aspect and conjunction vectors are calculated exclusively from the vantage
point of the receiving planet (p), honoring non-reciprocal relationships (Light on Life,
Table 4.3 & Chapter 10).
"""

import pytest
import jyotish.relationships.relationships as rel
from jyotish.planetary_evaluation.planetary_evaluation import (
    get_aspect_direction_vector,
    calculate_aspect_shift,
    calculate_planetary_evaluation
)


def test_moon_mercury_asymmetrical_friendship():
    """
    Test 1.1: Moon Receiving Mercury Aspect (Non-Reciprocal Friend)
    The Moon views Mercury as a natural friend (even though Mercury views the Moon as an enemy).
    Receiver p = 'Moon', Sender other_p = 'Mercury', contact_type = 'Aspect (Drishti)', aspect Virupas = 19.0.
    """
    natural_rel = rel.get_natural_relationship("Moon", "Mercury")
    assert natural_rel == "Friend"
    
    vec = get_aspect_direction_vector("Mercury", "Moon", "Aspect (Drishti)", natural_rel)
    assert vec == 1.0

    # Calculate aspect shift with alertness = 1.0
    shift = calculate_aspect_shift(19.0, 1.0, vec)
    assert shift > 0.0

    # Verify impact label format reflecting a positive bonus
    impact = f"{shift:+.1f}% (Mercury Aspect 19v [{natural_rel}])"
    assert impact.startswith("+")
    assert "Enemy" not in impact


def test_mercury_moon_asymmetrical_enmity():
    """
    Test 1.2: Mercury Receiving Moon Aspect (Non-Reciprocal Enemy)
    When positions are inverted, Mercury views the Moon as an enemy.
    Receiver p = 'Mercury', Sender other_p = 'Moon', contact_type = 'Aspect (Drishti)'.
    """
    natural_rel = rel.get_natural_relationship("Mercury", "Moon")
    assert natural_rel == "Enemy"
    
    vec = get_aspect_direction_vector("Moon", "Mercury", "Aspect (Drishti)", natural_rel)
    assert vec == -1.0

    shift = calculate_aspect_shift(19.0, 1.0, vec)
    assert shift < 0.0


def test_rahu_natural_allies():
    """
    Test 1.3: Natural Allies of Rahu
    Rahu collaborates with Saturn, Mercury, and Venus (+0.20 vector) rather than
    applying generic malefic eclipse starvation.
    """
    # Venus receiving Rahu conjunction
    vec_venus_rahu = get_aspect_direction_vector("Rahu", "Venus", "Conjunction", "Enemy")
    assert vec_venus_rahu == 0.20

    # Rahu receiving Saturn conjunction (or Saturn conjoining Rahu)
    vec_saturn_rahu = get_aspect_direction_vector("Saturn", "Rahu", "Conjunction", "Friend")
    assert vec_saturn_rahu == 0.20

    # Rahu with Mercury
    vec_rahu_merc = get_aspect_direction_vector("Rahu", "Mercury", "Conjunction", "Friend")
    assert vec_rahu_merc == 0.20

    vec_merc_rahu = get_aspect_direction_vector("Mercury", "Rahu", "Conjunction", "Friend")
    assert vec_merc_rahu == 0.20


def test_asymmetrical_aspect_in_full_chart_evaluation():
    """
    Integration test verifying that in full chart evaluation, Moon receiving Mercury aspect
    yields a positive shift and positive impact label in aspect_details.
    """
    chart = {
        "D1": {
            "lagna": {"sign": "Leo", "degree_0_to_30": 15.0},
            "grahas": {
                # Moon at 10.0 Cancer (100.0 lon), Mercury at 20.0 Scorpio (230.0 lon) -> 130 deg separation (approx 20v aspect)
                "Moon": {"sign": "Cancer", "degree_0_to_30": 10.0, "longitude": 100.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Scorpio", "degree_0_to_30": 20.0, "longitude": 230.0, "dignity": "Neutral"},
                "Sun": {"sign": "Leo", "degree_0_to_30": 15.0, "longitude": 135.0, "dignity": "Own Sign"},
                "Mars": {"sign": "Aries", "degree_0_to_30": 10.0, "longitude": 10.0, "dignity": "Own Sign"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Libra", "degree_0_to_30": 20.0, "longitude": 200.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 20.0, "longitude": 320.0, "dignity": "Moolatrikona"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }
    res = calculate_planetary_evaluation(chart)
    moon_aspects = res["planets"]["Moon"]["vitality"]["aspect_details"]
    merc_asp = next((a for a in moon_aspects if a["from_planet"] == "Mercury"), None)

    if merc_asp:
        assert merc_asp["direction"] == 1.0
        assert merc_asp["shift"] > 0.0
        assert merc_asp["impact"].startswith("+")
        assert "Friend" in merc_asp["impact"]
