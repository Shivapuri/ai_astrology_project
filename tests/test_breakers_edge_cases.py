"""
tests/test_breakers_edge_cases.py
Targeted regression and edge case tests for:
1. Sphuta Drishti & Aspect Gradients (get_aspect_score)
2. Combustion Auditing (audit_combustion)
3. Neecha Bhanga Cancellation & Lagna resolution (audit_neecha_bhanga, audit_neecha_bhanga_condition_3, get_lagna_sign)
4. Trishadaya Saboteurs (audit_trishadaya_interference, _first_ruler)
5. Data Models serialization robustness (YogaInstance.to_dict)
"""

import pytest
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_aspect_score, _extract_virupas,
    audit_combustion,
    get_lagna_sign, audit_neecha_bhanga_condition_3, audit_neecha_bhanga,
    audit_trishadaya_interference, _first_ruler,
    get_house_of_planet,
    audit_dispositor_vitality, audit_shadbala_muscle
)


# =============================================================================
# 1. Sphuta Drishti & Aspect Score Edge Cases
# =============================================================================

def test_extract_virupas_edge_cases():
    """Verify _extract_virupas handles None, dicts with None values, clamping, and malformed inputs."""
    assert _extract_virupas(None) == 0.0
    assert _extract_virupas({}) == 0.0
    assert _extract_virupas({"raw": None, "net": 48.0}) == 48.0
    assert _extract_virupas({"raw": -22.5}) == 0.0  # Clamped to 0.0
    assert _extract_virupas({"raw": 75.0}) == 60.0  # Clamped to 60.0
    assert _extract_virupas({"net": None, "plus": "35.5"}) == 35.5
    assert _extract_virupas("invalid") == 0.0
    assert _extract_virupas(45.0) == 45.0


def test_get_aspect_score_none_safety():
    """Verify get_aspect_score handles missing advanced_aspects or None values gracefully."""
    # 1. chart is None or empty
    assert get_aspect_score(None, "Mars", "Saturn") == 0.0
    assert get_aspect_score({}, "Mars", "Saturn") == 0.0
    assert get_aspect_score({"advanced_aspects": None}, "Mars", "Saturn") == 0.0

    # 2. planets dict contains None values
    chart_with_none = {
        "advanced_aspects": {
            "planets": {
                "Saturn": {"Mars": {"raw": None, "net": 48.0}}
            }
        }
    }
    assert get_aspect_score(chart_with_none, giver="Mars", receiver="Saturn") == 48.0

    # 3. Lagna checks with None cusps
    chart_lagna = {
        "advanced_aspects": {
            "planets": None,
            "lagna": {"Jupiter": 50.0},
            "cusps": None
        }
    }
    assert get_aspect_score(chart_lagna, giver="Jupiter", receiver="Lagna") == 50.0


# =============================================================================
# 2. Combustion Auditing Edge Cases
# =============================================================================

def test_audit_combustion_non_dict_comb_status():
    """Verify combustion status as a boolean, None, or string does not crash."""
    chart = {
        "combustion_status": {"Venus": True, "Mars": None},
        "planets": {
            "Sun": {"longitude": 10.0},
            "Venus": {"longitude": 11.0, "sun_distance": 1.0},
            "Mars": {"longitude": 50.0, "sun_distance": 40.0}
        }
    }
    breakers = audit_combustion(["Venus", "Mars"], chart)
    assert len(breakers) == 1
    assert breakers[0].culprit_planet == "Sun"
    assert "Venus" in breakers[0].description
    assert "Deep Planetary Combustion" in breakers[0].factor


def test_audit_combustion_signed_elongation_and_wrap_around():
    """Verify negative sun_distance does not falsely trigger combustion, and 0° wrap-around works."""
    # Negative sun_distance: planet trailing Sun by 14° (-14.0)
    chart_trailing = {
        "planets": {
            "Sun": {"longitude": 20.0},
            "Mercury": {"longitude": 6.0, "sun_distance": -14.0}
        }
    }
    breakers_trailing = audit_combustion(["Mercury"], chart_trailing)
    assert len(breakers_trailing) == 0, "Planet trailing Sun by 14° is not combust"

    # Wrap-around across 0° Aries: Sun at 359° Pisces, Mercury at 1.5° Aries (distance = 2.5°)
    chart_boundary = {
        "planets": {
            "Sun": {"longitude": 359.0},
            "Mercury": {"longitude": 1.5}
        }
    }
    breakers_boundary = audit_combustion(["Mercury"], chart_boundary)
    assert len(breakers_boundary) == 1
    assert "Deep Planetary Combustion" in breakers_boundary[0].factor
    assert breakers_boundary[0].penalty == 40.0


def test_audit_combustion_exclusions():
    """Verify Sun, Nodes, and Ascendant are safely excluded from combustion check."""
    chart = {
        "planets": {
            "Sun": {"longitude": 10.0},
            "Rahu": {"longitude": 10.5},
            "Ketu": {"longitude": 190.5}
        }
    }
    breakers = audit_combustion(["Sun", "Rahu", "Ketu", "Lagna", "Ascendant"], chart)
    assert len(breakers) == 0


