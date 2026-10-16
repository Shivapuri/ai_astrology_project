"""
tests/test_batch6_yogas.py
Comprehensive Edge-Case & Regression Test Suite for Batch 6:
- power_yogas.py (Null-safe lookups, Digbala sovereignty paradox, Full Moon 7.18 un-nesting, Venus self-conjunction block, Layer 2 breakers)
- bhava_yogas.py (Null-safe house rulers, no duplicate participating houses, Asura & Musala converse status, Bhanga mitigation in Dusthanas)
- evaluator.py (Null-safe empty chart handling, cross-module deduplication for Lakshmi, Viparita, and Dharma-Karma exchange, deterministic sorting)
"""

import pytest
from typing import Dict, Any
from jyotish.yogas.models import YogaStatus, YogaCategory, YogaInstance
from jyotish.yogas.power_yogas import (
    detect_chapter7_power_yogas,
    _safe_degree_in_sign,
    _get_planet_longitude,
    _get_nakshatra_of_planet,
    _get_navamsha_sign,
    _is_planet_retrograde,
)
from jyotish.yogas.bhava_yogas import detect_bhava_yogas
from jyotish.yogas.evaluator import detect_all_yogas


def make_clean_chart(
    lagna_sign: str = "Aries",
    grahas: Dict[str, Any] = None,
    is_day_birth: bool = True,
    aspects: Dict[str, Any] = None,
    shadbala: Dict[str, Any] = None,
    combustion_status: Dict[str, Any] = None,
    vargas: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Helper to assemble structured chart fixtures for Batch 6 tests."""
    from jyotish.yogas.breakers import ZODIAC_SIGNS

    default_shadbala = {
        p: {"total": 450.0, "ratio": 1.1, "Rupas": 7.0, "Ratio_to_Req": 1.1}
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    }
    if shadbala:
        default_shadbala.update(shadbala)

    grahas_dict = {}
    if grahas:
        for p, data in grahas.items():
            if isinstance(data, str):
                s_idx = ZODIAC_SIGNS.index(data) if data in ZODIAC_SIGNS else 0
                grahas_dict[p] = {
                    "sign": data,
                    "longitude": s_idx * 30.0 + 15.0,
                    "degree_0_to_30": 15.0,
                }
            elif isinstance(data, dict):
                p_copy = dict(data)
                if "sign" in p_copy and "longitude" not in p_copy and "degree_0_to_30" in p_copy:
                    s_idx = ZODIAC_SIGNS.index(p_copy["sign"]) if p_copy["sign"] in ZODIAC_SIGNS else 0
                    p_copy["longitude"] = s_idx * 30.0 + float(p_copy["degree_0_to_30"])
                grahas_dict[p] = p_copy
            else:
                grahas_dict[p] = {"sign": str(data)}

    l_idx = ZODIAC_SIGNS.index(lagna_sign) if lagna_sign in ZODIAC_SIGNS else 0
    chart_vargas = {
        "D1": {
            "lagna": {"sign": lagna_sign, "longitude": l_idx * 30.0 + 15.0, "degree_0_to_30": 15.0} if lagna_sign else None,
            "grahas": grahas_dict,
        }
    }
    if vargas:
        chart_vargas.update(vargas)

    chart = {
        "lagna": {"sign": lagna_sign, "longitude": l_idx * 30.0 + 15.0, "degree_0_to_30": 15.0} if lagna_sign else {},
        "vargas": chart_vargas,
        "planets": grahas_dict,
        "planetary_evaluation": {
            "planets": {
                p: {
                    "sign": p_data.get("sign", ""),
                    "house": 0,
                    "is_retrograde": p_data.get("is_retrograde", False),
                    "shadbala": default_shadbala.get(p, {}),
                }
                for p, p_data in grahas_dict.items()
            }
        },
        "advanced_aspects": {"planets": aspects or {}, "cusps": {}},
        "combustion_status": combustion_status or {},
        "is_day_birth": is_day_birth,
    }
    return chart


# =============================================================================
# PART 1: POWER YOGAS AUDIT TESTS
# =============================================================================

def test_power_yogas_null_safe_helpers_and_empty_charts():
    """1.1: Verify helpers and detect_chapter7_power_yogas gracefully handle None, missing fields, and empty charts."""
    # 1. _safe_degree_in_sign
    assert _safe_degree_in_sign(None) == 15.0
    assert _safe_degree_in_sign({}) == 15.0
    assert _safe_degree_in_sign({"degree_0_to_30": None, "longitude": None}) == 15.0
    assert _safe_degree_in_sign({"degree_0_to_30": 12.5}) == 12.5
    assert _safe_degree_in_sign({"degree_0_to_30": "invalid", "longitude": 45.0}) == 15.0

    # 2. _get_planet_longitude
    assert _get_planet_longitude({}, "Sun") is None
    chart_no_lon = {
        "planets": {
            "Sun": {"sign": "Taurus", "degree_0_to_30": 10.0}
        }
    }
    assert _get_planet_longitude(chart_no_lon, "Sun") == 40.0

    # 3. _get_nakshatra_of_planet
    assert _get_nakshatra_of_planet({}, "Moon") == ""
    chart_none_vargas = {"nakshatras": None, "planetary_evaluation": None, "planets": None}
    assert _get_nakshatra_of_planet(chart_none_vargas, "Moon") == ""

    # 4. _get_navamsha_sign
    assert _get_navamsha_sign({}, "Lagna") == ""
    assert _get_navamsha_sign({"vargas": None, "lagna": None}, "Mars") == ""

    # 5. _is_planet_retrograde
    assert _is_planet_retrograde({}, "Saturn") is False
    assert _is_planet_retrograde({"planets": {"Saturn": {"speed": -0.05}}}, "Saturn") is True

    # 6. detect_chapter7_power_yogas with empty or malformed charts
    assert detect_chapter7_power_yogas({}) == []
    assert detect_chapter7_power_yogas({"lagna": None}) == []
    assert detect_chapter7_power_yogas({"lagna": {"sign": "Aries"}, "planets": {}}) == []


def test_power_yogas_digbala_sovereignty_paradox_fix():
    """1.2: Verify 4th Digbala planet (Saturn) does not degrade a 3-planet PURE yoga, and handles dignity correctly."""
    # Chart A: 3 non-Saturn planets in Digbala (Jupiter H1, Mars H10, Moon H4) with Saturn in H2 (not in Digbala)
    chart_3_dig = make_clean_chart("Aries", {
        "Jupiter": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},      # H1 Digbala
        "Mars": {"sign": "Capricorn", "longitude": 272.0, "degree_0_to_30": 2.0},     # H10 Digbala
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},       # H4 Digbala
        "Saturn": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},      # H2 (not Digbala)
    })
    yogas_a = detect_chapter7_power_yogas(chart_3_dig)
    dig_a = next((y for y in yogas_a if "digbala_sovereignty" in y.id), None)
    assert dig_a is not None
    assert dig_a.status == YogaStatus.PURE
    assert dig_a.plausibility_score == 88.0

    # Chart B: Same 3 planets + Dignified Saturn in H7 (Libra, Exalted) -> Digbala count is 4 (including Saturn)
    chart_4_sat_exalted = make_clean_chart("Aries", {
        "Jupiter": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},      # H1 Digbala
        "Mars": {"sign": "Capricorn", "longitude": 272.0, "degree_0_to_30": 2.0},     # H10 Digbala
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},       # H4 Digbala
        "Saturn": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0},      # H7 Digbala (Exalted)
    })
    yogas_b = detect_chapter7_power_yogas(chart_4_sat_exalted)
    dig_b = next((y for y in yogas_b if "digbala_sovereignty" in y.id), None)
    assert dig_b is not None
    assert dig_b.status == YogaStatus.PURE
    assert dig_b.plausibility_score == 88.0, "Dignified Saturn in H7 must not degrade 3-planet PURE yoga to STAINED"

    # Chart C: 3 planets + Undignified Saturn in H7 (Gemini Lagna -> H7 is Sagittarius)
    # Jupiter in H1 (Gemini), Moon in H4 (Virgo), Mars in H10 (Pisces), Saturn in H7 (Sagittarius - Peregrine)
    chart_4_sat_undignified = make_clean_chart("Gemini", {
        "Jupiter": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0},       # H1 Digbala
        "Moon": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},          # H4 Digbala
        "Mars": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0},         # H10 Digbala
        "Saturn": {"sign": "Sagittarius", "longitude": 255.0, "degree_0_to_30": 15.0},  # H7 Digbala (Undignified)
    })
    yogas_c = detect_chapter7_power_yogas(chart_4_sat_undignified)
    dig_c = next((y for y in yogas_c if "digbala_sovereignty" in y.id), None)
    assert dig_c is not None
    # Because active group prefers non_saturn (3 planets) when >= 2, undignified Saturn is excluded and doesn't stain the 3 pure planets!
    assert "Saturn" not in dig_c.participating_planets
    assert dig_c.status == YogaStatus.PURE
    assert dig_c.plausibility_score == 88.0


def test_power_yogas_full_moon_longitude_fallback_and_718_unnesting():
    """1.3: Verify Full Moon configs reconstruct longitude when missing, and Config 4 (7.18) triggers independently."""
    # Config 4 (Phaladeepika 7.18): Jupiter + Moon in Kendra aspected by Venus with no debility
    # Moon in Cancer (H4), Jupiter in Cancer (H4), Venus in Capricorn (H10) aspecting H4 directly
    # In aspects dictionary, key is the receiver (Moon, Jupiter) and sub-key is the giver (Venus)
    chart_718 = make_clean_chart("Aries", {
        "Moon": {"sign": "Cancer", "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Cancer", "degree_0_to_30": 16.0},
        "Venus": {"sign": "Capricorn", "degree_0_to_30": 15.0},
    }, aspects={
        "Moon": {"Venus": {"raw": 60.0, "net": 60.0}},
        "Jupiter": {"Venus": {"raw": 60.0, "net": 60.0}}
    })
    yogas = detect_chapter7_power_yogas(chart_718)
    gk_crown = next((y for y in yogas if y.id == "power_yoga_gaja_kesari_venus_aspect"), None)
    assert gk_crown is not None, "Phaladeepika 7.18 Gajakesari Imperial Crown must trigger even when Sun is omitted"
    assert gk_crown.status == YogaStatus.PURE


def test_power_yogas_block_venus_self_conjunction_taurus_libra():
    """1.4: Verify that Taurus and Libra Lagnas (where 1st Lord is Venus) do not emit power_yoga_l1_venus_h2."""
    # Taurus Lagna: 1st lord is Venus. Sits in Gemini H2.
    chart_taurus = make_clean_chart("Taurus", {
        "Venus": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0}  # H2
    })
    yogas_t = detect_chapter7_power_yogas(chart_taurus)
    assert not any(y.id == "power_yoga_l1_venus_h2" for y in yogas_t), "Must not emit self-conjunction on Taurus Lagna"

    # Libra Lagna: 1st lord is Venus. Sits in Scorpio H2.
    chart_libra = make_clean_chart("Libra", {
        "Venus": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0}  # H2
    })
    yogas_l = detect_chapter7_power_yogas(chart_libra)
    assert not any(y.id == "power_yoga_l1_venus_h2" for y in yogas_l), "Must not emit self-conjunction on Libra Lagna"

    # Aries Lagna: 1st lord is Mars. Mars + Venus in Taurus H2. Must trigger!
    chart_aries = make_clean_chart("Aries", {
        "Mars": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Taurus", "longitude": 50.0, "degree_0_to_30": 20.0}
    })
    yogas_a = detect_chapter7_power_yogas(chart_aries)
    assert any(y.id == "power_yoga_l1_venus_h2" for y in yogas_a), "Must trigger for genuine 1st Lord + Venus union"


def test_power_yogas_layer_2_breakers_applied():
    """1.5: Verify Layer 2 combustion and Shadbala breakers are applied across Power Yogas."""
    # Mars & Mercury in H2 (Phaladeepika 7.21): deeply combust by Sun in H2 (< 3.0°)
    chart_combust = make_clean_chart("Aries", {
        "Sun": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Taurus", "longitude": 46.0, "degree_0_to_30": 16.0},      # Combust (1.0° from Sun)
        "Mercury": {"sign": "Taurus", "longitude": 47.0, "degree_0_to_30": 17.0},   # Combust (2.0° from Sun)
    })
    yogas = detect_chapter7_power_yogas(chart_combust)
    mars_merc = next((y for y in yogas if y.id == "power_yoga_mars_mercury_h2"), None)
    assert mars_merc is not None
    assert mars_merc.status != YogaStatus.PURE, "Deeply combust Mars + Mercury in H2 must NOT be PURE"
    assert any("Combustion" in b.factor for b in mars_merc.breakers)

    # Sun + Venus in H4 (Phaladeepika 7.22): 5.0° apart -> uses deep_only=True, so moderate combustion is not penalized
    chart_sun_ven_h4 = make_clean_chart("Aries", {
        "Sun": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},      # H4
        "Venus": {"sign": "Cancer", "longitude": 110.0, "degree_0_to_30": 20.0},    # H4 (5.0° separation)
    })
    yogas_sv = detect_chapter7_power_yogas(chart_sun_ven_h4)
    sun_ven = next((y for y in yogas_sv if y.id == "power_yoga_sun_venus_h4"), None)
    assert sun_ven is not None
    assert sun_ven.status == YogaStatus.PURE, "Sun + Venus in H4 with 5° separation must be PURE with deep_only=True"


# =============================================================================
# PART 2: BHAVA YOGAS AUDIT TESTS
# =============================================================================

def test_bhava_yogas_null_safe_and_no_duplicate_houses():
    """2.1: Verify null-safe ruler lookups and participating_houses deduplication."""
    # Empty chart
    assert detect_bhava_yogas({}) == []

    # 1st lord Mars in H1 (Aries): participating_houses must be [1], not [1, 1]
    chart_h1 = make_clean_chart("Aries", {
        "Mars": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_bhava_yogas(chart_h1)
    camara = next((y for y in yogas if y.id == "camara_yoga"), None)
    assert camara is not None
    assert camara.participating_houses == [1], f"Expected [1], got {camara.participating_houses}"


def test_bhava_yogas_asura_and_musala_converse_status_invariant():
    """2.2: Verify Asura (H8) and Musala (H12) in Kendra/Trikona are never PURE (STAINED or RESCUED only)."""
    # Aries Lagna: 8th lord is Mars. Mars in Capricorn (H10 Kendra, Exalted) -> Asura Yoga
    # Since Mars is exalted (and co-rules H1 Lagna), it is mitigated -> RESCUED, not PURE!
    chart_asura_mitigated = make_clean_chart("Aries", {
        "Mars": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0}  # Exalted in H10
    })
    yogas_a = detect_bhava_yogas(chart_asura_mitigated)
    asura_m = next((y for y in yogas_a if y.id == "asura_yoga"), None)
    assert asura_m is not None
    assert asura_m.status == YogaStatus.RESCUED, "Mitigated Asura Yoga must be RESCUED, never PURE"

    # Taurus Lagna: 8th lord is Jupiter (rules H8 Sagittarius + H11 Pisces, no trikona co-rulership).
    # Jupiter in Leo (H4 Kendra, peregrine) -> Unmitigated 8th lord in Kendra -> STAINED!
    chart_asura_stained = make_clean_chart("Taurus", {
        "Jupiter": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0}  # H4 Kendra
    })
    yogas_b = detect_bhava_yogas(chart_asura_stained)
    asura_s = next((y for y in yogas_b if y.id == "asura_yoga"), None)
    assert asura_s is not None
    assert asura_s.status == YogaStatus.STAINED, "Unmitigated Asura Yoga must be STAINED, never PURE"

    # Aries Lagna: 12th lord is Jupiter (rules H9+H12). Sits in Sagittarius H9 (Trikona co-ruler in own sign) -> Musala Yoga
    # Mitigated by Trikona co-rulership and own sign -> RESCUED, never PURE!
    chart_musala_mitigated = make_clean_chart("Aries", {
        "Jupiter": {"sign": "Sagittarius", "longitude": 255.0, "degree_0_to_30": 15.0}
    })
    yogas_c = detect_bhava_yogas(chart_musala_mitigated)
    musala_m = next((y for y in yogas_c if y.id == "musala_yoga"), None)
    assert musala_m is not None
    assert musala_m.status == YogaStatus.RESCUED, "Mitigated Musala Yoga must be RESCUED, never PURE"

    # Leo Lagna: 12th lord is Moon. Sits in Scorpio H4 Kendra (debilitated/peregrine) -> Unmitigated Musala Yoga -> STAINED!
    chart_musala_stained = make_clean_chart("Leo", {
        "Moon": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0}
    })
    yogas_d = detect_bhava_yogas(chart_musala_stained)
    musala_s = next((y for y in yogas_d if y.id == "musala_yoga"), None)
    assert musala_s is not None
    assert musala_s.status == YogaStatus.STAINED, "Unmitigated Musala Yoga must be STAINED, never PURE"


def test_bhava_yogas_converse_dusthana_bhanga_mitigation():
    """2.3: Verify Converse Bhāva Yogas transition to RESCUED when lord in 6/8/12 is in own sign or aspected by benefic."""
    # Aries Lagna: 1st lord Mars in Scorpio H8 (own sign!).
    # Ava Yoga (1st lord in Dusthana) is mitigated by own sign -> RESCUED (55.0)
    chart_ava_own = make_clean_chart("Aries", {
        "Mars": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0}
    })
    yogas_own = detect_bhava_yogas(chart_ava_own)
    ava_own = next((y for y in yogas_own if y.id == "ava_yoga"), None)
    assert ava_own is not None
    assert ava_own.status == YogaStatus.RESCUED
    assert ava_own.plausibility_score == 55.0

    # Aries Lagna: 1st lord Mars in Virgo H6 (peregrine, no benefic aspect).
    # Unmitigated -> STAINED (65.0)
    chart_ava_unmitigated = make_clean_chart("Aries", {
        "Mars": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0}
    })
    yogas_unmit = detect_bhava_yogas(chart_ava_unmitigated)
    ava_unmit = next((y for y in yogas_unmit if y.id == "ava_yoga"), None)
    assert ava_unmit is not None
    assert ava_unmit.status == YogaStatus.STAINED
    assert ava_unmit.plausibility_score == 65.0

    # Aries Lagna: 1st lord Mars in Virgo H6, but aspected by Jupiter with 50.0 Virupas -> Mitigated by benefic aspect!
    # In aspects dictionary, outer key is receiver (Mars), inner key is giver (Jupiter)
    chart_ava_aspect = make_clean_chart("Aries", {
        "Mars": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0}
    }, aspects={
        "Mars": {"Jupiter": {"raw": 50.0, "net": 50.0}}
    })
    yogas_asp = detect_bhava_yogas(chart_ava_aspect)
    ava_asp = next((y for y in yogas_asp if y.id == "ava_yoga"), None)
    assert ava_asp is not None
    assert ava_asp.status == YogaStatus.RESCUED, "Benefic aspect must mitigate Converse Dusthana yoga to RESCUED"


# =============================================================================
# PART 3: MASTER EVALUATOR AUDIT TESTS
# =============================================================================

def test_evaluator_empty_chart_and_invalid_lagna_crash_fix():
    """3.1: Verify detect_all_yogas({}) executes cleanly without IndexError."""
    res_empty = detect_all_yogas({})
    assert res_empty["total_count"] == 0
    assert res_empty["summary"]["pure"] == 0
    assert len(res_empty["categories"]) == 17

    res_none = detect_all_yogas(None)
    assert res_none["total_count"] == 0

    res_invalid = detect_all_yogas({"lagna": {"sign": "InvalidSign"}})
    assert res_invalid["total_count"] == 0


def test_evaluator_canonical_duplicate_grouping_and_deduplication():
    """3.2: Verify canonical duplicate groups prevent double counting for Lakshmi, Viparita, and Dharma-Karma exchange."""
    # 1. Lakshmi Yoga overlap (Dhana vs Deity Tridevi)
    # Test chart with Venus in own sign Taurus in Kendra H1, 9th lord Saturn exalted in Libra H6
    # Both dhana_daridrya.py and deity_yogas.py can detect Lakshmi Yoga.
    chart_lakshmi = make_clean_chart("Taurus", {
        "Venus": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},        # H1 Kendra
        "Saturn": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0},       # H6 Exalted (9th Lord)
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0}
    })
    payload_lakshmi = detect_all_yogas(chart_lakshmi)
    lakshmi_instances = [
        y for y in payload_lakshmi["yogas"]
        if "lakshmi" in y["id"].lower()
    ]
    assert len(lakshmi_instances) <= 1, f"Lakshmi Yoga must be deduplicated to at most 1 instance, found: {lakshmi_instances}"

    # 2. Viparita vs Bhava 6/8/12 Reversals (Harsha, Sarala, Vimala)
    # Aries Lagna: 6th lord Mercury in Virgo H6 -> Harsha
    chart_viparita = make_clean_chart("Aries", {
        "Mercury": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0}  # H6
    })
    payload_vip = detect_all_yogas(chart_viparita)
    harsha_instances = [
        y for y in payload_vip["yogas"]
        if "harsha" in y["id"].lower()
    ]
    assert len(harsha_instances) <= 1, f"Harsha Yoga must appear at most once, found: {harsha_instances}"

    # 3. Deterministic sorting: highest plausibility score first
    scores = [y["plausibility_score"] for y in payload_vip["yogas"]]
    assert scores == sorted(scores, reverse=True), "Yogas must be deterministically sorted by plausibility_score descending"
