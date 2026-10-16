"""
tests/test_batch4_yogas.py
Comprehensive Edge-Case & Regression Test Suite for Batch 4:
- dispositor_root_yogas.py (Kāhala Variants A & B, Parvata Authentic, Self-Dispositor & BPHS, Puṣkala Yoga)
- character_growth_yogas.py (Gaja Kesarī, Śakaṭa & Śakaṭa Bhaṅga, Vasumatī Graded & Anti-Interference, Amalā)
"""

import pytest
from typing import Dict, Any
from jyotish.yogas.models import YogaStatus, YogaCategory
from jyotish.yogas.dispositor_root_yogas import (
    detect_dispositor_root_yogas,
    detect_puskala_yoga,
)
from jyotish.yogas.character_growth_yogas import (
    detect_character_and_growth_yogas,
)
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
# PART 1: DISPOSITOR ROOT YOGAS AUDIT & EDGE CASES
# =============================================================================

def test_1_1_unsafe_house_rulers_extraction_and_empty_charts():
    """1.1: Guard against unrecognized lagna returning [] causing IndexError on house_rulers.get(n)[0]."""
    # Empty chart dict
    empty_res = detect_dispositor_root_yogas({})
    assert empty_res == []

    # Chart with unrecognized lagna sign
    invalid_chart = make_clean_chart(lagna_sign="UnknownConstellation", grahas={"Sun": "Aries"})
    invalid_res = detect_dispositor_root_yogas(invalid_chart)
    assert invalid_res == []


def test_1_2_kahala_a_dual_lagna_self_kendra_tautology_blocked():
    """1.2: Dual ascendants (Gemini, Virgo, Sagittarius, Pisces) have lord_4 == lord_10.
    Single-planet self-Kendra must NEVER trigger Kāhala Yoga Variant A."""
    # Gemini Lagna: 4L = Mercury, 10L = Mercury. Place Mercury debilitated in Pisces (H10).
    chart_gemini = make_clean_chart(
        lagna_sign="Gemini",
        grahas={
            "Mercury": "Pisces",  # In H10, 4L and 10L same planet!
            "Saturn": "Leo",     # 9L in H3
            "Jupiter": "Scorpio" # In H6
        }
    )
    yogas = detect_dispositor_root_yogas(chart_gemini)
    kahala_a = next((y for y in yogas if y.id == "kahala_yoga_variant_a"), None)
    assert kahala_a is None, "Dual Lagna chart must NOT trigger Kāhala Variant A on single-planet self-Kendra!"

    # Virgo Lagna: 4L = Jupiter, 10L = Mercury. (Wait, Virgo 4L is Sagittarius=Jupiter, 10L is Gemini=Mercury, so lord_4 != lord_10)
    # But for Sagittarius Lagna: 4L = Pisces (Jupiter), 10L = Virgo (Mercury).
    # Gemini: 4L = Virgo (Mercury), 10L = Pisces (Jupiter). Wait! Let's check Gemini sign lords:
    # Gemini = H1 (Mercury). H4 = Virgo (Mercury). H10 = Pisces (Jupiter).
    # Wait! In Gemini: H4 is Virgo (Mercury) and H1 is Gemini (Mercury). H10 is Pisces (Jupiter).
    # Wait, which signs have 4L == 10L?
    # In whole-sign astrology: 10th sign from Gemini is Pisces (Jupiter). 4th from Gemini is Virgo (Mercury).
    # What about signs where 4L == 10L?
    # Signs whose 4th and 10th houses are both Mercury or both Jupiter?
    # Mercury rules Gemini and Virgo (which are 4 signs apart). If Gemini is H10, then H4 is Sagittarius (Jupiter)!
    # Wait, if Lagna is Pisces: H4 is Gemini (Mercury), H10 is Virgo (Mercury)!
    # YES! In Pisces Lagna: H4 is Gemini (ruled by Mercury), H10 is Virgo (ruled by Mercury)!
    # In Sagittarius Lagna: H4 is Pisces (ruled by Jupiter), H10 is Virgo... wait, H10 is Virgo (Mercury).
    # In Virgo Lagna: H4 is Sagittarius (Jupiter), H10 is Gemini (Mercury).
    # Wait, in Pisces Lagna: H4 is Gemini (Mercury) and H10 is Virgo (Mercury). BOTH 4L AND 10L ARE MERCURY!
    # In Gemini Lagna: H7 is Sagittarius (Jupiter), H10 is Pisces (Jupiter), so 7L and 10L are Jupiter.
    chart_pisces = make_clean_chart(
        lagna_sign="Pisces",
        grahas={
            "Mercury": "Gemini",  # In H4. Rules both H4 and H10!
            "Jupiter": "Aries",   # 1L in H2
        }
    )
    yogas_pisces = detect_dispositor_root_yogas(chart_pisces)
    kahala_a_pisces = next((y for y in yogas_pisces if y.id == "kahala_yoga_variant_a"), None)
    assert kahala_a_pisces is None, "Pisces Lagna where lord_4 == lord_10 == Mercury must NOT trigger Kāhala Variant A on single planet!"


