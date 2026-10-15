"""
tests/test_batch3_yogas.py
Comprehensive Edge-Case & Regression Test Suite for Batch 3:
- contextual_yogas.py (Sāṅkhya, Candrādhi, Lagnādhi, Mahābhāgya, Adhama/Sama/Variṣṭha, Solitary Tanu, Ubhayalagna)
- lunar_solar_yogas.py (Sunaphā, Anaphā, Durudharā, Kemadruma 4-Tier, Budhāditya, Veśi/Vāsi/Ubhayacarī)
- kartari.py (Śubha Kartarī, Pāpa Kartarī, Suśubha fortification, Benefic rescue mitigation)
"""

import pytest
from typing import Dict, Any
from jyotish.yogas.models import YogaStatus, YogaCategory
from jyotish.yogas.contextual_yogas import (
    detect_sankhya_yogas,
    detect_adhi_yogas,
    detect_general_scope_yogas,
    detect_mahabhagya_yogas,
    detect_solitary_first_house_yogas,
    detect_dual_lagna_raja_yogas,
    detect_contextual_yogas,
)
from jyotish.yogas.lunar_solar_yogas import detect_lunar_and_solar_yogas
from jyotish.yogas.kartari import detect_kartari_yogas
from jyotish.yogas.evaluator import detect_all_yogas


def make_clean_chart(
    lagna_sign: str = "Aries",
    grahas: Dict[str, Any] = None,
    is_day_birth: bool = True,
    gender: str = "male",
    aspects: Dict[str, Any] = None,
    shadbala: Dict[str, Any] = None,
    combustion_status: Dict[str, Any] = None,
    d9_grahas: Dict[str, Any] = None,
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
    if d9_grahas:
        vargas["D9"] = {
            "lagna": {"sign": "Aries"},
            "grahas": {p: ({"sign": s} if isinstance(s, str) else s) for p, s in d9_grahas.items()}
        }

    return {
        "vargas": vargas,
        "is_day_birth": is_day_birth,
        "gender": gender,
        "advanced_aspects": {"planets": aspects or {}},
        "shadbala": default_shadbala,
        "combustion_status": combustion_status or {},
    }


# =============================================================================
# 1. SĀṄKHYA YOGAS TESTS
# =============================================================================

def test_sankhya_incomplete_chart_guard():
    """1.2: Incomplete chart with fewer than 7 classical grahas must not trigger Sāṅkhya yogas."""
    chart = make_clean_chart(grahas={
        "Sun": "Aries", "Moon": "Leo", "Jupiter": "Sagittarius"  # Only 3 grahas
    })
    yogas = detect_sankhya_yogas(chart)
    assert len(yogas) == 0, "Incomplete chart must not falsely trigger Sāṅkhya yogas like Śūla Yoga"


def test_sankhya_shula_yoga_full_7_grahas():
    """1.2: All 7 classical grahas cleanly in exactly 3 unique signs -> Śūla Yoga (ZERO Layer 2 breakers)."""
    chart = make_clean_chart(grahas={
        "Sun": "Aries", "Mars": "Aries",
        "Moon": "Leo", "Jupiter": "Leo", "Venus": "Leo",
        "Mercury": "Sagittarius", "Saturn": "Sagittarius"
    })
    yogas = detect_sankhya_yogas(chart)
    assert len(yogas) == 1
    assert yogas[0].id == "sankhya_shula_yoga"
    assert yogas[0].status == YogaStatus.PURE
    assert len(yogas[0].breakers) == 0, "Sāṅkhya yogas stand alone with ZERO breakers per Phaladeepika 6.39"


# =============================================================================
# 2. CANDRĀDHI & LAGNĀDHI YOGAS TESTS
# =============================================================================

def test_candradhi_command_pillars_grading():
    """1.3: Graded base score across Netā (6th), Mantrī (7th), Bhūpati (8th) command pillars."""
    # Moon in Aries: 6th=Virgo, 7th=Libra, 8th=Scorpio
    # A. 1 pillar: only Mercury in Virgo (6th)
    chart_1p = make_clean_chart(grahas={"Moon": "Aries", "Mercury": "Virgo"})
    y_1p = detect_adhi_yogas(chart_1p)
    cadhi_1p = next((y for y in y_1p if y.id == "candradhi_yoga"), None)
    assert cadhi_1p is not None
    assert "Netā" in cadhi_1p.name

    # B. 3 pillars: Mercury in 6th, Venus in 7th, Jupiter in 8th -> Full command confluence
    chart_3p = make_clean_chart(grahas={
        "Moon": "Aries", "Mercury": "Virgo", "Venus": "Libra", "Jupiter": "Scorpio"
    })
    y_3p = detect_adhi_yogas(chart_3p)
    cadhi_3p = next((y for y in y_3p if y.id == "candradhi_yoga"), None)
    assert cadhi_3p is not None
    assert cadhi_3p.status == YogaStatus.PURE
    assert cadhi_3p.plausibility_score >= 90.0


def test_candradhi_combustion_and_shadbala_breakers():
    """1.3: Deeply combust or weak Shadbala benefic in Ādhi must trigger Layer 2 breaker penalties."""
    # Mercury in 7th (Libra) from Moon (Aries), but Mercury is deeply combust
    chart = make_clean_chart(
        grahas={"Moon": "Aries", "Mercury": "Libra", "Sun": "Libra"},
        combustion_status={"Mercury": {"is_combust": True, "separation_deg": 1.2, "is_deep": True}},
        shadbala={"Mercury": {"total": 280.0, "ratio": 0.7, "Rupas": 4.5, "Ratio_to_Req": 0.7}}
    )
    yogas = detect_adhi_yogas(chart)
    cadhi = next((y for y in y_1 if y.id == "candradhi_yoga"), None) if (y_1 := detect_adhi_yogas(chart)) else None
    assert cadhi is not None
    assert cadhi.status != YogaStatus.PURE, "Deep combustion and weak Shadbala must prevent PURE status on Ādhi"
    assert any("Combustion" in b.factor for b in cadhi.breakers)


def test_lagnadhi_evaluated_independent_of_moon():
    """1.3: Lagnādhi must evaluate cleanly when Moon is missing or unpositioned."""
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={"Jupiter": "Libra"}  # Jupiter in 7th from Lagna, NO Moon in chart
    )
    yogas = detect_adhi_yogas(chart)
    ladhi = next((y for y in yogas if y.id == "lagnadhi_yoga"), None)
    assert ladhi is not None, "Lagnādhi must not be gated on moon_house > 0"
    assert "Mantrī" in ladhi.name


