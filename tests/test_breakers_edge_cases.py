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


# =============================================================================
# 7. Batch 1 Audit Regression Tests: pancha_mahapurusha.py & neechabhanga.py
# =============================================================================

from jyotish.yogas.pancha_mahapurusha import detect_pancha_mahapurusha_yogas
from jyotish.yogas.neechabhanga import audit_neecha_bhanga_details, detect_neechabhanga_yogas


def test_pancha_mahapurusha_missing_lagna_rulers_safety():
    """Verify empty/missing lagna rulers dictionary does not raise IndexError."""
    # Chart with no lagna sign, leading get_house_rulers to return {1: []}
    chart_empty = {
        "ascendant": {"sign": ""},
        "planets": {
            "Mars": {"sign": "Capricorn", "longitude": 280.0},
            "Moon": {"sign": "Aries", "longitude": 15.0}
        }
    }
    # Should safely return without IndexError
    yogas = detect_pancha_mahapurusha_yogas(chart_empty)
    assert isinstance(yogas, list)


def test_pancha_mahapurusha_lagna_vs_chandra_scoring_and_confluence():
    """Verify primary Lagna Kendra scores higher than secondary Chandra-only Kendra, and labels are accurate."""
    # Chart 1: Mars in Capricorn in H4 for Libra Lagna, Moon in Gemini (H9).
    # Angular from Lagna (H4), but NOT from Moon (diff = (4 - 9) % 12 + 1 = 8).
    chart_lagna = {
        "ascendant": {"sign": "Libra"},
        "planets": {
            "Mars": {"sign": "Capricorn", "longitude": 280.0},
            "Moon": {"sign": "Gemini", "longitude": 75.0}
        }
    }
    yogas_lagna = detect_pancha_mahapurusha_yogas(chart_lagna)
    ruchaka_lagna = next(y for y in yogas_lagna if y.id == "ruchaka_yoga")
    # Base 80.0 + 10.0 (exalted) = 90.0
    assert ruchaka_lagna.plausibility_score == 90.0
    assert any("Angular prominence: Situated in Kendra House 4" in f for f in ruchaka_lagna.positive_factors)
    assert not any("Also angular from the Moon" in f for f in ruchaka_lagna.positive_factors)

    # Chart 2: Mars in Capricorn in H2 for Sagittarius Lagna, Moon in Libra (H11).
    # Mars is in H2 from Lagna (non-Kendra), but H4 from Moon (Chandra Kendra).
    # Mars is not Lagna lord (Sagittarius is ruled by Jupiter).
    chart_chandra_only = {
        "ascendant": {"sign": "Sagittarius"},
        "planets": {
            "Mars": {"sign": "Capricorn", "longitude": 280.0},
            "Moon": {"sign": "Libra", "longitude": 200.0}
        }
    }
    yogas_chandra = detect_pancha_mahapurusha_yogas(chart_chandra_only)
    ruchaka_chandra = next(y for y in yogas_chandra if y.id == "ruchaka_yoga")
    # Base 70.0 + 10.0 (exalted) = 80.0
    # Lagna Kendra (90.0) strictly scores higher than Chandra-only (80.0)!
    assert ruchaka_chandra.plausibility_score == 80.0
    assert ruchaka_lagna.plausibility_score > ruchaka_chandra.plausibility_score
    assert any("Lunar angularity (indāvapi): Situated in Kendra H4 from the Moon" in f for f in ruchaka_chandra.positive_factors)
    assert not any("Also angular from the Moon" in f for f in ruchaka_chandra.positive_factors)

    # Chart 3: Mars in Capricorn in H1 for Capricorn Lagna, Moon in Aries (H4).
    # Confluence: Angular from BOTH Lagna (H1) and Moon (H10).
    chart_both = {
        "ascendant": {"sign": "Capricorn"},
        "planets": {
            "Mars": {"sign": "Capricorn", "longitude": 280.0},
            "Moon": {"sign": "Aries", "longitude": 15.0}
        }
    }
    yogas_both = detect_pancha_mahapurusha_yogas(chart_both)
    ruchaka_both = next(y for y in yogas_both if y.id == "ruchaka_yoga")
    assert any("Confluence: Also angular from the Moon" in f for f in ruchaka_both.positive_factors)