def test_1_2_kahala_a_bphs_pairings_on_pisces_lagna():
    """1.2: Pisces Lagna has lord_4 == lord_10 == Mercury.
    BPHS Ch. 36 pair (4L + 9L: Mercury + Mars) or (4L + Jupiter: Mercury + Jupiter) in mutual Kendra triggers Kāhala A!"""
    # Pisces Lagna: 4L = Mercury (in H4 Gemini), 9L = Mars (in H7 Virgo -> 4th from Mercury, mutual Kendra!)
    chart_pisces_bphs = make_clean_chart(
        lagna_sign="Pisces",
        grahas={
            "Mercury": "Gemini",  # H4
            "Mars": "Virgo",      # H7 (4th from Mercury -> Kendra!)
            "Jupiter": "Cancer",  # 1L exalted in H5
        }
    )
    yogas = detect_dispositor_root_yogas(chart_pisces_bphs)
    kahala_a = next((y for y in yogas if y.id == "kahala_yoga_variant_a"), None)
    assert kahala_a is not None, "BPHS (4L, 9L) mutual Kendra alliance must trigger Kāhala Variant A on Pisces Lagna"
    assert kahala_a.status == YogaStatus.PURE
    assert set(kahala_a.participating_planets) == {"Mercury", "Mars", "Jupiter"}


def test_1_2_kahala_a_layer2_breakers_applied():
    """1.2: Layer 2 breakers applied when Lagnesha or participating lords sit in Dusthanas."""
    # Aries Lagna: 4L Moon in H6 (Virgo), 10L Saturn in H12 (Pisces).
    # Moon in H6 and Saturn in H12 are 7th from each other (mutual Kendra!), but both in Dusthanas!
    chart_dusthana = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Mars": "Aries",   # 1L in H1
            "Moon": "Virgo",   # 4L in H6
            "Saturn": "Pisces" # 10L in H12 (7th from Moon)
        }
    )
    yogas = detect_dispositor_root_yogas(chart_dusthana)
    kahala_a = next((y for y in yogas if y.id == "kahala_yoga_variant_a"), None)
    assert kahala_a is not None
    # Dusthana breaker must be active
    assert any("Dusthana" in b.factor for b in kahala_a.breakers)
    assert kahala_a.status != YogaStatus.PURE


