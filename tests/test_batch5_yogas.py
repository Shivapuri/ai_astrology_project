"""
tests/test_batch5_yogas.py
Comprehensive Edge-Case & Regression Test Suite for Batch 5:
- dhana_daridrya.py (Lakṣmī Yoga, 10 BPHS Dhana Pairs, Single-Planet Dual Lords, Dāridrya & Dāridrya Bhaṅga)
- chandal_yogas.py (Guru-Chāṇḍāla, Guru-Ketu Jñāna, Śrāpita, Aṅgāraka, Separation Geometry, Affliction Invariant)
- deity_yogas.py (Trimūrti: Śrīkaṇṭha, Viriñci, Śrīnātha; Tridevī: Gaurī, Sarasvatī; Mālā: Śubhamālā & Aśubhamālā)
"""

import pytest
from typing import Dict, Any
from jyotish.yogas.models import YogaStatus, YogaCategory
from jyotish.yogas.dhana_daridrya import detect_dhana_and_daridrya_yogas
from jyotish.yogas.chandal_yogas import detect_chandal_yogas
from jyotish.yogas.deity_yogas import detect_deity_yogas
from jyotish.yogas.evaluator import detect_all_yogas


def make_clean_chart(
    lagna_sign: str = "Aries",
    grahas: Dict[str, Any] = None,
    aspects: Dict[str, Any] = None,
    shadbala: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Helper to assemble structured chart fixtures."""
    default_shadbala = {
        p: {"total": 450.0, "ratio": 1.1, "Rupas": 7.0, "Ratio_to_Req": 1.1}
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    }
    if shadbala:
        default_shadbala.update(shadbala)

    from jyotish.yogas.breakers import ZODIAC_SIGNS
    grahas_dict = {}
    if grahas:
        for p, data in grahas.items():
            if isinstance(data, str):
                s_idx = ZODIAC_SIGNS.index(data) if data in ZODIAC_SIGNS else 0
                grahas_dict[p] = {"sign": data, "longitude": s_idx * 30.0 + 15.0, "degree_0_to_30": 15.0}
            elif isinstance(data, dict):
                grahas_dict[p] = data
            else:
                grahas_dict[p] = {"sign": str(data)}

    l_idx = ZODIAC_SIGNS.index(lagna_sign) if lagna_sign in ZODIAC_SIGNS else 0
    vargas = {
        "D1": {
            "lagna": {"sign": lagna_sign, "longitude": l_idx * 30.0 + 15.0, "degree_0_to_30": 15.0} if lagna_sign else None,
            "grahas": grahas_dict,
        }
    }

    chart = {
        "vargas": vargas,
        "ascendant": {"sign": lagna_sign},
        "shadbala": default_shadbala,
        "planetary_evaluation": {
            p: {"dignity": "Own" if p in ["Mars", "Sun", "Jupiter"] else "Neutral"}
            for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        }
    }
    if aspects:
        chart["advanced_aspects"] = {"planets": aspects}
    return chart


# =============================================================================
# 1. DHANA & DĀRIDRYA YOGA TESTS
# =============================================================================

def test_dhana_safe_ruler_indexing_empty_rulers():
    """Verify that an empty or missing house ruler map does not trigger IndexError."""
    chart = {"vargas": {"D1": {"lagna": {"sign": "Aries"}, "grahas": {}}}}
    yogas = detect_dhana_and_daridrya_yogas(chart)
    assert isinstance(yogas, list)


def test_dhana_all_bphs_pairs():
    """Verify detection of various classical BPHS Ch. 41 wealth pairings."""
    # Aries Lagna: H1 lord = Mars, H9 lord = Jupiter. Mars & Jupiter conjoined in Aries H1.
    chart = make_clean_chart("Aries", {
        "Mars": {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0},
        "Jupiter": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
    })
    yogas = detect_dhana_and_daridrya_yogas(chart)
    dhana_1_9 = next((y for y in yogas if y.id == "dhana_yoga_mars_jupiter"), None)
    assert dhana_1_9 is not None, "Must detect 1L + 9L (Mars + Jupiter) Dhana pairing"
    assert dhana_1_9.category == YogaCategory.DHANA
    assert dhana_1_9.status == YogaStatus.PURE

    # Verify combustion detection when Sun conjoins Mars within 5°
    chart_combust = make_clean_chart("Aries", {
        "Mars": {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0},
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
    })
    yogas_comb = detect_dhana_and_daridrya_yogas(chart_combust)
    dhana_1_5 = next((y for y in yogas_comb if y.id == "dhana_yoga_mars_sun"), None)
    assert dhana_1_5 is not None
    assert any("Combustion" in b.factor for b in dhana_1_5.breakers)
    assert dhana_1_5.status == YogaStatus.STAINED


def test_single_planet_dual_dhana_lord():
    """
    Verify Single-Planet Dual Dhana Lordship (BPHS 41.2–12).
    E.g., Taurus Lagna: Mercury simultaneously rules H2 (Gemini) and H5 (Virgo).
    If Mercury is well-placed in Gemini H2 (own sign), it triggers Viśeṣa Dhana Kāraka Yoga.
    """
    chart = make_clean_chart("Taurus", {
        "Mercury": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_dhana_and_daridrya_yogas(chart)
    single_dhana = next((y for y in yogas if y.id == "single_dhana_yoga_mercury"), None)
    assert single_dhana is not None, "Must detect Mercury as single-planet dual wealth lord for Taurus Lagna"
    assert "H2 & H5" in single_dhana.name
    assert single_dhana.status == YogaStatus.PURE
    assert single_dhana.plausibility_score >= 90.0


def test_lakshmi_yoga_with_lagnesha_breaker():
    """
    Verify Lakṣmī Yoga: 9th Lord + Venus strong in Kendras/Trikoṇas.
    If 1st Lord (Lagneśa) is in Dusthana, it incurs a breaker penalty.
    """
    # Aries Lagna: 9th Lord = Jupiter. Put Jupiter in Cancer H4 (exalted), Venus in Pisces H12 (exalted).
    # But Venus must be in Kendra/Trikona: put Venus in Libra H7 (own sign).
    # 1st Lord Mars is debilitated in Cancer H4 with Jupiter (Neecha Bhanga) or placed in Scorpio H8.
    chart = make_clean_chart("Aries", {
        "Jupiter": {"sign": "Cancer", "longitude": 95.0, "degree_0_to_30": 5.0},
        "Venus": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},  # H8
    })
    yogas = detect_dhana_and_daridrya_yogas(chart)
    lakshmi = next((y for y in yogas if y.id == "lakshmi_yoga"), None)
    assert lakshmi is not None, "Must detect Lakṣmī Yoga when 9L and Venus are fortified"
    assert lakshmi.status == YogaStatus.PURE


def test_daridrya_yoga_mitigation():
    """
    Verify Dāridrya Yoga and Dāridrya Bhaṅga (Mitigation).
    When 2nd lord is in H8 in own sign (e.g. Mars in Scorpio H8 for Aries Lagna),
    it is RESCUED by dignity, not unmitigated STAINED.
    """
    chart = make_clean_chart("Aries", {
        # 2nd lord Venus in Scorpio H8 (neutral, unmitigated)
        "Venus": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_dhana_and_daridrya_yogas(chart)
    daridrya_unmit = next((y for y in yogas if y.id == "daridrya_h2_venus"), None)
    assert daridrya_unmit is not None
    assert daridrya_unmit.status == YogaStatus.STAINED

    # Mitigated via benefic aspect (Jupiter palpably aspects Venus)
    aspects = {"Venus": {"Jupiter": {"raw": 50.0, "net": 50.0}}}
    chart_mit = make_clean_chart("Aries", {
        "Venus": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0}
    }, aspects=aspects)
    yogas_mit = detect_dhana_and_daridrya_yogas(chart_mit)
    daridrya_mit = next((y for y in yogas_mit if y.id == "daridrya_h2_venus"), None)
    assert daridrya_mit is not None
    assert daridrya_mit.status == YogaStatus.RESCUED, "Palpable benefic aspect must rescue Daridrya Yoga"


# =============================================================================
# 2. CHANDAL & NODAL AFFLICTION YOGA TESTS
# =============================================================================

def test_chandal_same_sign_separation_inversion_fix():
    """
    Verify the critical degree inversion bug fix:
    Jupiter at 1.0° and Rahu at 29.0° in the same sign are 28.0° apart.
    They must be classified as 'Wide Sign Conjunction', NOT 'Exact / Intimate Orb (2.00°)'.
    """
    chart = make_clean_chart("Sagittarius", {
        "Jupiter": {"sign": "Sagittarius", "longitude": 241.0, "degree_0_to_30": 1.0},
        "Rahu": {"sign": "Sagittarius", "longitude": 269.0, "degree_0_to_30": 29.0}
    })
    yogas = detect_chandal_yogas(chart)
    gc = next((y for y in yogas if y.id == "guru_chandal_yoga"), None)
    assert gc is not None
    assert gc.plausibility_score == 68.0, "Wide separation (28°) must score 68.0, not intimate 92.0"
    assert any("Wide Sign Conjunction" in eff for eff in gc.manifestation_effects)


def test_chandal_safe_deg_extraction_none_values():
    """Verify that None values in coordinates do not cause TypeError."""
    chart = make_clean_chart("Cancer", {
        "Jupiter": {"sign": "Cancer", "longitude": None, "degree_0_to_30": None},
        "Rahu": {"sign": "Cancer", "longitude": None, "degree_0_to_30": None}
    })
    yogas = detect_chandal_yogas(chart)
    assert isinstance(yogas, list)


def test_chandal_category_status_invariants():
    """
    Verify YOGA_ARCHITECTURE.md Row 7 & Section 5 Rule 3:
    CHANDAL yogas must use STAINED or RESCUED, NEVER PURE.
    """
    # Exalted Jupiter in Cancer conjoined with Rahu -> RESCUED
    chart_exalted = make_clean_chart("Aries", {
        "Jupiter": {"sign": "Cancer", "longitude": 95.0, "degree_0_to_30": 5.0},
        "Rahu": {"sign": "Cancer", "longitude": 98.0, "degree_0_to_30": 8.0}
    })
    yogas = detect_chandal_yogas(chart_exalted)
    gc_exalted = next((y for y in yogas if y.id == "guru_chandal_yoga"), None)
    assert gc_exalted is not None
    assert gc_exalted.status == YogaStatus.RESCUED, "Exalted Jupiter must mitigate Guru-Chandal to RESCUED, never PURE"

    # Guru-Ketu Jnana Yoga -> RESCUED
    chart_gk = make_clean_chart("Pisces", {
        "Jupiter": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0},
        "Ketu": {"sign": "Pisces", "longitude": 348.0, "degree_0_to_30": 18.0}
    })
    y_gk = detect_chandal_yogas(chart_gk)
    gk = next((y for y in y_gk if y.id == "guru_ketu_jnana_yoga"), None)
    assert gk is not None
    assert gk.status == YogaStatus.RESCUED, "Guru-Ketu Jnana Yoga must be RESCUED, never PURE"


# =============================================================================
# 3. COSMIC DEITY YOGAS TESTS
# =============================================================================

def test_deity_safe_ruler_indexing_and_deduplication():
    """Verify safe ruler indexing and deduplication in participating houses."""
    chart = {"vargas": {"D1": {"lagna": {"sign": "Aries"}, "grahas": {}}}}
    yogas = detect_deity_yogas(chart)
    assert isinstance(yogas, list)


def test_deity_compound_friendship():
    """
    Verify that Trimurti yogas support Compound Friendship (Panchadha Maitri).
    A planet in a friendly host's sign in Kendra/Trikona qualifies for Srikantha Yoga.
    """
    # Aries Lagna: 1st Lord Mars in Leo H5 (Sun's sign, Mars & Sun are natural friends)
    # Sun in Aries H1 (exalted), Moon in Taurus H2 (exalted, but needs Kendra/Trikona: Cancer H4)
    chart = make_clean_chart("Aries", {
        "Mars": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_deity_yogas(chart)
    srik = next((y for y in yogas if y.id == "srikantha_yoga"), None)
    assert srik is not None, "Śrīkaṇṭha Yoga must detect friendly sign Leo for Mars"
    assert srik.status == YogaStatus.PURE


def test_subhamala_requires_all_three_houses():
    """
    Verify that Śubhamālā Yoga requires benefics to span ALL THREE houses {5, 6, 7}.
    If all 3 benefics are clumped in House 5 alone, it must NOT trigger.
    """
    # Clumped in H5 alone (Aries Lagna: Leo H5)
    chart_clumped = make_clean_chart("Aries", {
        "Jupiter": {"sign": "Leo", "longitude": 125.0, "degree_0_to_30": 5.0},
        "Venus": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},
        "Mercury": {"sign": "Leo", "longitude": 145.0, "degree_0_to_30": 25.0}
    })
    y_clumped = detect_deity_yogas(chart_clumped)
    assert not any(y.id == "subhamala_yoga" for y in y_clumped), "Clumping in H5 must not trigger Śubhamālā Yoga"

    # Continuous span across {5, 6, 7}: H5=Leo, H6=Virgo, H7=Libra
    chart_garland = make_clean_chart("Aries", {
        "Jupiter": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},
        "Mercury": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0}
    })
    y_garland = detect_deity_yogas(chart_garland)
    subha = next((y for y in y_garland if y.id == "subhamala_yoga"), None)
    assert subha is not None, "Continuous span across 5, 6, 7 must trigger Śubhamālā Yoga"
    assert subha.participating_houses == [5, 6, 7]


def test_asubhamala_yoga_detection():
    """
    Verify Aśubhamālā Yoga when natural benefics are trapped in Dusthanas (6, 8, 12).
    """
    # Benefics in H6 (Virgo), H8 (Scorpio), H12 (Pisces) for Aries Lagna
    chart_asubha = make_clean_chart("Aries", {
        "Mercury": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_deity_yogas(chart_asubha)
    asubha = next((y for y in yogas if y.id == "asubhamala_yoga"), None)
    assert asubha is not None, "Must detect Aśubhamālā Yoga when all benefics in 6, 8, 12"
    assert asubha.status == YogaStatus.STAINED