# =============================================================================
# 3. Neecha Bhanga Cancellation & Lagna Edge Cases
# =============================================================================

def test_get_lagna_sign_missing_safety():
    """Verify get_lagna_sign returns '' instead of faking 'Aries' when chart has no ascendant."""
    assert get_lagna_sign({}) == ""
    assert get_lagna_sign({"vargas": None}) == ""
    assert get_lagna_sign({"ascendant": None}) == ""
    assert get_lagna_sign({"ascendant": {"sign": None}}) == ""
    assert get_lagna_sign({"ascendant": {"sign": "Leo"}}) == "Leo"


def test_audit_neecha_bhanga_missing_dispositor_house_safety():
    """Verify missing dispositor (house=0) does not trigger false positive Kendra from Moon."""
    # Chart with fallen Saturn in Aries, but dispositor Mars is missing from planets data
    # Moon in Gemini (House 3)
    chart = {
        "ascendant": {"sign": "Virgo"},
        "planets": {
            "Saturn": {"sign": "Aries"},
            "Moon": {"sign": "Scorpio"}  # Moon in House 3 for Virgo Lagna
        }
    }
    is_rescued, reasons, bonus = audit_neecha_bhanga("Saturn", chart)
    # Dispositor Mars is missing, so disp_house == 0.
    # Without fix: (0 - 3) % 12 + 1 == 10, which was falsely in (1, 4, 7, 10)!
    assert not any("Dispositor in Kendra from Moon" in r for r in reasons)


def test_audit_neecha_bhanga_condition_3_self_lordship():
    """Verify Mercury in Pisces (House 1) rescues itself via Condition 3A without double-counting Condition 6."""
    # Pisces Lagna: Mercury in Pisces (House 1, fallen). Exaltation sign Virgo, lord Mercury.
    # Dispositor of Pisces is Jupiter, placed in House 3 (Taurus, non-Kendra).
    # Moon placed in House 2 (Aries).
    chart = {
        "ascendant": {"sign": "Pisces"},
        "planets": {
            "Mercury": {"sign": "Pisces"},
            "Jupiter": {"sign": "Taurus"},
            "Moon": {"sign": "Aries"}
        }
    }
    met, desc = audit_neecha_bhanga_condition_3("Mercury", "Pisces", chart)
    assert met is True
    assert "Mercury" in desc
    assert "Kendra H1" in desc

    # In audit_neecha_bhanga, Mercury is rescued with exactly 30.0 bonus (Condition 6 skipped)
    is_rescued, reasons, bonus = audit_neecha_bhanga("Mercury", chart)
    assert is_rescued is True
    assert bonus == 30.0
    assert any("Condition 3" in r for r in reasons)
    assert not any("Angular fallen planet" in r for r in reasons)


def test_audit_neecha_bhanga_condition_3_standalone_rescue():
    """Verify Condition 3 awards +30.0 and standalone rescues the fallen planet."""
    # Fallen Sun in Libra (debilitated). Dispositor Venus in 6th (Pisces, exalted).
    # Exaltation sign Aries, lord Mars in Kendra H10 (Cancer).
    chart = {
        "ascendant": {"sign": "Libra"},
        "planets": {
            "Sun": {"sign": "Libra"},         # H1
            "Venus": {"sign": "Pisces"},      # H6 (disp not in Kendra)
            "Mars": {"sign": "Cancer"},       # H10 (exaltation lord in Kendra from Lagna)
            "Moon": {"sign": "Sagittarius"}   # H3
        }
    }
    is_rescued, reasons, bonus = audit_neecha_bhanga("Sun", chart)
    assert is_rescued is True
    assert bonus >= 30.0
    assert any("Condition 3" in r for r in reasons)


# =============================================================================
# 4. Trishadaya Interference Edge Cases
# =============================================================================

def test_audit_trishadaya_invalid_lagna_index_error():
    """Verify invalid lagna sign does not cause IndexError in _first_ruler."""
    chart = {"ascendant": {"sign": "InvalidSign"}}
    breakers = audit_trishadaya_interference(["Sun", "Jupiter"], chart)
    assert isinstance(breakers, list)
    assert len(breakers) == 0


def test_audit_trishadaya_dual_lord_deduplication():
    """Verify dual Trishadaya lords (e.g. Mars ruling H6 and H11 for Gemini Lagna) are penalized only once."""
    # Gemini Lagna: Mars rules 6 (Scorpio) and 11 (Aries).
    # Put Mars conjoined with Sun in Gemini H1.
    chart = {
        "ascendant": {"sign": "Gemini"},
        "planets": {
            "Sun": {"sign": "Gemini"},
            "Jupiter": {"sign": "Gemini"},
            "Mars": {"sign": "Gemini"}  # Saboteur conjoined!
        }
    }
    breakers = audit_trishadaya_interference(["Sun", "Jupiter"], chart)
    mars_breakers = [b for b in breakers if b.culprit_planet == "Mars"]
    assert len(mars_breakers) == 1, "Mars must only be penalized once as primary saboteur (11th Lord), not twice"
    assert mars_breakers[0].penalty == 40.0