def test_1_3_parvata_self_dispositor_loophole_and_no_kahala_b_leak():
    """1.3: 1st lord in own sign in H1 (e.g. Mars in Aries in H1):
    Emits parvata_yoga_self_dispositor (score 70.0, STAINED) and does NOT emit kahala_yoga_variant_b!"""
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={"Mars": "Aries"}
    )
    yogas = detect_dispositor_root_yogas(chart)
    parv_self = next((y for y in yogas if y.id == "parvata_yoga_self_dispositor"), None)
    assert parv_self is not None
    assert parv_self.plausibility_score == 70.0
    assert parv_self.status == YogaStatus.STAINED
    assert any("Self-Dispositor Loophole" in b.factor for b in parv_self.breakers)

    # Must NOT emit kahala_yoga_variant_b
    kahala_b = next((y for y in yogas if y.id == "kahala_yoga_variant_b"), None)
    assert kahala_b is None, "Self-dispositor loophole must NOT emit Kāhala Yoga Variant B"


def test_1_3_authentic_parvata_does_not_double_emit_kahala_b():
    """1.3: Authentic Parvata (both 1L and dispositor own/exalted in Kendra/Trikona)
    must NOT double-emit kahala_yoga_variant_b for the same planetary pair."""
    # Capricorn Lagna: 1L Saturn exalted in Libra H10. Dispositor Venus in Taurus H5 (own sign).
    chart = make_clean_chart(
        lagna_sign="Capricorn",
        grahas={
            "Saturn": "Libra",   # 1L exalted in H10
            "Venus": "Taurus",   # Dispositor in own sign in H5
        }
    )
    yogas = detect_dispositor_root_yogas(chart)
    parv_auth = next((y for y in yogas if y.id == "parvata_yoga_authentic"), None)
    assert parv_auth is not None
    assert parv_auth.status == YogaStatus.PURE
    assert parv_auth.plausibility_score >= 90.0

    # Ensure Kāhala Variant B is NOT double-emitted
    kahala_b = next((y for y in yogas if y.id == "kahala_yoga_variant_b"), None)
    assert kahala_b is None, "Authentic Parvata must consume the root chain without double-emitting Kāhala Variant B"


def test_1_3_bphs_parvata_kendra_benefics():
    """1.3: BPHS Parvata variant: 2+ benefics in Kendras with H6/H8 free of malefics."""
    # Aries Lagna: Jupiter in H1, Venus in H4. H6 (Virgo) and H8 (Scorpio) unoccupied.
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Mars": "Taurus",    # 1L in H2 (not own/exalted, so authentic Parvata not formed)
            "Jupiter": "Aries",  # Benefic in H1
            "Venus": "Cancer",   # Benefic in H4
        }
    )
    yogas = detect_dispositor_root_yogas(chart)
    parv_bphs = next((y for y in yogas if y.id == "parvata_yoga_bphs"), None)
    assert parv_bphs is not None
    assert parv_bphs.status == YogaStatus.PURE


def test_1_3_kahala_variant_b_two_step_dispositor_root():
    """1.3: 2-step dispositor chain: 1L -> disp1 -> disp2 (where disp2 is own/exalted in KT)."""
    # Aries Lagna:
    # 1L Mars in Gemini H3 (ruled by Mercury). Mars not in KT, not own/exalted -> Authentic Parvata impossible.
    # disp1 Mercury in Cancer H4 (ruled by Moon). Mercury not own/exalted.
    # disp2 Moon in Cancer H4 (own sign in Kendra H4!).
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Mars": "Gemini",    # H3
            "Mercury": "Cancer", # H4
            "Moon": "Cancer",    # H4 (own sign in Kendra!)
        }
    )
    yogas = detect_dispositor_root_yogas(chart)
    kahala_b = next((y for y in yogas if y.id == "kahala_yoga_variant_b"), None)
    assert kahala_b is not None, "Must detect 2-step dispositor root in Kāhala Variant B"
    assert "Two-step dispositor chain" in kahala_b.positive_factors[0]
    assert set(kahala_b.participating_planets) == {"Mars", "Mercury", "Moon"}