def test_pancha_mahapurusha_chandra_kendra_in_dusthana_penalized():
    """Verify a Chandra-Kendra Mahapurusha planet trapped in Lagna Dusthana (6, 8, 12) is penalized."""
    # Leo Lagna: Moon in Sagittarius (H5), exalted Venus in Pisces (H8).
    # Venus is in H4 from Moon (Chandra Kendra), but in H8 from Lagna (Dusthana).
    chart = {
        "ascendant": {"sign": "Leo"},
        "planets": {
            "Venus": {"sign": "Pisces", "longitude": 345.0},
            "Moon": {"sign": "Sagittarius", "longitude": 255.0}
        }
    }
    yogas = detect_pancha_mahapurusha_yogas(chart)
    malavya = next((y for y in yogas if y.id == "malavya_yoga"), None)
    assert malavya is not None
    # Dusthana breaker must be flagged
    dusthana_b = next((b for b in malavya.breakers if "Dusthana" in b.factor), None)
    assert dusthana_b is not None
    assert dusthana_b.penalty == 25.0
    # Must NOT be PURE
    assert malavya.status != YogaStatus.PURE
    assert malavya.plausibility_score == 55.0  # 70 (base) + 10 (exalted) - 25 (dusthana)


def test_neechabhanga_moon_tautology_guard():
    """Verify Moon is not considered in Kendra H1 from itself when evaluating dispositor or exaltation lord."""
    # 1. Fallen Mars in Cancer: Dispositor of Cancer is Moon. Moon in Scorpio (H8 for Aries Lagna).
    # Moon in H8 is non-Kendra from Lagna. It must NOT trigger Condition 1 as "in Kendra H1 from Moon".
    chart_mars = {
        "ascendant": {"sign": "Aries"},
        "planets": {
            "Mars": {"sign": "Cancer", "longitude": 105.0},
            "Moon": {"sign": "Scorpio", "longitude": 225.0}  # In H8
        }
    }
    is_rescued, reasons, bonus, meta = audit_neecha_bhanga_details("Mars", chart_mars)
    assert not any("Dispositor in Chandra Kendra" in r for r in reasons)
    assert meta["conditions_met"]["c1"] is False

    # Also verify breakers.audit_neecha_bhanga is synchronized
    is_rescued_b, reasons_b, _ = audit_neecha_bhanga("Mars", chart_mars)
    assert not any("Dispositor in Kendra from Moon" in r for r in reasons_b)

    # 2. Fallen Jupiter in Capricorn: Exaltation sign Cancer, lord Moon. Moon in Scorpio (H8).
    # Moon must NOT trigger Condition 2 as "in Kendra H1 from Moon".
    chart_jup = {
        "ascendant": {"sign": "Aries"},
        "planets": {
            "Jupiter": {"sign": "Capricorn", "longitude": 285.0},
            "Moon": {"sign": "Scorpio", "longitude": 225.0}  # In H8
        }
    }
    is_rescued_j, reasons_j, bonus_j, meta_j = audit_neecha_bhanga_details("Jupiter", chart_jup)
    assert not any("Exaltation Lord in Kendra" in r and "from Moon" in r for r in reasons_j)
    assert meta_j["conditions_met"]["c2"] is False

    # 3. Fallen Moon in Scorpio: Moon in Scorpio in H8 (Aries Lagna).
    # Moon must NOT trigger Condition 6 as "in Kendra H1 from Chandra".
    chart_moon = {
        "ascendant": {"sign": "Aries"},
        "planets": {
            "Moon": {"sign": "Scorpio", "longitude": 225.0}  # In H8
        }
    }
    is_rescued_m, reasons_m, bonus_m, meta_m = audit_neecha_bhanga_details("Moon", chart_moon)
    assert not any("Kendra" in r and "Chandra" in r for r in reasons_m)
    assert meta_m["conditions_met"]["c6"] is False


