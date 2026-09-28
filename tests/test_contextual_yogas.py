"""
tests/test_contextual_yogas.py
Comprehensive unit test suite for Contextual Setup Yogas (jyotish/yogas/contextual_yogas.py).
Authority: BPHS Ch. 34, 35, 37, 38; Phaladeepika Ch. 6.
"""

import pytest
from typing import Dict, Any
from jyotish.yogas.contextual_yogas import (
    detect_sankhya_yogas,
    detect_general_scope_yogas,
    detect_mahabhagya_yogas,
    detect_solitary_first_house_yogas,
    detect_kemadruma_yoga,
    detect_solar_flanking_yogas,
    detect_dual_lagna_raja_yogas,
    detect_contextual_yogas
)
from jyotish.yogas.models import YogaStatus, YogaCategory


def make_chart(
    lagna_sign: str = "Aries",
    graha_signs: Dict[str, str] = None,
    is_day_birth: bool = True,
    gender: str = "male"
) -> Dict[str, Any]:
    """Helper to assemble a minimal mock chart for contextual yoga testing."""
    if graha_signs is None:
        graha_signs = {
            "Sun": "Aries", "Moon": "Taurus", "Mars": "Gemini",
            "Mercury": "Cancer", "Jupiter": "Leo", "Venus": "Virgo", "Saturn": "Libra"
        }
    return {
        "vargas": {
            "D1": {
                "lagna": {"sign": lagna_sign},
                "grahas": {p: {"sign": s} for p, s in graha_signs.items()}
            }
        },
        "is_day_birth": is_day_birth,
        "gender": gender
    }


# =============================================================================
# 1. SĀṄKHYA YOGAS (1 to 7 unique signs)
# =============================================================================