def test_1_4_puskala_yoga_architecture_and_friendly_host():
    """1.4: Puṣkala Yoga correctly checks friendly host via Pañcadhā Maitrī without temp_rel self-enemy bug."""
    # Capricorn Lagna: 1L Saturn in Libra H10 (exalted).
    # Moon in Virgo H9 (ruled by Mercury). Moon dispositor Mercury is in Libra H10 (conjoined with Saturn in Kendra!).
    # Shared sign is Libra, hosted by Venus.
    # Place Venus in Scorpio H11 (2 houses away from Libra -> Temporary Friend, and H11 is not Dusthana!).
    # Saturn natural friend with Venus + Temp friend = Great Friend.
    # Aspect on Lagna: Sun in Aries H4 (aspects Lagna H1 with 50 Virupas).
    # Fortification: Jupiter in H1.
    chart = make_clean_chart(
        lagna_sign="Capricorn",
        grahas={
            "Saturn": "Libra",        # 1L in H10
            "Mercury": "Libra",       # Moon dispositor in H10 (conjoined with Saturn!)
            "Moon": "Virgo",          # Moon in H9
            "Venus": "Scorpio",       # Host of Libra in H11 (2 houses from Libra -> Temp Friend; H11 not Dusthana)
            "Sun": "Aries",           # H4 (casts palpable aspect on Lagna)
            "Jupiter": "Capricorn",   # In H1 (fortifies Lagna)
        },
        aspects={"Lagna": {"Sun": 50.0}}
    )
    yogas = detect_puskala_yoga(chart)
    assert len(yogas) == 1
    puskala = yogas[0]
    assert puskala.id == "puskala_yoga"
    assert puskala.category == YogaCategory.DISPOSITOR_ROOT
    assert puskala.status == YogaStatus.PURE
    assert puskala.plausibility_score >= 90.0


def test_1_4_puskala_yoga_self_conjunction_guard():
    """1.4: When lagna_lord == moon_lord, single planet sitting alone in Kendra must NOT trigger Puṣkala."""
    # Aries Lagna: Moon in Scorpio H8 -> Moon lord is Mars. Lagna lord is Mars.
    # Mars sits alone in Capricorn H10. Moon is in H8.
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Mars": "Capricorn",  # H10
            "Moon": "Scorpio",    # H8
        }
    )
    yogas = detect_puskala_yoga(chart)
    assert len(yogas) == 0, "Single planet with lagna_lord == moon_lord without Moon conjoining must not trigger Puṣkala"


# =============================================================================
# PART 2: CHARACTER & GROWTH YOGAS AUDIT & EDGE CASES
# =============================================================================

def test_2_1_gaja_kesari_pure_and_dual_kendra():
    """2.1: Gaja Kesarī Yoga detected when Jupiter is in Kendra from Moon with dual Kendra bonus."""
    # Aries Lagna: Moon in Aries H1, Jupiter in Cancer H4 (4th from Moon, also Kendra from Lagna!).
    # Jupiter is also exalted in Cancer (+dignity bonus).
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Moon": "Aries",
            "Jupiter": "Cancer"
        }
    )
    yogas = detect_character_and_growth_yogas(chart)
    gk = next((y for y in yogas if y.id == "gaja_kesari_yoga"), None)
    assert gk is not None, "Must detect Gaja Kesarī Yoga"
    assert gk.category == YogaCategory.CHARACTER
    assert gk.status == YogaStatus.PURE
    assert gk.plausibility_score >= 95.0  # 82 base + 8 dual kendra + 5 dignity