def test_neechabhanga_venus_virgo_anti_triple_counting():
    """Verify fallen Venus in Virgo is not triple-counted when Mercury is dispositor and exalted in Virgo."""
    # Virgo Lagna: Venus in Virgo (H1). Dispositor Mercury in Sagittarius (H4 Kendra).
    # Jupiter (exaltation lord of Pisces) is in Capricorn (H5, non-Kendra from Lagna and H6 from Moon).
    # Moon in Leo (H12).
    chart = {
        "ascendant": {"sign": "Virgo"},
        "planets": {
            "Venus": {"sign": "Virgo", "longitude": 165.0},      # H1 (Kendra)
            "Mercury": {"sign": "Sagittarius", "longitude": 255.0}, # H4 (Kendra)
            "Jupiter": {"sign": "Capricorn", "longitude": 285.0},  # H5 (non-Kendra from Lagna and Moon)
            "Moon": {"sign": "Leo", "longitude": 135.0}          # H12
        }
    }
    is_rescued, reasons, bonus, meta = audit_neecha_bhanga_details("Venus", chart)
    # Mercury satisfies Condition 1 (+30.0).
    # Mercury must NOT also satisfy Condition 2 as exalted guest (+0).
    # Condition 3 (Dual Lord) must NOT trigger (+0).
    # Venus in H1 satisfies Condition 6 (Angular Fallen Planet, +20.0).
    # Total bonus should be 30 + 20 = 50.0%, NOT 75.0% PURE!
    assert meta["conditions_met"]["c1"] is True
    assert meta["conditions_met"]["c2"] is False
    assert meta["conditions_met"]["c3"] is False
    assert bonus == 50.0


def test_neechabhanga_mercury_pisces_no_self_conjunction():
    """Verify fallen Mercury in Pisces does not treat itself as conjoined with its own exaltation lord."""
    # Sagittarius Lagna: Mercury in Pisces (H4 Kendra). Exaltation lord is Mercury (lord of Virgo).
    # No other planets in H4.
    chart = {
        "ascendant": {"sign": "Sagittarius"},
        "planets": {
            "Mercury": {"sign": "Pisces", "longitude": 345.0},   # H4
            "Jupiter": {"sign": "Taurus", "longitude": 45.0},     # H6
            "Moon": {"sign": "Aries", "longitude": 15.0}         # H5
        }
    }
    is_rescued, reasons, bonus, meta = audit_neecha_bhanga_details("Mercury", chart)
    # Condition 6 should NOT say "alongside its ruler/exaltation lord"
    assert not any("alongside its ruler/exaltation lord" in r for r in reasons)
    # Exaltation lord Mercury already counted under Condition 2A via self; Condition 6 angular bonus skipped
    assert not any("Angular Fallen Planet" in r for r in reasons)
    assert bonus == 30.0


def test_neechabhanga_condition_6_label_from_moon():
    """Verify Condition 6 correctly labels Kendra from Moon when not in Kendra from Lagna."""
    # Scorpio Lagna: Saturn in Aries (H6). Moon in Capricorn (H3).
    # Saturn from Moon: (6 - 3) % 12 + 1 = 4 (Kendra H4 from Chandra).
    chart = {
        "ascendant": {"sign": "Scorpio"},
        "planets": {
            "Saturn": {"sign": "Aries", "longitude": 15.0},       # H6 from Lagna, H4 from Moon
            "Moon": {"sign": "Capricorn", "longitude": 285.0},    # H3
            "Mars": {"sign": "Cancer", "longitude": 105.0}       # H9
        }
    }
    is_rescued, reasons, bonus, meta = audit_neecha_bhanga_details("Saturn", chart)
    c6_reasons = [r for r in reasons if "Condition 6" in r]
    assert len(c6_reasons) == 1
    # Label must reflect Kendra from Chandra (H6), not misleading "Kendra H6 from Lagna"
    assert "Kendra H4 from Chandra (H6)" in c6_reasons[0]


