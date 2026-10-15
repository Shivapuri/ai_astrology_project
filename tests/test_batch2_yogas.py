"""
tests/test_batch2_yogas.py
Targeted edge case and regression test suite for Batch 2:
- raja_yogas.py (Single-Planet Yogakāraka, Multi-Planet Alliances, Intervening Planets, Dispositor Vitality, Breaker Gating)
- parivartana.py (Maha, Khala, Dainya, Viparita Crossovers, Null Lagna Safety, Layer 2 Breakers)
- viparita.py (Harsha, Sarala, Vimala, Scripture References, Co-Rulership Guards, Strongest Contamination, Layer 2 Breakers)
"""

import pytest
from typing import Dict, Any
from jyotish.yogas.models import YogaStatus, YogaCategory
from jyotish.yogas.raja_yogas import detect_raja_yogas, audit_intervening_planet
from jyotish.yogas.parivartana import detect_parivartana_yogas
from jyotish.yogas.viparita import detect_viparita_raja_yogas


def make_test_chart(
    lagna_sign: str,
    grahas: Dict[str, Dict[str, Any]],
    aspects: Dict[str, Any] = None,
    shadbala: Dict[str, Dict[str, Any]] = None,
    combustion_status: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Helper to assemble a clean chart payload for testing yoga edge cases."""
    default_shadbala = {
        p: {"total": 450.0, "ratio": 1.0, "Rupas": 6.5, "Ratio_to_Req": 1.1}
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    }
    if shadbala:
        default_shadbala.update(shadbala)

    return {
        "vargas": {
            "D1": {
                "lagna": {"sign": lagna_sign, "longitude": 15.0, "degree_0_to_30": 15.0} if lagna_sign else None,
                "grahas": grahas
            }
        },
        "advanced_aspects": {"planets": aspects or {}},
        "shadbala": default_shadbala,
        "combustion_status": combustion_status or {}
    }


# =============================================================================
# PART 1: RAJA YOGAS TESTS
# =============================================================================

def test_raja_audit_dispositor_vitality_multi_planet():
    """1.1: If conjoined Raja Yoga planets have a debilitated dispositor, it must trigger Debilitated Host Dispositor."""
    # Gemini Lagna: 1st lord Mercury and 5th lord Venus conjoin in Cancer (H2).
    # Host dispositor Moon is in Scorpio (H6) debilitated without Neecha Bhanga (Mars in Libra H5).
    chart = make_test_chart("Gemini", {
        "Mercury": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Cancer", "longitude": 110.0, "degree_0_to_30": 20.0},
        "Moon": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_raja_yogas(chart)
    sh = next((y for y in yogas if "shankha_yoga" in y.id), None)
    assert sh is not None
    disp_breaker = next((b for b in sh.breakers if b.factor == "Debilitated Host Dispositor"), None)
    assert disp_breaker is not None, "Debilitated host dispositor Moon must trigger breaker"
    assert disp_breaker.culprit_planet == "Moon"
    assert disp_breaker.penalty == 25.0
    assert sh.status != YogaStatus.PURE, "Yoga with 25% breaker cannot be Pure"


def test_raja_audit_dispositor_vitality_single_planet():
    """1.1: Single-Planet Yogakaraka must audit host dispositor vitality."""
    # Cancer Lagna: Mars is Yogakaraka (rules H5 & H10).
    # Mars is in Taurus (H11).
    # Dispositor Venus is trapped in Gemini (H12 Dusthana).
    chart = make_test_chart("Cancer", {
        "Mars": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},    # H11
        "Venus": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0}    # Dispositor in H12 Dusthana
    })
    yogas = detect_raja_yogas(chart)
    yk = next((y for y in yogas if "single_yogakaraka_mars" in y.id), None)
    assert yk is not None
    disp_breaker = next((b for b in yk.breakers if "Host Dispositor Trapped in Dusthana" in b.factor), None)
    assert disp_breaker is not None
    assert disp_breaker.culprit_planet == "Venus"
    assert disp_breaker.penalty == 15.0


def test_raja_uncapped_score_and_major_breaker_gate():
    """1.2: A score with high bonuses but a major breaker (>= 20%) must NEVER be YogaStatus.PURE."""
    # Leo Lagna: Mars (H9) and Venus (H10) conjoin tightly (+10 bonus, +10 natural YK bonus -> 110%).
    # Sun is combusting Venus within 5° (Moderate Combustion, -20% penalty).
    chart = make_test_chart("Leo", {
        "Mars": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Taurus", "longitude": 47.0, "degree_0_to_30": 17.0, "sun_distance": 5.0},
        "Sun": {"sign": "Taurus", "longitude": 42.0, "degree_0_to_30": 12.0}
    }, combustion_status={"Venus": {"sun_separation": 5.0}})
    yogas = detect_raja_yogas(chart)
    dk = next((y for y in yogas if "dharma_karma_raja_yoga" in y.id), None)
    assert dk is not None
    comb_breaker = next((b for b in dk.breakers if "Combustion" in b.factor), None)
    assert comb_breaker is not None
    assert comb_breaker.penalty >= 20.0
    # Net score should be at most 80.0 (100 capped - 20)
    assert dk.plausibility_score <= 80.0
    assert dk.status == YogaStatus.STAINED, "Major breaker (>= 20%) must block YogaStatus.PURE"


def test_raja_symmetric_evaluated_pairs_taurus():
    """1.3: Symmetrical aggregation includes all Kendra/Trikona houses ruled by both planets in Taurus Lagna."""
    # Taurus Lagna: Venus (H1) and Saturn (H9, H10) conjoined in Aquarius H10.
    chart = make_test_chart("Taurus", {
        "Venus": {"sign": "Aquarius", "longitude": 315.0, "degree_0_to_30": 15.0},
        "Saturn": {"sign": "Aquarius", "longitude": 317.0, "degree_0_to_30": 17.0}
    })
    yogas = detect_raja_yogas(chart)
    sh = next((y for y in yogas if "shankha_yoga" in y.id), None)
    assert sh is not None, "Saturn and Venus must form Śaṅkha Yoga"
    # Verify that BOTH H9 and H10 are captured in Saturn's kk houses in positive factors
    assert any("H[9, 10]" in f or ("9" in f and "10" in f) for f in sh.positive_factors), "Saturn's H10 lordship must not be dropped"

    # Also test Sagittarius Lagna: 9th lord Sun and 10th lord Mercury conjoined in Sagittarius H1
    chart_sag = make_test_chart("Sagittarius", {
        "Sun": {"sign": "Sagittarius", "longitude": 255.0, "degree_0_to_30": 15.0},
        "Mercury": {"sign": "Sagittarius", "longitude": 257.0, "degree_0_to_30": 17.0}
    })
    yogas_sag = detect_raja_yogas(chart_sag)
    dk_sag = next((y for y in yogas_sag if "dharma_karma_raja_yoga" in y.id), None)
    assert dk_sag is not None, "Sun (H9) and Mercury (H10) must form Dharma-Karma Raja Yoga symmetrically"


def test_raja_exchange_precedence_over_marginal_aspect():
    """1.4: Mutual sign exchange (Parivartana) with marginal aspect is credited as exchange without marginal penalty."""
    # Aries Lagna: Mars (H1) in Cancer (Moon's sign, H4) and Moon (H4) in Aries (Mars' sign, H1).
    # Both are Kendra houses. Suppose they also have a 35 Virupa marginal aspect.
    chart = make_test_chart("Aries", {
        "Mars": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
    }, aspects={
        "Mars": {"Moon": {"raw": 35.0, "net": 35.0}},
        "Moon": {"Mars": {"raw": 35.0, "net": 35.0}}
    })
    yogas = detect_raja_yogas(chart)
    sh = next((y for y in yogas if "shankha_yoga" in y.id), None)
    assert sh is not None
    assert any("Mutual Reception" in f for f in sh.positive_factors), "Must credit Parivartana positive factor"
    assert not any(b.factor == "Marginal Aspect Connection" for b in sh.breakers), "Exchange must not be penalized by Marginal Aspect Connection"


def test_raja_intervening_planet_null_safety():
    """1.5: Missing coordinates or None values in planet dictionary must not cause TypeError crash."""
    chart = make_test_chart("Aries", {
        "Jupiter": {"sign": "Aries", "longitude": None, "degree_0_to_30": 10.0},
        "Saturn": {"sign": "Aries", "longitude": 20.0, "degree_0_to_30": None},
        "Mercury": {"sign": "Aries", "longitude": None, "degree_0_to_30": None},
        "Mars": "malformed_entry"
    })
    # Must not raise TypeError
    breakers = audit_intervening_planet("Jupiter", "Saturn", chart)
    assert isinstance(breakers, list)


def test_raja_intervening_lagna_lord_exempted():
    """1.5b: Lagna lord or fellow Trikona lord sitting between two Raja Yoga planets must not obstruct."""
    # Aries Lagna: 5L Sun (5°), 1L Mars (10°), 9L Jupiter (15°) all in Aries H1.
    chart = make_test_chart("Aries", {
        "Sun": {"sign": "Aries", "longitude": 5.0, "degree_0_to_30": 5.0},
        "Mars": {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0},
        "Jupiter": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_raja_yogas(chart)
    for y in yogas:
        assert not any(b.factor == "Intervening Planet Obstruction" for b in y.breakers), (
            f"Lagna/Trikona lord must not trigger Intervening Planet Obstruction in {y.id}"
        )


def test_raja_single_planet_dusthana_no_double_penalty():
    """1.6: Debilitated Yogakaraka with cancellation in Dusthana does not get double-penalized."""
    # Leo Lagna: Mars (H4, H9 YK) debilitated in Cancer (H12). Moon in Taurus H10 rescues it.
    chart = make_test_chart("Leo", {
        "Mars": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_raja_yogas(chart)
    yk = next((y for y in yogas if "single_yogakaraka_mars" in y.id), None)
    assert yk is not None
    assert yk.status == YogaStatus.BROKEN
    assert yk.plausibility_score <= 25.0
    # Should only have Incomplete Foundation breaker, NOT a second "Dusthana Placement (Bhanga)" breaker
    dust_breakers = [b for b in yk.breakers if "Dusthana Placement (Bhanga)" in b.factor]
    assert len(dust_breakers) == 0, "Dusthana must not be penalized twice"
    incomplete_breakers = [b for b in yk.breakers if "Incomplete Foundation" in b.factor]
    assert len(incomplete_breakers) == 1


# =============================================================================
# PART 2: PARIVARTANA YOGAS TESTS
# =============================================================================

def test_parivartana_missing_lagna_does_not_emit_maha():
    """2.1: Missing/empty Lagna must not produce a phantom Mahā Parivartana with houses [0, 0]."""
    chart = make_test_chart("", {
        "Sun": {"sign": "Aries", "longitude": 15.0},
        "Mars": {"sign": "Leo", "longitude": 135.0}
    })
    yogas = detect_parivartana_yogas(chart)
    assert len(yogas) == 0, "No Parivartana should be detected without a valid Lagna"


def test_parivartana_layer2_combustion_and_trishadaya():
    """2.2: Mahā Parivartana must audit Layer 2 combustion and Trishadaya intrusion."""
    # Aries Lagna: Sun in Aries (H1) and Mars in Leo (H5) exchange.
    # Sun is combust with Mercury nearby (Mars is combust < 3° from Sun).
    # Saturn (11th lord saboteur) conjoins Sun in Aries H1.
    chart = make_test_chart("Aries", {
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0, "sun_distance": 2.0},
        "Saturn": {"sign": "Aries", "longitude": 18.0, "degree_0_to_30": 18.0}  # 11L saboteur in H1
    }, combustion_status={"Mars": {"sun_separation": 2.0}})
    yogas = detect_parivartana_yogas(chart)
    maha = next((y for y in yogas if "maha_parivartana" in y.id), None)
    assert maha is not None
    assert any("Combustion" in b.factor for b in maha.breakers), "Combustion breaker must be audited"
    assert any("11th Lord" in b.factor for b in maha.breakers), "11th lord Trishadaya saboteur must be audited"
    assert maha.status != YogaStatus.PURE, "Breakers must block YogaStatus.PURE"


def test_parivartana_dusthana_to_dusthana_viparita_crossover():
    """2.3: 6 ⇄ 8 exchange is a Viparīta Crossover (YogaStatus.RESCUED, base 68, score <= 74)."""
    # Aries Lagna: Mercury (6L) in Scorpio (H8) and Mars (8L) in Virgo (H6).
    chart = make_test_chart("Aries", {
        "Mercury": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},  # H8
        "Mars": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0}        # H6
    })
    yogas = detect_parivartana_yogas(chart)
    dainya = next((y for y in yogas if "dainya_parivartana" in y.id), None)
    assert dainya is not None
    assert dainya.status == YogaStatus.RESCUED, "Duṣṭhāna-to-Duṣṭhāna exchange must be YogaStatus.RESCUED"
    assert dainya.plausibility_score <= 74.0
    assert any("Viparīta Crossover" in f for f in dainya.positive_factors)


def test_parivartana_khala_third_house():
    """2.3: 3rd house exchange produces Khala Parivartana with status STAINED."""
    # Aries Lagna: Mercury (3L) in Capricorn (H10) and Saturn (10L) in Gemini (H3).
    chart = make_test_chart("Aries", {
        "Mercury": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},
        "Saturn": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_parivartana_yogas(chart)
    khala = next((y for y in yogas if "khala_parivartana" in y.id), None)
    assert khala is not None
    assert khala.status == YogaStatus.STAINED
    assert any("Khala" in b.factor for b in khala.breakers)


# =============================================================================
# PART 3: VIPARITA RAJA YOGAS TESTS
# =============================================================================

def test_viparita_missing_lagna_index_error_safe():
    """3.1: Missing Lagna sign must not crash with IndexError."""
    chart = make_test_chart("", {
        "Mercury": {"sign": "Virgo", "longitude": 165.0}
    })
    yogas = detect_viparita_raja_yogas(chart)
    assert len(yogas) == 0


def test_viparita_scripture_reference_accuracy():
    """3.2: Scripture references must be Harsha 6.63, Sarala 6.65, Vimala 6.69."""
    # Aries Lagna: Mercury in Virgo (H6), Mars in Scorpio (H8), Jupiter in Pisces (H12).
    chart = make_test_chart("Aries", {
        "Mercury": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_viparita_raja_yogas(chart)
    harsha = next((y for y in yogas if y.id == "harsha_yoga"), None)
    sarala = next((y for y in yogas if y.id == "sarala_yoga"), None)
    vimala = next((y for y in yogas if y.id == "vimala_yoga"), None)

    assert "6.63" in harsha.scripture_ref
    assert "6.65" in sarala.scripture_ref
    assert "6.69" in vimala.scripture_ref


def test_viparita_strongest_contamination_wins():
    """3.3: Conjunction (-25%) takes precedence over marginal aspect (-12.5%)."""
    # Aries Lagna: 6th lord Mercury in H8 (Scorpio).
    # 9th lord Jupiter conjoins Mercury in H8 (-25% penalty).
    # 4th lord Moon casts a marginal 35 Virupa aspect on Mercury (-12.5% penalty).
    chart = make_test_chart("Aries", {
        "Mercury": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Scorpio", "longitude": 227.0, "degree_0_to_30": 17.0},  # Conjunction
        "Moon": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0}
    }, aspects={
        "Moon": {"Mercury": {"raw": 35.0, "net": 35.0}}
    })
    yogas = detect_viparita_raja_yogas(chart)
    harsha = next((y for y in yogas if y.id == "harsha_yoga"), None)
    assert harsha is not None
    contam = next((b for b in harsha.breakers if "Auspicious Lord Contaminated" in b.factor), None)
    assert contam is not None
    assert contam.penalty == 25.0, "Full conjunction contamination must be selected over marginal aspect"


def test_viparita_lagna_co_rulership_vulnerability():
    """3.4: 1st + 8th lord Mars in foreign Duṣṭhāna H6 triggers Lagna Co-Rulership Vulnerability."""
    # Aries Lagna: Mars rules H1 and H8, placed in Virgo (H6).
    chart = make_test_chart("Aries", {
        "Mars": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_viparita_raja_yogas(chart)
    sarala = next((y for y in yogas if y.id == "sarala_yoga"), None)
    assert sarala is not None
    lagna_vuln = next((b for b in sarala.breakers if b.factor == "Lagna Co-Rulership Vulnerability"), None)
    assert lagna_vuln is not None
    assert lagna_vuln.penalty == 20.0


def test_viparita_trikona_co_rulership_leakage():
    """3.4: 5th + 12th lord Mars in foreign Duṣṭhāna H8 triggers Trikoṇa Co-Rulership Leakage."""
    # Sagittarius Lagna: Mars rules H5 and H12, placed in Cancer (H8).
    # Moon in Taurus H6 to give Mars Neecha Bhanga so it's not unredeemed debility
    chart = make_test_chart("Sagittarius", {
        "Mars": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_viparita_raja_yogas(chart)
    vimala = next((y for y in yogas if y.id == "vimala_yoga"), None)
    assert vimala is not None
    trik_vuln = next((b for b in vimala.breakers if b.factor == "Trikoṇa Co-Rulership Leakage"), None)
    assert trik_vuln is not None
    assert trik_vuln.penalty == 20.0


def test_viparita_layer2_combustion_and_dispositor():
    """3.5: Duṣṭhāna lord combust or with debilitated dispositor triggers Layer 2 breakers."""
    # Aries Lagna: 6th lord Mercury in Virgo (H6), but combust within 2° of Sun.
    chart = make_test_chart("Aries", {
        "Mercury": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0, "sun_distance": 2.0},
        "Sun": {"sign": "Virgo", "longitude": 167.0, "degree_0_to_30": 17.0}
    }, combustion_status={"Mercury": {"sun_separation": 2.0}})
    yogas = detect_viparita_raja_yogas(chart)
    harsha = next((y for y in yogas if y.id == "harsha_yoga"), None)
    assert harsha is not None
    assert any("Combustion" in b.factor for b in harsha.breakers)
    assert harsha.status != YogaStatus.PURE