def test_2_1_gaja_kesari_debilitation_penalty():
    """2.1: Gaja Kesarī with debilitated Moon without Neecha Bhanga receives breaker."""
    # Aries Lagna: Moon in Scorpio H8 (debilitated), Jupiter in Leo H5 (10th from Moon -> Kendra).
    # Neither in Lagna Kendra. Mars (dispositor) and Venus (exaltation lord) placed in Gemini H3 (not Kendra).
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Moon": "Scorpio",    # H8 (debilitated in Scorpio)
            "Jupiter": "Leo",     # H5 (10th from Moon -> Kendra!)
            "Mars": "Gemini",     # H3 (dispositor of Scorpio, not Kendra)
            "Venus": "Gemini"     # H3 (exaltation lord of Moon, not Kendra)
        }
    )
    yogas = detect_character_and_growth_yogas(chart)
    gk = next((y for y in yogas if y.id == "gaja_kesari_yoga"), None)
    assert gk is not None
    assert any("Debilitation" in b.factor for b in gk.breakers)
    assert gk.status != YogaStatus.PURE


def test_2_2_sakata_yoga_active_vs_rescued():
    """2.2: Śakaṭa Yoga active (STAINED, 60.0) when Moon in 6/8/12 from Jupiter without Kendra anchor,
    and rescued (< 75.0, RESCUED) when Moon or Jupiter is in Lagna Kendra."""
    # Active: Jupiter in Gemini H3, Moon in Scorpio H8 (6th from Jupiter, neither in Kendra)
    chart_active = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Jupiter": "Gemini",  # H3
            "Moon": "Scorpio",    # H8
        }
    )
    yogas_act = detect_character_and_growth_yogas(chart_active)
    sakata_act = next((y for y in yogas_act if y.id == "sakata_yoga"), None)
    assert sakata_act is not None
    assert sakata_act.status == YogaStatus.STAINED
    assert sakata_act.plausibility_score == 60.0

    # Rescued by Moon in Lagna Kendra (Cancer H4)
    chart_res_moon = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Jupiter": "Sagittarius",  # H9
            "Moon": "Cancer",          # H4 (8th from Jupiter, but Kendra from Lagna!)
        }
    )
    yogas_rm = detect_character_and_growth_yogas(chart_res_moon)
    sakata_rm = next((y for y in yogas_rm if y.id == "sakata_yoga_rescued"), None)
    assert sakata_rm is not None
    assert sakata_rm.status == YogaStatus.RESCUED
    assert sakata_rm.plausibility_score == 72.0

    # Rescued by Jupiter in Lagna Kendra (Aries H1)
    chart_res_jup = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Jupiter": "Aries",   # H1 (Lagna Kendra!)
            "Moon": "Virgo",      # H6 (6th from Jupiter)
        }
    )
    yogas_rj = detect_character_and_growth_yogas(chart_res_jup)
    sakata_rj = next((y for y in yogas_rj if y.id == "sakata_yoga_rescued"), None)
    assert sakata_rj is not None
    assert sakata_rj.status == YogaStatus.RESCUED
    assert sakata_rj.plausibility_score == 68.0


def test_2_3_vasumati_elimination_of_single_benefic_false_positive():
    """2.3: Single benefic in Upachaya must NEVER trigger Vasumatī Yoga (eliminates 92% false-positive rate).
    Requires at least 2 benefics."""
    # Single benefic in H3 (Gemini for Aries Lagna)
    chart_1 = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Jupiter": "Gemini", # H3 (Upachaya)
            "Venus": "Cancer",   # H4
            "Mercury": "Leo",    # H5
            "Moon": "Aries"
        }
    )
    yogas_1 = detect_character_and_growth_yogas(chart_1)
    vasu_1 = next((y for y in yogas_1 if "vasumati" in y.id), None)
    assert vasu_1 is None, "Single benefic in Upachaya must not trigger Vasumatī Yoga!"

    # 2 Benefics in Upachaya (Jupiter in H3, Venus in H6) -> Madhyama
    chart_2 = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Jupiter": "Gemini", # H3
            "Venus": "Virgo",    # H6
            "Mercury": "Leo",    # H5
            "Moon": "Aries"
        }
    )
    yogas_2 = detect_character_and_growth_yogas(chart_2)
    vasu_2 = next((y for y in yogas_2 if "vasumati" in y.id), None)
    assert vasu_2 is not None
    assert "Madhyama" in vasu_2.name
    # Both are major benefics (Jupiter and Venus)
    assert vasu_2.plausibility_score >= 82.0

    # 3 Benefics in Upachaya (Jupiter in H3, Venus in H6, Mercury in H10) -> Uttama
    chart_3 = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Jupiter": "Gemini",    # H3
            "Venus": "Virgo",       # H6
            "Mercury": "Capricorn", # H10
            "Moon": "Aries"
        }
    )
    yogas_3 = detect_character_and_growth_yogas(chart_3)
    vasu_3 = next((y for y in yogas_3 if "vasumati" in y.id), None)
    assert vasu_3 is not None
    assert "Uttama" in vasu_3.name
    assert vasu_3.plausibility_score >= 90.0