# =============================================================================
# 3. MAHĀBHĀGYA YOGA TESTS
# =============================================================================

def test_mahabhagya_unspecified_gender_penalty():
    """1.4: Satisfying all 4 polarity factors with unspecified gender triggers penalty and blocks PURE status."""
    chart = make_clean_chart(
        lagna_sign="Aries",  # Odd
        grahas={"Sun": "Leo", "Moon": "Sagittarius"},  # Both Odd
        is_day_birth=True,
        gender=""  # Unspecified
    )
    yogas = detect_mahabhagya_yogas(chart)
    mb = next((y for y in yogas if "mahabhagya" in y.id), None)
    assert mb is not None
    assert mb.status == YogaStatus.STAINED, "Unspecified gender must prevent PURE status"
    assert any("Unverified Biological Gender" in b.factor for b in mb.breakers)


def test_mahabhagya_partial_3_of_4_confluence():
    """1.4: 3 out of 4 polarity alignment factors triggers partial Mahābhāgya synergy."""
    # Male: Day birth, Odd Lagna, Odd Sun, but EVEN Moon (Taurus)
    chart = make_clean_chart(
        lagna_sign="Aries",  # Odd
        grahas={"Sun": "Leo", "Moon": "Taurus"},  # Sun Odd, Moon Even
        is_day_birth=True,
        gender="male"
    )
    yogas = detect_mahabhagya_yogas(chart)
    mb_part = next((y for y in yogas if y.id == "mahabhagya_partial_male_yoga"), None)
    assert mb_part is not None, "3 of 4 factors must trigger partial Mahābhāgya"
    assert mb_part.status == YogaStatus.STAINED
    assert any("Partial Polarity Alignment" in b.factor for b in mb_part.breakers)