def test_sankhya_gola_yoga():
    """All 7 classical planets in 1 sign -> Gola Yoga."""
    grahas = {p: "Leo" for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    chart = make_chart(graha_signs=grahas)
    yogas = detect_sankhya_yogas(chart)
    assert len(yogas) == 1
    assert yogas[0].id == "sankhya_gola_yoga"
    assert yogas[0].category == YogaCategory.CONTEXTUAL


def test_sankhya_kedara_yoga():
    """All 7 classical planets in 4 unique signs -> Kedāra Yoga."""
    grahas = {
        "Sun": "Aries", "Moon": "Aries",
        "Mars": "Taurus", "Mercury": "Taurus",
        "Jupiter": "Cancer", "Venus": "Cancer",
        "Saturn": "Leo"
    }
    chart = make_chart(graha_signs=grahas)
    yogas = detect_sankhya_yogas(chart)
    assert len(yogas) == 1
    assert yogas[0].id == "sankhya_kedara_yoga"


def test_sankhya_veena_yoga():
    """All 7 classical planets in 7 distinct signs -> Vīṇā Yoga."""
    grahas = {
        "Sun": "Aries", "Moon": "Taurus", "Mars": "Gemini",
        "Mercury": "Cancer", "Jupiter": "Leo", "Venus": "Virgo", "Saturn": "Libra"
    }
    chart = make_chart(graha_signs=grahas)
    yogas = detect_sankhya_yogas(chart)
    assert len(yogas) == 1
    assert yogas[0].id == "sankhya_veena_yoga"


# =============================================================================
# 2. GENERAL SCOPE YOGAS (Sun-Moon Quadrant Geometry)
# =============================================================================

def test_general_scope_kendra():
    """Sun in Aries (1st), Moon in Cancer (4th from Sun) -> Kendra Scope."""
    chart = make_chart(lagna_sign="Aries", graha_signs={"Sun": "Aries", "Moon": "Cancer"})
    yogas = detect_general_scope_yogas(chart)
    assert any(y.id == "kendra_scope_yoga" for y in yogas)


def test_general_scope_panaphara():
    """Sun in Aries (1st), Moon in Taurus (2nd from Sun) -> Panaphara Scope."""
    chart = make_chart(lagna_sign="Aries", graha_signs={"Sun": "Aries", "Moon": "Taurus"})
    yogas = detect_general_scope_yogas(chart)
    assert any(y.id == "panaphara_scope_yoga" for y in yogas)


def test_general_scope_apoklima():
    """Sun in Aries (1st), Moon in Gemini (3rd from Sun) -> Apoklima Scope."""
    chart = make_chart(lagna_sign="Aries", graha_signs={"Sun": "Aries", "Moon": "Gemini"})
    yogas = detect_general_scope_yogas(chart)
    assert any(y.id == "apoklima_scope_yoga" for y in yogas)


# =============================================================================
# 3. MAHĀBHĀGYA YOGA
# =============================================================================

def test_mahabhagya_male_configuration():
    """Male + Day birth + Odd Lagna + Odd Sun + Odd Moon -> Mahābhāgya Yoga."""
    chart = make_chart(
        lagna_sign="Aries",  # Odd
        graha_signs={"Sun": "Leo", "Moon": "Sagittarius"},  # Both Odd
        is_day_birth=True,
        gender="male"
    )
    yogas = detect_mahabhagya_yogas(chart)
    assert any(y.id == "mahabhagya_male_yoga" and y.status == YogaStatus.PURE for y in yogas)


def test_mahabhagya_female_configuration():
    """Female + Night birth + Even Lagna + Even Sun + Even Moon -> Mahābhāgya Yoga."""
    chart = make_chart(
        lagna_sign="Taurus",  # Even
        graha_signs={"Sun": "Cancer", "Moon": "Virgo"},  # Both Even
        is_day_birth=False,
        gender="female"
    )
    yogas = detect_mahabhagya_yogas(chart)
    assert any(y.id == "mahabhagya_female_yoga" and y.status == YogaStatus.PURE for y in yogas)


# =============================================================================
# 4. SOLITARY 1ST HOUSE & FLANKING YOGAS
# =============================================================================

def test_solitary_mars_tanu():
    """Mars alone in 1st house -> Solitary Mars in 1st (Aśubha Fortitude)."""
    grahas = {
        "Mars": "Aries",  # 1st house for Aries Lagna
        "Sun": "Taurus", "Moon": "Gemini", "Jupiter": "Leo",
        "Venus": "Virgo", "Saturn": "Scorpio", "Mercury": "Capricorn"
    }
    chart = make_chart(lagna_sign="Aries", graha_signs=grahas)
    yogas = detect_solitary_first_house_yogas(chart)
    assert any(y.id == "solitary_mars_tanu_yoga" for y in yogas)


def test_solitary_jupiter_tanu():
    """Jupiter alone in 1st house -> Solitary Jupiter in 1st (Śubha Tanu)."""
    grahas = {
        "Jupiter": "Aries",  # 1st house for Aries Lagna
        "Sun": "Taurus", "Moon": "Gemini", "Mars": "Leo",
        "Venus": "Virgo", "Saturn": "Scorpio", "Mercury": "Capricorn"
    }
    chart = make_chart(lagna_sign="Aries", graha_signs=grahas)
    yogas = detect_solitary_first_house_yogas(chart)
    assert any(y.id == "solitary_jupiter_tanu_yoga" for y in yogas)


def test_shubhakartari_lagna():
    """Benefics in 2nd and 12th houses from Lagna -> Śubhakartari of Lagna."""
    grahas = {
        "Jupiter": "Taurus",  # 2nd from Aries
        "Venus": "Pisces",    # 12th from Aries
        "Sun": "Leo", "Moon": "Cancer"
    }
    chart = make_chart(lagna_sign="Aries", graha_signs=grahas)
    yogas = detect_solitary_first_house_yogas(chart)
    assert any(y.id == "shubhakartari_lagna_yoga" for y in yogas)


def test_papakartari_lagna():
    """Malefics in 2nd and 12th houses from Lagna -> Pāpakartari of Lagna."""
    grahas = {
        "Saturn": "Taurus",  # 2nd from Aries
        "Mars": "Pisces",    # 12th from Aries
        "Moon": "Cancer"
    }
    chart = make_chart(lagna_sign="Aries", graha_signs=grahas)
    yogas = detect_solitary_first_house_yogas(chart)
    assert any(y.id == "papakartari_lagna_yoga" for y in yogas)


# =============================================================================
# 5. 3-TIER KEMADRUMA YOGA & CANCELLATION
# =============================================================================

def test_full_kemadruma_yoga():
    """
    Moon in Taurus (2nd from Aries):
    - No planets in 2nd or 12th from Moon (Aries and Gemini empty)
    - Moon not in Kendra from Lagna (in 2nd house)
    - No classical planets in Kendras from Moon (Leo, Scorpio, Aquarius empty)
    -> Full Kemadruma Yoga.
    """
    grahas = {
        "Moon": "Taurus",   # 2nd house from Aries Lagna (not Kendra)
        "Sun": "Virgo",     # 5th from Moon
        "Mars": "Libra",    # 6th from Moon
        "Saturn": "Libra"
    }
    chart = make_chart(lagna_sign="Aries", graha_signs=grahas)
    yogas = detect_kemadruma_yoga(chart)
    assert any(y.id == "kemadruma_yoga" and y.status == YogaStatus.STAINED for y in yogas)


def test_kemadruma_bhanga_moon_in_kendra():
    """
    Moon in Cancer (4th Kendra from Aries Lagna):
    - No flankers in 2nd or 12th from Moon
    - BUT Moon occupies Kendra from Lagna -> Kemadruma Bhaṅga Yoga (Rescued).
    """
    grahas = {
        "Moon": "Cancer",  # 4th Kendra from Lagna
        "Sun": "Virgo",
        "Mars": "Libra"
    }
    chart = make_chart(lagna_sign="Aries", graha_signs=grahas)
    yogas = detect_kemadruma_yoga(chart)
    assert any(y.id == "kemadruma_bhanga_yoga" and y.status == YogaStatus.RESCUED for y in yogas)


def test_kemadruma_bhanga_planet_in_moon_kendra():
    """
    Moon in 2nd house (Taurus), but Jupiter is in Leo (4th Kendra from Moon)
    -> Kemadruma Bhaṅga Yoga (Rescued).
    """
    grahas = {
        "Moon": "Taurus",
        "Jupiter": "Leo",  # 4th from Moon
        "Sun": "Virgo"
    }
    chart = make_chart(lagna_sign="Aries", graha_signs=grahas)
    yogas = detect_kemadruma_yoga(chart)
    assert any(y.id == "kemadruma_bhanga_yoga" and y.status == YogaStatus.RESCUED for y in yogas)


# =============================================================================
# 6. SOLAR FLANKING YOGAS (Veśi, Vośi, Ubhayācarī)
# =============================================================================

def test_subhavesi_yoga():
    """Jupiter in 2nd from Sun (Taurus, Sun in Aries) -> Śubhaveśi Yoga."""
    grahas = {
        "Sun": "Aries",
        "Jupiter": "Taurus",
        "Moon": "Leo"
    }
    chart = make_chart(graha_signs=grahas)
    yogas = detect_solar_flanking_yogas(chart)
    assert any(y.id == "vesi_yoga" and "Śubha-" in y.name for y in yogas)


def test_subhavosi_yoga():
    """Venus in 12th from Sun (Pisces, Sun in Aries) -> Śubhavośi Yoga."""
    grahas = {
        "Sun": "Aries",
        "Venus": "Pisces",
        "Moon": "Leo"
    }
    chart = make_chart(graha_signs=grahas)
    yogas = detect_solar_flanking_yogas(chart)
    assert any(y.id == "vosi_yoga" and "Śubha-" in y.name for y in yogas)


def test_subha_ubhayacari_yoga():
    """Benefics in both 2nd (Jupiter) and 12th (Venus) from Sun -> Śubha-Ubhayācarī Yoga."""
    grahas = {
        "Sun": "Aries",
        "Jupiter": "Taurus",  # 2nd
        "Venus": "Pisces",    # 12th
        "Moon": "Leo"
    }
    chart = make_chart(graha_signs=grahas)
    yogas = detect_solar_flanking_yogas(chart)
    assert any(y.id == "ubhayacari_yoga" and "Śubha-" in y.name for y in yogas)


# =============================================================================
# 7. DUAL-LAGNA RAJA YOGA (Ubhayalagna)
# =============================================================================

def test_ubhayalagna_raja_yoga():
    """
    Sagittarius Lagna and Sagittarius Moon (Janma Lagna == Candra Lagna).
    Sun rules 9th house (Leo), Mercury rules 10th house (Virgo).
    Sun and Mercury conjunct in Leo -> Ubhayalagna Raja Yoga (Sun + Mercury).
    """
    grahas = {
        "Moon": "Sagittarius",
        "Sun": "Leo",
        "Mercury": "Leo",
        "Jupiter": "Aries",
        "Mars": "Taurus",
        "Venus": "Gemini",
        "Saturn": "Libra"
    }
    chart = make_chart(lagna_sign="Sagittarius", graha_signs=grahas)
    yogas = detect_dual_lagna_raja_yogas(chart)
    assert any("ubhayalagna_raja_yoga" in y.id for y in yogas)


# =============================================================================
# 8. MASTER ORCHESTRATOR
# =============================================================================

def test_detect_contextual_yogas_master():
    """Verify that detect_contextual_yogas orchestrates all categories seamlessly."""
    chart = make_chart()
    all_contextual = detect_contextual_yogas(chart)
    assert len(all_contextual) > 0
    assert all(isinstance(y.category, YogaCategory) for y in all_contextual)