def test_neechabhanga_secondary_breakers_and_rescuing_planets():
    """Verify detect_neechabhanga_yogas applies secondary breakers (combustion) and includes rescuing planets/houses."""
    # Pisces Lagna: Fallen Mercury in Pisces (H1). Dispositor Jupiter in Gemini (H4 Kendra).
    # Mercury is deeply combust with Sun in Pisces (diff = 1.0°).
    chart = {
        "ascendant": {"sign": "Pisces"},
        "planets": {
            "Mercury": {"sign": "Pisces", "longitude": 345.0},
            "Sun": {"sign": "Pisces", "longitude": 346.0},
            "Jupiter": {"sign": "Gemini", "longitude": 75.0},
            "Moon": {"sign": "Aries", "longitude": 15.0}
        }
    }
    yogas = detect_neechabhanga_yogas(chart)
    nb = next((y for y in yogas if "mercury" in y.id), None)
    assert nb is not None
    # Combustion breaker must be recorded
    comb_b = next((b for b in nb.breakers if "Combustion" in b.factor), None)
    assert comb_b is not None
    assert comb_b.penalty == 40.0
    # Must NOT be PURE despite being in Kendra H1
    assert nb.status != YogaStatus.PURE
    # Rescuing planet Jupiter and its house H4 must be in participating lists
    assert "Jupiter" in nb.participating_planets
    assert 4 in nb.participating_houses


def test_neechabhanga_mercury_pisces_dual_lord_requires_distinct_planet():
    """Verify Mercury in Pisces does not trigger Condition 3 Dual Lord Prominence via self-lordship."""
    # Chart A: Pisces Lagna, Mercury in Pisces (H1), Jupiter in Gemini (H4). Venus in Taurus (H3, non-Kendra).
    # Mercury satisfies C2 via self, Jupiter satisfies C1.
    # C3 Dual Lord must NOT trigger because C2 is not satisfied by a distinct planet.
    chart_a = {
        "ascendant": {"sign": "Pisces"},
        "planets": {
            "Mercury": {"sign": "Pisces", "longitude": 345.0},   # H1 (Kendra)
            "Jupiter": {"sign": "Gemini", "longitude": 75.0},     # H4 (Kendra)
            "Venus": {"sign": "Taurus", "longitude": 45.0},       # H3 (non-Kendra)
            "Moon": {"sign": "Aries", "longitude": 15.0}         # H2
        }
    }
    is_rescued_a, reasons_a, bonus_a, meta_a = audit_neecha_bhanga_details("Mercury", chart_a)
    assert meta_a["conditions_met"]["c1"] is True
    assert meta_a["conditions_met"]["c2"] is True
    assert meta_a["conditions_met"]["c3"] is False  # NOT met via self!
    assert not any("Dual Lord Prominence" in r for r in reasons_a)

    # Chart B: Move Venus (exalted in Pisces) to Sagittarius (H10 Kendra, not co-occupying H1).
    # Now Venus is distinct from dispositor Jupiter and fallen Mercury, occupying Kendra.
    # Condition 3 MUST trigger!
    chart_b = {
        "ascendant": {"sign": "Pisces"},
        "planets": {
            "Mercury": {"sign": "Pisces", "longitude": 345.0},      # H1 (Kendra)
            "Jupiter": {"sign": "Gemini", "longitude": 75.0},        # H4 (Kendra)
            "Venus": {"sign": "Sagittarius", "longitude": 255.0},   # H10 (Kendra)
            "Moon": {"sign": "Aries", "longitude": 15.0}            # H2
        }
    }
    is_rescued_b, reasons_b, bonus_b, meta_b = audit_neecha_bhanga_details("Mercury", chart_b)
    assert meta_b["conditions_met"]["c1"] is True
    assert meta_b["conditions_met"]["c2"] is True
    assert meta_b["conditions_met"]["c3"] is True   # Met via distinct Venus!
    assert any("Dual Lord Prominence" in r for r in reasons_b)