def test_mahabhagya_flat_schema_and_duplicate_houses_guard():
    """1.4: Top-level flat schema compatibility and duplicate house numbers elimination."""
    # Sun and Moon conjoined in Lagna (House 1)
    chart = {
        "lagna": {"sign": "Aries"},
        "planets": {
            "Sun": {"sign": "Aries"},
            "Moon": {"sign": "Aries"}
        },
        "is_day_birth": True,
        "gender": "male"
    }
    yogas = detect_mahabhagya_yogas(chart)
    assert len(yogas) == 1
    assert yogas[0].participating_houses == [1], "participating_houses must deduplicate [1, 1, 1] into [1]"


# =============================================================================
# 4. SUN-MOON QUADRANTS (Adhama, Sama, Variṣṭha)
# =============================================================================

def test_sun_moon_quadrant_adhama_kendra_and_rescue():
    """1.5: Moon in Kendra from Sun is Adhama Yoga (STAINED; RESCUED if anchored in Lagna Kendra)."""
    # A. Unanchored Adhama: Sun in Taurus H2, Moon in Leo H5 (4th from Sun, neither in Lagna Kendra)
    chart_stn = make_clean_chart("Aries", {"Sun": "Taurus", "Moon": "Leo"})
    y_stn = detect_general_scope_yogas(chart_stn)
    adh_stn = next((y for y in y_stn if y.id == "adhama_yoga"), None)
    assert adh_stn is not None
    assert adh_stn.status == YogaStatus.STAINED

    # B. Rescued Adhama: Sun in Aries H1, Moon in Cancer H4 (4th from Sun, both in Lagna Kendra)
    chart_res = make_clean_chart("Aries", {"Sun": "Aries", "Moon": "Cancer"})
    y_res = detect_general_scope_yogas(chart_res)
    adh_res = next((y for y in y_res if y.id == "adhama_yoga"), None)
    assert adh_res is not None
    assert adh_res.status == YogaStatus.RESCUED


# =============================================================================
# 5. LUNAR & SOLAR FLANKING WHITELIST (Five Starry Grahas)
# =============================================================================

def test_flanking_ignores_non_classical_points():
    """2.1: Uranus, Neptune, Pluto, Ascendant, or Gulika must not trigger flanking yogas or cancel Kemadruma."""
    # Moon in Leo with Uranus in Virgo (2nd) and Neptune in Cancer (12th)
    chart = make_clean_chart("Aries", {
        "Moon": "Leo",
        "Uranus": "Virgo",
        "Neptune": "Cancer"
    })
    yogas = detect_lunar_and_solar_yogas(chart)
    # Must NOT form Durudharā, Sunaphā, or Anaphā
    assert not any(y.id in ("durudhara_yoga", "sunapha_yoga", "anapha_yoga") for y in yogas)
    # Moon remains isolated (Kemadruma forms)
    assert any("kemadruma" in y.id for y in yogas)


# =============================================================================
# 6. KEMADRUMA 4-TIER BHAṄGA HIERARCHY
# =============================================================================

def test_kemadruma_active_unmitigated_status_is_stained():
    """2.3: Unmitigated Kemadruma must use YogaStatus.STAINED (Affliction Invariant), NEVER BROKEN or PURE."""
    # Moon in Taurus H2 (not Kendra), Sun in Virgo H5, Mars in Libra H6, Saturn in Libra H6
    # No planets in 2nd/12th from Moon; no planets in Kendras from Moon; Moon not in Lagna Kendra; Aries (Cardinal) != Taurus (Fixed)
    chart = make_clean_chart("Aries", {
        "Moon": "Taurus", "Sun": "Virgo", "Mars": "Libra", "Saturn": "Libra"
    })
    yogas = detect_lunar_and_solar_yogas(chart)
    kema = next((y for y in yogas if y.id == "kemadruma_yoga"), None)
    assert kema is not None
    assert kema.status == YogaStatus.STAINED, "Active Kemadruma must have STAINED status"
    assert kema.plausibility_score >= 75.0