def test_audit_trishadaya_selects_strongest_interference_across_planets():
    """Verify that when saboteur has a marginal aspect on planet 1 and conjunction on planet 2, conjunction is selected."""
    # Aries Lagna: Saturn rules 11.
    # Yoga planets: ["Moon", "Jupiter"].
    # Saturn in Cancer (H4) conjoining Jupiter in Cancer (H4).
    # Moon in Aries (H1) receiving 35 Virupa aspect from Saturn.
    chart = {
        "ascendant": {"sign": "Aries"},
        "planets": {
            "Moon": {"sign": "Aries"},
            "Jupiter": {"sign": "Cancer"},
            "Saturn": {"sign": "Cancer"}  # Conjoined Jupiter
        },
        "advanced_aspects": {
            "planets": {
                "Moon": {"Saturn": 35.0}  # Marginal aspect
            }
        }
    }
    breakers = audit_trishadaya_interference(["Moon", "Jupiter"], chart)
    saturn_breaker = next((b for b in breakers if b.culprit_planet == "Saturn"), None)
    assert saturn_breaker is not None
    # Conjunction (40.0) should override marginal aspect
    assert saturn_breaker.penalty == 40.0
    assert "conjoins Jupiter" in saturn_breaker.description


# =============================================================================
# 5. YogaInstance.to_dict Robustness
# =============================================================================

def test_yoga_instance_to_dict_robustness():
    """Verify YogaInstance.to_dict handles raw strings, None breakers, and dict breakers."""
    inst = YogaInstance(
        id="test_yoga",
        name="Test Yoga",
        category="Raja Yoga",  # raw string instead of Enum
        status="Pure & Eminent",  # raw string instead of Enum
        plausibility_score=150.0,  # overflow clamped to 100.0
        participating_planets=["Sun", "Moon"],
        participating_houses=[1, 5],
        scripture_ref="BPHS",
        archetype="Test archetype",
        manifestation_effects=["Effect 1"],
        positive_factors=["Factor 1"],
        breakers=[
            None,  # None breaker
            {"factor": "Manual Breaker", "culprit_planet": "Mars", "description": "Manual", "penalty": 20.0},
            YogaBreakerDetail(factor="Typed Breaker", culprit_planet="Saturn", description="Typed", penalty=30.0)
        ]
    )
    d = inst.to_dict()
    assert d["id"] == "test_yoga"
    assert d["category"] == "Raja Yoga"
    assert d["status"] == "Pure & Eminent"
    assert d["plausibility_score"] == 100.0  # Clamped
    assert len(d["breakers"]) == 2
    assert d["breakers"][0]["factor"] == "Manual Breaker"
    assert d["breakers"][1]["factor"] == "Typed Breaker"


# =============================================================================
# 6. Dispositor Vitality & Shadbala Muscle Polish Tests
# =============================================================================

def test_audit_dispositor_vitality_deduplication():
    """Verify conjoined yoga planets sharing a debilitated/dusthana dispositor are penalized only once."""
    # Leo Lagna: Sun (H1 lord) and Mars (H9 lord) conjoined in Taurus (H10).
    # Dispositor of Taurus is Venus.
    # Venus is in Virgo (H2, debilitated) without cancellation.
    chart = {
        "ascendant": {"sign": "Leo"},
        "planets": {
            "Sun": {"sign": "Taurus"},
            "Mars": {"sign": "Taurus"},
            "Venus": {"sign": "Virgo"},  # Debilitated dispositor in 2nd
            "Moon": {"sign": "Aries"}
        }
    }
    breakers = audit_dispositor_vitality(["Sun", "Mars"], chart)
    venus_breakers = [b for b in breakers if b.culprit_planet == "Venus"]
    # Shared host Venus must be penalized once (-25.0), not twice (-50.0)
    assert len(venus_breakers) == 1
    assert venus_breakers[0].penalty == 25.0
    assert "Debilitated Host Dispositor" in venus_breakers[0].factor


def test_audit_shadbala_muscle_robustness():
    """Verify audit_shadbala_muscle handles None shadbala and None/string inner keys safely."""
    # 1. chart["shadbala"] is None
    breakers_none, notes_none = audit_shadbala_muscle(["Sun", "Moon"], {"shadbala": None})
    assert breakers_none == []
    assert notes_none == []

    # 2. inner keys are None or malformed
    chart_malformed = {
        "shadbala": {
            "Sun": {"Rupas": None, "Ratio_to_Req": None},
            "Moon": {"Rupas": "invalid", "Ratio_to_Req": "invalid"},
            "Mars": {"Rupas": 0.70, "Ratio_to_Req": 0.70},  # Low muscle (< 0.85)
            "Jupiter": {"Rupas": 1.40, "Ratio_to_Req": 1.30}  # Muscular (>= 1.25)
        }
    }
    breakers, notes = audit_shadbala_muscle(["Sun", "Moon", "Mars", "Jupiter"], chart_malformed)
    assert len(breakers) == 1
    assert breakers[0].culprit_planet == "Mars"
    assert breakers[0].penalty == 15.0
    assert len(notes) == 1
    assert "Jupiter is muscular in Shadbala" in notes[0]