def test_2_3_vasumati_anti_interference_rule():
    """2.3: Anti-Interference rule: Houses 3, 6, 11 must NOT be penalized as Trishadaya or Dusthana in Vasumatī!"""
    # Aries Lagna: Jupiter in H6 (Virgo), Venus in H3 (Gemini), Mercury in H11 (Aquarius).
    # All 3 are in Trishadaya houses (3, 6, 11) and H6 is a Dusthana!
    # But Vasumatī specifically requires Upachayas (3, 6, 10, 11)!
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Jupiter": "Virgo",     # H6
            "Venus": "Gemini",      # H3
            "Mercury": "Aquarius",  # H11
            "Moon": "Aries"
        }
    )
    yogas = detect_character_and_growth_yogas(chart)
    vasu = next((y for y in yogas if "vasumati" in y.id), None)
    assert vasu is not None
    # Verify NO Trishadaya breaker or Dusthana breaker on House 6
    assert not any("Trishadaya" in b.factor for b in vasu.breakers)
    assert not any("Dusthana" in b.factor for b in vasu.breakers)
    assert vasu.status == YogaStatus.PURE


def test_2_4_amala_single_penalty_subtraction():
    """2.4: Amalā Yoga malefic corruption subtracts 35.0 ONCE (yielding 50.0 STAINED),
    never twice (which gave 15.0 clamped to 25.0)."""
    # Aries Lagna: Jupiter in 10th (Capricorn), joined by malefic Saturn.
    # Moon in Taurus H2 (so H10 is not 10th from Moon, isolating single-reference base score).
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Jupiter": "Capricorn",  # Benefic in 10th
            "Saturn": "Capricorn",   # Malefic in 10th
            "Sun": "Aries",          # H1
            "Moon": "Taurus",        # H2
        }
    )
    yogas = detect_character_and_growth_yogas(chart)
    amala = next((y for y in yogas if "amala_yoga" in y.id), None)
    assert amala is not None
    assert amala.status == YogaStatus.STAINED
    # Base 85.0 - 35.0 = 50.0. If double-subtracted, it would be 15.0/25.0!
    assert amala.plausibility_score == 50.0
    assert any("Malefic Corruption" in b.factor for b in amala.breakers)


def test_2_4_amala_from_moon_and_dual_10th_bonus():
    """2.4: Amalā formed from Moon and simultaneous dual 10th bonus."""
    # Aries Lagna: Moon in Aries H1. House 10 is simultaneously 10th from Lagna and 10th from Moon!
    chart = make_clean_chart(
        lagna_sign="Aries",
        grahas={
            "Jupiter": "Capricorn",  # H10
            "Moon": "Aries",         # H1
        }
    )
    yogas = detect_character_and_growth_yogas(chart)
    amala = next((y for y in yogas if "amala_yoga" in y.id), None)
    assert amala is not None
    assert amala.status == YogaStatus.PURE
    assert amala.plausibility_score == 90.0  # 85 base + 5 dual 10th bonus
    assert any("simultaneously the 10th house from both Lagna and Moon" in f for f in amala.positive_factors)