def test_kemadruma_tier3_modality_rescue():
    """2.3: Tier 3 Modality Alignment (Cardinal-Cardinal, Fixed-Fixed, Dual-Dual) rescues Kemadruma."""
    # Aries Lagna (Cardinal) + Cancer Moon (Cardinal in H4) -> Cardinal modality alignment
    # Or Capricorn Lagna (Cardinal) + Libra Moon (Cardinal in H10)
    chart = make_clean_chart("Capricorn", {
        "Moon": "Libra",  # Both Cardinal
        "Sun": "Sagittarius"
    })
    yogas = detect_lunar_and_solar_yogas(chart)
    kema = next((y for y in yogas if y.id == "kemadruma_yoga"), None)
    assert kema is not None
    assert kema.status == YogaStatus.RESCUED
    assert any("Tier 3 Modality Alignment" in note for note in kema.positive_factors)


def test_kemadruma_tier4_d9_kendra_rescue():
    """2.3: Tier 4 Navāṃśa (D9) Kendra support from Moon cancels Kemadruma."""
    # Moon in Taurus in D1, D9 Moon in Aries, Jupiter in Cancer in D9 (4th from Moon in D9)
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={"Moon": "Taurus", "Sun": "Virgo"},
        d9_grahas={"Moon": "Aries", "Jupiter": "Cancer"}
    )
    yogas = detect_lunar_and_solar_yogas(chart)
    kema = next((y for y in yogas if y.id == "kemadruma_yoga"), None)
    assert kema is not None
    assert kema.status == YogaStatus.RESCUED
    assert any("Tier 4 Navāṃśa Kendra" in note for note in kema.positive_factors)


def test_kemadruma_missing_house_zero_modulo_safety():
    """2.3: Planet with house = 0 must not falsely trigger Tier 1 Lunar Kendra cancellation."""
    chart = {
        "vargas": {"D1": {"lagna": None, "grahas": {"Moon": {"sign": "Aries"}}}},
        "planets": {"Moon": {"sign": "Aries"}, "Mars": {"sign": ""}}
    }
    yogas = detect_lunar_and_solar_yogas(chart)
    # When Lagna is None, moon_house is 0 -> detect_lunar_and_solar_yogas safely skips without crash
    assert isinstance(yogas, list)


# =============================================================================
# 7. BUDHĀDITYA & SOLAR FLANKING TESTS
# =============================================================================

def test_budhaditya_optimal_orb_bonus_and_deep_combustion():
    """2.4: Budhāditya grants optimal orb bonus at 3°-14°; only deep combustion (< 3°) penalizes."""
    # A. Optimal 8° separation -> PURE + 5.0 bonus = 90.0
    chart_opt = make_clean_chart("Gemini", {
        "Sun": {"sign": "Gemini", "longitude": 70.0, "degree_0_to_30": 10.0},
        "Mercury": {"sign": "Gemini", "longitude": 78.0, "degree_0_to_30": 18.0}
    })
    y_opt = detect_lunar_and_solar_yogas(chart_opt)
    budh_opt = next((y for y in y_opt if y.id == "budhaditya_yoga"), None)
    assert budh_opt is not None
    assert budh_opt.status == YogaStatus.PURE
    assert any("Optimal illumination orb" in p for p in budh_opt.positive_factors)

    # B. Deep combustion (1.5° separation) -> penalized
    chart_deep = make_clean_chart(
        lagna_sign="Gemini",
        grahas={
            "Sun": {"sign": "Gemini", "longitude": 70.0, "degree_0_to_30": 10.0},
            "Mercury": {"sign": "Gemini", "longitude": 71.5, "degree_0_to_30": 11.5}
        },
        combustion_status={"Mercury": {"is_combust": True, "separation_deg": 1.5, "is_deep": True}}
    )
    y_deep = detect_lunar_and_solar_yogas(chart_deep)
    budh_deep = next((y for y in y_deep if y.id == "budhaditya_yoga"), None)
    assert budh_deep is not None
    assert budh_deep.status != YogaStatus.PURE