def test_neechabhanga_exalted_co_occupant_anti_triple_counting():
    """Verify exalted Sun sharing Aries with fallen Saturn is scored under C5, not also C2B and C6 alongside lord."""
    # Aries Lagna: Saturn in Aries (H1), Sun in Aries (H1, exalted).
    # Moon in Leo (H5).
    # Mars in Gemini (H3 -> H11 from Moon, non-Kendra from both).
    # Venus in Sagittarius (H9 -> H5 from Moon, non-Kendra from both).
    chart = {
        "ascendant": {"sign": "Aries"},
        "planets": {
            "Saturn": {"sign": "Aries", "longitude": 15.0},
            "Sun": {"sign": "Aries", "longitude": 10.0},          # Exalted co-occupant in H1
            "Mars": {"sign": "Gemini", "longitude": 75.0},        # H3 (non-Kendra from Lagna and Moon)
            "Venus": {"sign": "Sagittarius", "longitude": 255.0}, # H9 (non-Kendra from Lagna and Moon)
            "Moon": {"sign": "Leo", "longitude": 135.0}           # H5
        }
    }
    is_rescued, reasons, bonus, meta = audit_neecha_bhanga_details("Saturn", chart)
    # Sun is scored under Condition 5 (+35.0)
    assert meta["conditions_met"]["c5"] is True
    # Sun must NOT also be scored under Condition 2B (+0)
    assert meta["conditions_met"]["c2"] is False
    # Saturn in H1 gets Condition 6 angular bonus (+20.0), NOT +30.0 alongside lord
    assert meta["conditions_met"]["c6"] is True
    assert not any("alongside its ruler/exaltation lord" in r for r in reasons)
    # Total bonus must be 35.0 (C5) + 20.0 (C6) = 55.0%, NOT 95.0%!
    assert bonus == 55.0


def test_neechabhanga_conjoined_with_moon_in_non_lagna_kendra():
    """Verify fallen Mars in Cancer conjoined with Moon in H3 is rescued in both neechabhanga and breakers."""
    # Taurus Lagna: fallen Mars in Cancer (H3), Moon in Cancer (H3).
    # Mars is in Kendra H1 from Chandra alongside dispositor Moon.
    chart = {
        "ascendant": {"sign": "Taurus"},
        "planets": {
            "Mars": {"sign": "Cancer", "longitude": 105.0},
            "Moon": {"sign": "Cancer", "longitude": 108.0}
        }
    }
    # 1. Check neechabhanga.audit_neecha_bhanga_details
    is_rescued_nb, reasons_nb, bonus_nb, _ = audit_neecha_bhanga_details("Mars", chart)
    assert is_rescued_nb is True
    assert bonus_nb >= 30.0

    # 2. Check breakers.audit_neecha_bhanga
    is_rescued_br, reasons_br, bonus_br = audit_neecha_bhanga("Mars", chart)
    assert is_rescued_br is True
    assert bonus_br >= 30.0
    assert any("from Moon" in r for r in reasons_br)


def test_pancha_mahapurusha_capped_pre_breaker_score_major_breaker_not_pure():
    """Verify pre-breaker score is capped at 100.0, and major breakers (penalty >= 20.0) prevent PURE status."""
    # Scorpio Lagna: Mars in Scorpio (H1).
    # Base 80 + own sign 10 + Kendra H1 5 + Kendra from Moon 5 + Lagna lord 10 = 110.0 pre-breaker!
    # Sun is in Scorpio at 214.0° (Mars is at 210.0°, diff = 4.0° -> Moderate combustion, penalty = 20.0).
    chart = {
        "ascendant": {"sign": "Scorpio"},
        "planets": {
            "Mars": {"sign": "Scorpio", "longitude": 210.0},
            "Sun": {"sign": "Scorpio", "longitude": 214.0},     # 4° apart -> Moderate combustion
            "Moon": {"sign": "Taurus", "longitude": 45.0}       # H7 Kendra from Lagna and Moon
        }
    }
    yogas = detect_pancha_mahapurusha_yogas(chart)
    ruchaka = next(y for y in yogas if y.id == "ruchaka_yoga")
    # Score capped at min(100.0, 110.0) - 20.0 = 80.0
    assert ruchaka.plausibility_score == 80.0
    # Because combustion breaker has penalty 20.0, status must NOT be PURE
    assert ruchaka.status == YogaStatus.STAINED