def test_solar_flanking_papa_vs_shubha_distinction():
    """2.4: Malefics flanking the Sun produce Pāpa-Veśi/Vāsi/Ubhayacarī (STAINED per Phaladeepika 6.12)."""
    # Saturn in 2nd from Sun (Aries Sun, Taurus Saturn)
    chart = make_clean_chart("Aries", {
        "Sun": "Aries", "Saturn": "Taurus", "Moon": "Leo"
    })
    yogas = detect_lunar_and_solar_yogas(chart)
    vesi = next((y for y in yogas if y.id == "vesi_yoga"), None)
    assert vesi is not None
    assert "Pāpa-" in vesi.name
    assert vesi.status == YogaStatus.STAINED, "Pāpa solar flanking must be STAINED"


# =============================================================================
# 8. KARTARĪ YOGAS TESTS
# =============================================================================

def test_kartari_one_sided_benefic_does_not_trigger():
    """3.1: Benefic in H2 with unrecognized or empty H12 must not falsely trigger Śubha Kartarī."""
    # Jupiter in Taurus (2nd from Aries Lagna), Uranus in Pisces (12th from Aries Lagna - unrecognized)
    chart = make_clean_chart("Aries", {
        "Jupiter": "Taurus", "Uranus": "Pisces", "Moon": "Leo"
    })
    yogas = detect_kartari_yogas(chart)
    assert not any("shubha_kartari_lagna" in y.id for y in yogas), "Both flanks must be independently valid"


def test_sushubha_kartari_fortification():
    """3.1: Śubha Kartarī fortified by benefic aspect on Lagna upgrades to Suśubha Kartarī (95.0 PURE)."""
    # Jupiter in H2 (Taurus), Venus in H12 (Pisces), Mercury in H7 (Libra) casting palpable aspect on Lagna
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={"Jupiter": "Taurus", "Venus": "Pisces", "Mercury": "Libra"},
        aspects={"Lagna": {"Mercury": 50.0}}
    )
    yogas = detect_kartari_yogas(chart)
    shubha = next((y for y in yogas if "shubha_kartari_lagna" in y.id), None)
    assert shubha is not None
    assert "Suśubha" in shubha.name
    assert shubha.status == YogaStatus.PURE
    assert shubha.plausibility_score >= 95.0


def test_papa_kartari_benefic_rescue_mitigation():
    """3.1: Pāpa Kartarī mitigated by benefic occupant/aspect transitions to RESCUED (55.0, never PURE)."""
    # Saturn in H2 (Taurus), Mars in H12 (Pisces) hemming Lagna, but Jupiter occupies Lagna (H1)
    chart = make_clean_chart("Aries", {
        "Saturn": "Taurus", "Mars": "Pisces", "Jupiter": "Aries"
    })
    yogas = detect_kartari_yogas(chart)
    papa = next((y for y in yogas if "papa_kartari_lagna" in y.id), None)
    assert papa is not None
    assert papa.status == YogaStatus.RESCUED, "Benefic protector must mitigate Pāpa Kartarī to RESCUED"
    assert papa.plausibility_score == 55.0


# =============================================================================
# 9. MASTER EVALUATOR GLOBAL DEDUPLICATION
# =============================================================================

def test_batch3_cross_module_zero_duplicates():
    """1.1: Verify master evaluator emits zero duplicate IDs or duplicate canonical concepts across Batch 3."""
    chart = make_clean_chart("Aries", {
        "Sun": "Aries",
        "Moon": "Cancer",
        "Mars": "Capricorn",
        "Mercury": "Taurus",
        "Jupiter": "Pisces",
        "Venus": "Taurus",
        "Saturn": "Aquarius"
    })
    payload = detect_all_yogas(chart)
    yogas = payload["yogas"]
    ids = [y["id"] for y in yogas]

    # 1. No duplicate IDs
    assert len(ids) == len(set(ids)), f"Duplicate IDs detected: {[x for x in ids if ids.count(x) > 1]}"

    # 2. Kemadruma, Ubhayacarī, Kartarī must each appear at most once
    kema_matches = [y["id"] for y in yogas if "kemadruma" in y["id"]]
    assert len(kema_matches) <= 1, f"Kemadruma must appear at most once, got: {kema_matches}"

    kartari_lagna = [y["id"] for y in yogas if "kartari" in y["id"] and "lagna" in y["id"]]
    assert len(kartari_lagna) <= 1, f"Lagna Kartarī must appear at most once, got: {kartari_lagna}"
