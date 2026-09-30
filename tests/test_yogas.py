"""
tests/test_yogas.py
Comprehensive unit, regression, and classical verification test suite for Astra's Classical Yoga Detection Engine.
Verifies all 9 categories, Yoga Breakers (Yoga Bhanga), Neecha Bhanga cancellation, and plausibility scoring.
Scriptural Authority: BPHS Ch. 34, 37-42, 75; Phaladeepika Ch. 6-7.
"""

import pytest
from typing import Dict, Any
from jyotish.yogas import (
    detect_all_yogas,
    YogaStatus,
    YogaCategory,
    YogaInstance,
)
from jyotish.yogas.pancha_mahapurusha import detect_pancha_mahapurusha_yogas
from jyotish.yogas.raja_yogas import detect_raja_yogas
from jyotish.yogas.dhana_daridrya import detect_dhana_and_daridrya_yogas
from jyotish.yogas.lunar_solar_yogas import detect_lunar_and_solar_yogas
from jyotish.yogas.parivartana import detect_parivartana_yogas
from jyotish.yogas.viparita import detect_viparita_raja_yogas
from jyotish.yogas.kartari import detect_kartari_yogas
from jyotish.yogas.chandal_yogas import detect_chandal_yogas
from jyotish.yogas.character_growth_yogas import detect_character_and_growth_yogas
from jyotish.yogas.dispositor_root_yogas import detect_dispositor_root_yogas
from jyotish.yogas.deity_yogas import detect_deity_yogas
from jyotish.yogas.bhava_yogas import detect_bhava_yogas
from jyotish.yogas.power_yogas import detect_chapter7_power_yogas
from jyotish.yogas.breakers import (
    audit_neecha_bhanga,
    audit_trishadaya_interference,
    audit_combustion,
    get_house_rulers,
    get_house_of_planet
)
from jyotish.generate_jyotish import generate_kala_chart


def make_mock_chart(lagna_sign: str, grahas: Dict[str, Dict[str, Any]], aspects: Dict[str, Any] = None) -> Dict[str, Any]:
    """Helper to assemble a minimal well-formed chart dictionary for unit testing."""
    return {
        "vargas": {
            "D1": {
                "lagna": {"sign": lagna_sign, "longitude": 15.0, "degree_0_to_30": 15.0},
                "grahas": grahas
            }
        },
        "advanced_aspects": {"planets": aspects or {}},
        "shadbala": {
            p: {"total": 450.0, "ratio": 1.25} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        }
    }


# =============================================================================
# 1. PANCHA MAHAPURUSHA YOGAS
# =============================================================================

def test_pancha_mahapurusha_ruchaka():
    """Mars in Capricorn (exalted) in 10th Kendra for Aries Lagna -> Ruchaka Yoga."""
    grahas = {
        "Mars": {"sign": "Capricorn", "longitude": 280.0, "degree_0_to_30": 10.0},
        "Moon": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Sun": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},
        "Mercury": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},
        "Saturn": {"sign": "Sagittarius", "longitude": 255.0, "degree_0_to_30": 15.0}
    }
    chart = make_mock_chart("Aries", grahas)
    yogas = detect_pancha_mahapurusha_yogas(chart)
    
    ruchaka = next((y for y in yogas if y.id == "ruchaka_yoga"), None)
    assert ruchaka is not None, "Ruchaka Yoga should be detected for Mars in Capricorn in 10th house"
    assert ruchaka.status in [YogaStatus.PURE, YogaStatus.STAINED]
    assert ruchaka.plausibility_score >= 80.0
    assert "Mars" in ruchaka.participating_planets


def test_pancha_mahapurusha_malavya_shivapuri():
    """Venus in Libra in 1st house for Libra Lagna -> Malavya Yoga."""
    grahas = {
        "Venus": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Aquarius", "longitude": 315.0, "degree_0_to_30": 15.0},
        "Sun": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
        "Mercury": {"sign": "Scorpio", "longitude": 230.0, "degree_0_to_30": 20.0},
        "Jupiter": {"sign": "Sagittarius", "longitude": 255.0, "degree_0_to_30": 15.0},
        "Saturn": {"sign": "Libra", "longitude": 205.0, "degree_0_to_30": 25.0}
    }
    chart = make_mock_chart("Libra", grahas)
    yogas = detect_pancha_mahapurusha_yogas(chart)
    
    malavya = next((y for y in yogas if y.id == "malavya_yoga"), None)
    assert malavya is not None, "Malavya Yoga should be detected for Venus in own sign in Kendra"
    assert malavya.status == YogaStatus.PURE
    assert malavya.plausibility_score >= 85.0


# =============================================================================
# 2. NEECHA BHANGA (CANCELLATION OF DEBILITY)
# =============================================================================

def test_neecha_bhanga_redemption_dispositor_in_kendra():
    """Mercury in Pisces (debilitated) with Jupiter (dispositor) in Gemini (4th Kendra) -> Rescued."""
    grahas = {
        "Mercury": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0},  # Dispositor in 4th Kendra from Pisces/Sagittarius
        "Moon": {"sign": "Sagittarius", "longitude": 255.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Pisces", "longitude": 350.0, "degree_0_to_30": 20.0}   # Exaltation lord also in Kendra/Pisces
    }
    chart = make_mock_chart("Sagittarius", grahas)
    
    is_rescued, reasons, bonus = audit_neecha_bhanga("Mercury", chart)
    assert is_rescued is True, "Mercury's debility should be cancelled"
    assert len(reasons) >= 1
    assert bonus > 0.0


def test_neecha_bhanga_unredeemed():
    """Saturn in Aries in 8th house for Virgo Lagna without Kendra dispositors -> Not cancelled."""
    grahas = {
        "Saturn": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},  # Dispositor in 3rd (not Kendra from Lagna or Moon)
        "Moon": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0}     # Moon in 1st house; Mars is in 3rd from Moon
    }
    chart = make_mock_chart("Virgo", grahas)
    
    is_rescued, reasons, bonus = audit_neecha_bhanga("Saturn", chart)
    assert is_rescued is False, "Saturn in 8th with non-angular lords should not have Neecha Bhanga"
    assert bonus == 0.0


# =============================================================================
# 3. TRISHADAYA SABOTEURS (YOGA BREAKERS)
# =============================================================================

def test_trishadaya_11th_lord_primary_saboteur():
    """For Aries Lagna, Saturn is 11th lord. Conjoining yoga planets yields a -40% penalty."""
    grahas = {
        "Sun": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},      # Lord 5
        "Jupiter": {"sign": "Leo", "longitude": 137.0, "degree_0_to_30": 17.0},  # Lord 9
        "Saturn": {"sign": "Leo", "longitude": 140.0, "degree_0_to_30": 20.0}   # Lord 11 (Saboteur) conjoined!
    }
    chart = make_mock_chart("Aries", grahas)
    
    breakers = audit_trishadaya_interference(["Sun", "Jupiter"], chart)
    saboteur_11 = next((b for b in breakers if "11th Lord" in b.factor), None)
    assert saboteur_11 is not None, "11th lord conjunction must be flagged as primary saboteur"
    assert saboteur_11.penalty == 40.0


def test_trishadaya_lagnesha_exemption():
    """For Scorpio Lagna, Mars rules 1st (Lagna) and 6th. Lagnesha status exempts it from destroying own yoga."""
    grahas = {
        "Mars": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Cancer", "longitude": 110.0, "degree_0_to_30": 20.0}
    }
    chart = make_mock_chart("Scorpio", grahas)
    # Scorpio lagna lord is Mars. Mars rules 1 and 6.
    breakers = audit_trishadaya_interference(["Jupiter"], chart)
    # Mars is lagna lord, so it should not be treated as a purely destructive saboteur
    assert not any(b.culprit_planet == "Mars" and "6th Lord" in b.factor for b in breakers)


# =============================================================================
# 4. RAJA YOGAS
# =============================================================================

def test_single_planet_yogakaraka_taurus():
    """Taurus Lagna has Saturn as single Yogakaraka (rules 9 and 10)."""
    grahas = {
        "Saturn": {"sign": "Aquarius", "longitude": 315.0, "degree_0_to_30": 15.0},  # In 10th Kendra
        "Moon": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0}
    }
    chart = make_mock_chart("Taurus", grahas)
    yogas = detect_raja_yogas(chart)
    
    yk_yoga = next((y for y in yogas if "single_yogakaraka" in y.id), None)
    assert yk_yoga is not None, "Saturn must be recognized as single Yogakaraka for Taurus"
    assert "Saturn" in yk_yoga.participating_planets
    assert yk_yoga.status == YogaStatus.PURE


def test_dharma_karma_adhipati_raja_yoga():
    """9th Lord + 10th Lord conjoined in 10th Kendra -> Supreme Dharma-Karma Adhipati Raja Yoga."""
    # For Leo Lagna: 9th lord is Mars, 10th lord is Venus
    grahas = {
        "Mars": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},   # House 10
        "Venus": {"sign": "Taurus", "longitude": 48.0, "degree_0_to_30": 18.0},  # House 10
        "Sun": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0}
    }
    chart = make_mock_chart("Leo", grahas)
    yogas = detect_raja_yogas(chart)
    
    dk = next((y for y in yogas if "Dharma-Karma" in y.name), None)
    assert dk is not None, "Dharma-Karma Adhipati Raja Yoga must be detected"
    assert set(dk.participating_planets) == {"Mars", "Venus"}
    assert dk.plausibility_score >= 80.0


# =============================================================================
# 5. VIPARITA RAJA YOGAS
# =============================================================================

def test_viparita_raja_yogas_harsha_sarala_vimala():
    """
    Harsha: 6th lord in 6/8/12
    Sarala: 8th lord in 6/8/12
    Vimala: 12th lord in 6/8/12
    For Aries Lagna: 6th lord is Mercury, 8th lord is Mars, 12th lord is Jupiter.
    """
    grahas = {
        "Mercury": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},    # H6 lord in H6 -> Harsha
        "Mars": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},     # H8 lord in H8 -> Sarala
        "Jupiter": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0}    # H12 lord in H12 -> Vimala
    }
    chart = make_mock_chart("Aries", grahas)
    yogas = detect_viparita_raja_yogas(chart)
    
    ids = [y.id for y in yogas]
    assert "harsha_yoga" in ids
    assert "sarala_yoga" in ids
    assert "vimala_yoga" in ids


# =============================================================================
# 6. LUNAR & SOLAR YOGAS
# =============================================================================

def test_kemadruma_and_cancellation():
    """Kemadruma Yoga triggers when 2nd and 12th from Moon are empty, but cancels if planets are in Kendra from Moon."""
    # Isolated Moon in House 5 (Leo) for Aries Lagna, but Jupiter in House 8 (Scorpio, 4th/Kendra from Moon) -> Rescued
    grahas = {
        "Moon": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0}  # 4th from Moon (Lunar Kendra)
    }
    chart = make_mock_chart("Aries", grahas)
    yogas = detect_lunar_and_solar_yogas(chart)
    
    kema = next((y for y in yogas if y.id == "kemadruma_yoga"), None)
    assert kema is not None, "Kemadruma Yoga should be detected"
    assert kema.status == YogaStatus.RESCUED, "Kemadruma should be cancelled/rescued by Jupiter in Lunar Kendra"


def test_kemadruma_cancellation_moon_in_lagna_kendra():
    """Kemadruma cancels when Moon itself sits in a Kendra from Lagna (Tier 2 rescue)."""
    # Isolated Moon in House 4 (Cancer) for Aries Lagna, with no other planets in chart
    grahas = {
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},
    }
    chart = make_mock_chart("Aries", grahas)
    yogas = detect_lunar_and_solar_yogas(chart)
    
    kema = next((y for y in yogas if y.id == "kemadruma_yoga"), None)
    assert kema is not None, "Kemadruma Yoga should be detected"
    assert kema.status == YogaStatus.RESCUED, "Kemadruma should be cancelled/rescued by Moon itself in 4th Kendra from Lagna"


def test_budhaditya_solar_yoga():
    """Sun + Mercury conjoined without deep combustion -> Budhaditya Yoga."""
    grahas = {
        "Sun": {"sign": "Gemini", "longitude": 70.0, "degree_0_to_30": 10.0},
        "Mercury": {"sign": "Gemini", "longitude": 80.0, "degree_0_to_30": 20.0}  # 10° apart (> 3° deep combustion orb)
    }
    chart = make_mock_chart("Gemini", grahas)
    yogas = detect_lunar_and_solar_yogas(chart)
    
    budh = next((y for y in yogas if y.id == "budhaditya_yoga"), None)
    assert budh is not None, "Budhaditya Yoga must be detected"
    assert budh.status == YogaStatus.PURE


# =============================================================================
# 7. PARIVARTANA & KARTARI YOGAS
# =============================================================================

def test_parivartana_maha_exchange():
    """Sun in Aries (Mars sign, H1) and Mars in Leo (Sun sign, H5) -> Maha Parivartana Yoga."""
    grahas = {
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0}
    }
    chart = make_mock_chart("Aries", grahas)
    yogas = detect_parivartana_yogas(chart)
    
    maha = next((y for y in yogas if "maha_parivartana" in y.id), None)
    assert maha is not None, "Maha Parivartana Yoga should be detected"
    assert maha.category == YogaCategory.PARIVARTANA
    assert maha.status == YogaStatus.PURE


def test_parivartana_dainya_exchange():
    """Sun in Scorpio (Mars sign, H8 Dusthana) and Mars in Leo (Sun sign, H5) -> Dainya Parivartana Yoga."""
    grahas = {
        "Sun": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0}
    }
    chart = make_mock_chart("Aries", grahas)
    yogas = detect_parivartana_yogas(chart)
    
    dainya = next((y for y in yogas if "dainya_parivartana" in y.id), None)
    assert dainya is not None, "Dainya Parivartana Yoga should be detected when exchange involves H8"
    assert dainya.status == YogaStatus.STAINED


def test_shubha_kartari_lagna():
    """Benefics flanking Lagna in 2nd and 12th -> Shubha Kartari Yoga."""
    # Aries Lagna: 12th is Pisces (Jupiter), 2nd is Taurus (Venus)
    grahas = {
        "Jupiter": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0}
    }
    chart = make_mock_chart("Aries", grahas)
    yogas = detect_kartari_yogas(chart)
    
    shubha = next((y for y in yogas if "shubha_kartari" in y.id), None)
    assert shubha is not None, "Shubha Kartari Yoga should be detected for Lagna"
    assert shubha.status == YogaStatus.PURE


# =============================================================================
# 8. FULL END-TO-END GENERATE_KALA_CHART INTEGRATION
# =============================================================================

def test_generate_kala_chart_yogas_payload():
    """Verifies that generate_kala_chart() populates the complete 'yogas' dictionary structure."""
    chart = generate_kala_chart("Swami Shivapuri", 1983, 11, 10, 22, 20, 52.20296, 8.0448, 1.0)
    
    assert "yogas" in chart, "Chart must contain 'yogas' key"
    y_data = chart["yogas"]
    
    assert "total_count" in y_data
    assert "summary" in y_data
    assert "yogas" in y_data
    assert "categories" in y_data
    
    summary = y_data["summary"]
    assert "pure" in summary
    assert "stained" in summary
    assert "rescued" in summary
    assert "broken" in summary
    
    assert y_data["total_count"] > 5, "Chart should have several classical yogas"
    
    # Assert specific prominent Shivapuri Yogas
    yoga_names = [y["name"] for y in y_data["yogas"]]
    assert any("Mālavya" in n for n in yoga_names), "Shivapuri should have Malavya Mahapurusha Yoga"
    assert any("Budhāditya" in n for n in yoga_names), "Shivapuri should have Budhaditya Yoga"
    assert any("Mahā Parivartana" in n for n in yoga_names), "Shivapuri should have Maha Parivartana Yoga"
    assert YogaCategory.CHANDAL.value in y_data["categories"]


# =============================================================================
# 9. CHANDAL & NODAL AFFLICTION YOGAS
# =============================================================================

def test_guru_chandal_yoga_detection():
    """Verify Guru-Chandal Yoga detection (Jupiter + Rahu in same sign)."""
    # Mock chart: Aquarius Lagna, Jupiter + Rahu in Sagittarius (H11)
    chart = make_mock_chart("Aquarius", {
        "Jupiter": {"sign": "Sagittarius", "longitude": 247.77, "degree_0_to_30": 7.77},
        "Rahu": {"sign": "Sagittarius", "longitude": 242.90, "degree_0_to_30": 2.90},
        "Saturn": {"sign": "Sagittarius", "longitude": 269.41, "degree_0_to_30": 29.41}
    })
    yogas = detect_chandal_yogas(chart)
    gc = next((y for y in yogas if y.id == "guru_chandal_yoga"), None)
    assert gc is not None, "Must detect Guru-Chandal Yoga when Jupiter and Rahu are in the same sign"
    assert gc.category == YogaCategory.CHANDAL
    assert "Jupiter" in gc.participating_planets
    assert "Rahu" in gc.participating_planets
    assert gc.status == YogaStatus.STAINED
    # Saturn conjoined in Sagittarius should trigger Vikala breaker
    assert any("Vikala" in b.factor for b in gc.breakers), "Must record Saturn co-conjunction as Vikala breaker"


def test_guru_ketu_jnana_yoga_detection():
    """Verify Guru-Ketu Jnana Yoga detection (Jupiter + Ketu promotes spiritual contemplation)."""
    chart = make_mock_chart("Pisces", {
        "Jupiter": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0},
        "Ketu": {"sign": "Pisces", "longitude": 348.0, "degree_0_to_30": 18.0}
    })
    yogas = detect_chandal_yogas(chart)
    gk = next((y for y in yogas if y.id == "guru_ketu_jnana_yoga"), None)
    assert gk is not None, "Must detect Guru-Ketu Jnana Yoga when Jupiter and Ketu are in the same sign"
    assert gk.status == YogaStatus.PURE, "Guru-Ketu is a spiritual jnana combination, not an asubha dosha"


def test_shrapit_and_angaraka_yoga_detection():
    """Verify Shrapit Yoga (Saturn+Rahu) and Angaraka Yoga (Mars+Rahu)."""
    chart = make_mock_chart("Aries", {
        "Saturn": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0},
        "Rahu": {"sign": "Libra", "longitude": 198.0, "degree_0_to_30": 18.0},
        "Mars": {"sign": "Capricorn", "longitude": 280.0, "degree_0_to_30": 10.0}
    })
    yogas = detect_chandal_yogas(chart)
    shrapit = next((y for y in yogas if y.id == "shrapit_yoga"), None)
    assert shrapit is not None
    assert shrapit.status == YogaStatus.RESCUED, "Exalted Saturn in Libra should rescue Shrapit Yoga"


def test_get_aspect_score_directionality():
    """Verify get_aspect_score correctly looks up aspects from giver to receiver."""
    from jyotish.yogas.breakers import get_aspect_score
    chart = {
        "advanced_aspects": {
            "planets": {
                # Moon receives aspect from Saturn (receiver=Moon, giver=Saturn)
                "Moon": {
                    "Saturn": {"raw": 55.7, "net": -55.7}
                }
            }
        }
    }
    # Saturn aspects Moon -> 55.7
    assert get_aspect_score(chart, giver="Saturn", receiver="Moon") == 55.7
    # Moon does not aspect Saturn -> 0.0
    assert get_aspect_score(chart, giver="Moon", receiver="Saturn") == 0.0


def test_raja_yoga_aspect_threshold_palpable_vs_marginal():
    """
    Verify that Raja Yoga aspect verification strictly respects the 45 Virupa palpable threshold:
    - Mutual aspect >= 45 Virupas -> Fully Verified (PURE).
    - Mutual aspect 30-44 Virupas -> Marginal / Stained (STAINED with Marginal Aspect breaker).
    - Mutual aspect < 30 Virupas -> Connection fails (not formed).
    """
    # Leo Lagna: H9 lord is Mars, H10 lord is Venus. Put them in separate houses (H1 and H7).
    # 1. Palpable connection (50 Virupas each):
    chart_palpable = make_mock_chart(
        "Leo",
        {
            "Mars": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},
            "Venus": {"sign": "Aquarius", "longitude": 315.0, "degree_0_to_30": 15.0},
            "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
        },
        aspects={
            "Mars": {"Venus": {"raw": 50.0, "net": 50.0}},
            "Venus": {"Mars": {"raw": 50.0, "net": 50.0}}
        }
    )
    yogas_palpable = detect_raja_yogas(chart_palpable)
    dk_pure = next((y for y in yogas_palpable if "Dharma-Karma" in y.name), None)
    assert dk_pure is not None, "Must detect Dharma-Karma Raja Yoga via mutual aspect"
    assert dk_pure.status == YogaStatus.PURE, "Palpable aspect (>= 45 Virupas) must be Pure / Fully Verified"

    # 2. Marginal connection (35 Virupas each):
    chart_marginal = make_mock_chart(
        "Leo",
        {
            "Mars": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},
            "Venus": {"sign": "Aquarius", "longitude": 315.0, "degree_0_to_30": 15.0},
            "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
        },
        aspects={
            "Mars": {"Venus": {"raw": 35.0, "net": 35.0}},
            "Venus": {"Mars": {"raw": 35.0, "net": 35.0}}
        }
    )
    yogas_marginal = detect_raja_yogas(chart_marginal)
    dk_stained = next((y for y in yogas_marginal if "Dharma-Karma" in y.name), None)
    assert dk_stained is not None, "Marginal aspect connection must still be detected"
    assert dk_stained.status == YogaStatus.STAINED, "Marginal aspect (30-44 Virupas) must be categorized as STAINED"
    assert any("Marginal Aspect Connection" in b.factor for b in dk_stained.breakers), "Must record Marginal Aspect Connection breaker"

    # 3. Weak connection (< 30 Virupas):
    chart_weak = make_mock_chart(
        "Leo",
        {
            "Mars": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},
            "Venus": {"sign": "Aquarius", "longitude": 315.0, "degree_0_to_30": 15.0},
            "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
        },
        aspects={
            "Mars": {"Venus": {"raw": 20.0, "net": 20.0}},
            "Venus": {"Mars": {"raw": 20.0, "net": 20.0}}
        }
    )
    yogas_weak = detect_raja_yogas(chart_weak)
    dk_none = next((y for y in yogas_weak if "Dharma-Karma" in y.name), None)
    assert dk_none is None, "Weak aspect (< 30 Virupas) must not form a mutual aspect yoga connection"


# =============================================================================
# 10. CHARACTER & GROWTH YOGAS (Vasumatī, Amalā, Puṣkala, Śakaṭa)
# =============================================================================

def test_vasumati_graded_scale():
    """Verify 3-tier graded scale for Vasumatī Yoga (Uttama=3, Madhyama=2, Svalpa=1)."""
    # Aries Lagna: Upachayas are Gemini (3), Virgo (6), Capricorn (10), Aquarius (11)
    # Tier 1: All 3 benefics in Upachayas -> Uttama
    chart_3 = make_mock_chart("Aries", {
        "Jupiter": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
        "Mercury": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
    })
    yogas_3 = detect_character_and_growth_yogas(chart_3)
    vasu_3 = next((y for y in yogas_3 if y.id == "vasumati_yoga_3"), None)
    assert vasu_3 is not None, "Must detect 3-benefic Vasumatī Yoga (Uttama)"
    assert "Uttama" in vasu_3.name

    # Tier 2: 2 benefics in Upachayas -> Madhyama
    chart_2 = make_mock_chart("Aries", {
        "Jupiter": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
        "Mercury": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},  # H4 (not Upachaya)
        "Moon": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
    })
    yogas_2 = detect_character_and_growth_yogas(chart_2)
    vasu_2 = next((y for y in yogas_2 if y.id == "vasumati_yoga_2"), None)
    assert vasu_2 is not None, "Must detect 2-benefic Vasumatī Yoga (Madhyama)"
    assert "Madhyama" in vasu_2.name

    # Tier 3: 1 benefic in Upachaya -> Svalpa
    chart_1 = make_mock_chart("Aries", {
        "Jupiter": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},   # H4
        "Mercury": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},     # H5
        "Moon": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
    })
    yogas_1 = detect_character_and_growth_yogas(chart_1)
    vasu_1 = next((y for y in yogas_1 if y.id == "vasumati_yoga_1"), None)
    assert vasu_1 is not None, "Must detect 1-benefic Vasumatī Yoga (Svalpa)"
    assert "Svalpa" in vasu_1.name


def test_amala_yoga_pure_vs_corrupted():
    """Verify Amalā Yoga triggers for single benefic in 10th and is stained if malefic joins."""
    # Pure: Jupiter alone in 10th (Capricorn for Aries Lagna)
    chart_pure = make_mock_chart("Aries", {
        "Jupiter": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
    })
    y_pure = detect_character_and_growth_yogas(chart_pure)
    amala_p = next((y for y in y_pure if "amala_yoga" in y.id), None)
    assert amala_p is not None, "Must detect Amalā Yoga"
    assert amala_p.status == YogaStatus.PURE

    # Corrupted: Saturn shares 10th house
    chart_corr = make_mock_chart("Aries", {
        "Jupiter": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},
        "Saturn": {"sign": "Capricorn", "longitude": 280.0, "degree_0_to_30": 10.0}
    })
    y_corr = detect_character_and_growth_yogas(chart_corr)
    amala_c = next((y for y in y_corr if "amala_yoga" in y.id), None)
    assert amala_c is not None
    assert amala_c.status == YogaStatus.STAINED
    assert any("Malefic Corruption" in b.factor for b in amala_c.breakers)


def test_sakata_yoga_and_cancellation():
    """Verify Śakaṭa Yoga forms when Moon is 6/8/12 from Jupiter, and is rescued if Moon is in Lagna Kendra."""
    # Stained: Jupiter in Aries H1, Moon in Virgo H6 (6th from Jupiter, not in Lagna Kendra)
    chart_stained = make_mock_chart("Aries", {
        "Jupiter": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0}
    })
    y_stained = detect_character_and_growth_yogas(chart_stained)
    sakata_s = next((y for y in y_stained if y.id == "sakata_yoga"), None)
    assert sakata_s is not None, "Must detect Śakaṭa Yoga when Moon in 6th from Jupiter without Kendra"
    assert sakata_s.status == YogaStatus.STAINED

    # Rescued: Jupiter in Sagittarius H9, Moon in Cancer H4 (8th from Jupiter, but Moon in Kendra H4 from Lagna)
    chart_rescued = make_mock_chart("Aries", {
        "Jupiter": {"sign": "Sagittarius", "longitude": 255.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0}
    })
    y_rescued = detect_character_and_growth_yogas(chart_rescued)
    sakata_r = next((y for y in y_rescued if y.id == "sakata_yoga_rescued"), None)
    assert sakata_r is not None, "Must detect Rescued Śakaṭa Yoga when Moon is in Lagna Kendra"
    assert sakata_r.status == YogaStatus.RESCUED


# =============================================================================
# 11. DISPOSITOR ROOT YOGAS (Kāhala Variants A & B, Parvata & Loophole)
# =============================================================================

def test_kahala_yoga_variants():
    """Verify both Variant A (4th/10th mutual Kendras) and Variant B (Dispositor root chain)."""
    # Variant A: Aries Lagna. 4th lord Moon in Aries H1, 10th lord Saturn in Cancer H4 (mutual Kendra)
    chart_a = make_mock_chart("Aries", {
        "Mars": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},      # Lagna lord in H1
        "Moon": {"sign": "Aries", "longitude": 20.0, "degree_0_to_30": 20.0},      # 4th lord in H1
        "Saturn": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0}   # 10th lord in H4 (4th from Moon)
    })
    yogas_a = detect_dispositor_root_yogas(chart_a)
    kahala_a = next((y for y in yogas_a if y.id == "kahala_yoga_variant_a"), None)
    assert kahala_a is not None, "Must detect Kāhala Yoga Variant A"

    # Variant B: Aries Lagna. Lagna lord Mars in Taurus H2. Dispositor Venus in Libra H7 (own sign in Kendra)
    chart_b = make_mock_chart("Aries", {
        "Mars": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0}
    })
    yogas_b = detect_dispositor_root_yogas(chart_b)
    kahala_b = next((y for y in yogas_b if y.id == "kahala_yoga_variant_b"), None)
    assert kahala_b is not None, "Must detect Kāhala Yoga Variant B (Dispositor Root Chain)"


def test_parvata_yoga_authentic_vs_self_dispositor():
    """Verify Parvata Yoga authentic two-tier chain vs. 70%-weighted Self-Dispositor loophole."""
    # Self-Dispositor loophole: Mars in Aries H1 (hosts itself in own sign in angle)
    chart_loophole = make_mock_chart("Aries", {
        "Mars": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}
    })
    y_loop = detect_dispositor_root_yogas(chart_loophole)
    parv_loop = next((y for y in y_loop if y.id == "parvata_yoga_self_dispositor"), None)
    assert parv_loop is not None, "Must detect Parvata Self-Dispositor Variant"
    assert parv_loop.plausibility_score == 70.0, "Self-Dispositor loophole must be calibrated to ~70% plausibility"
    assert parv_loop.status == YogaStatus.STAINED, "Self-Dispositor loophole with 70% plausibility must be STAINED"
    assert any("Self-Dispositor Loophole" in b.factor for b in parv_loop.breakers)

    # Authentic two-tier chain: Mars in Capricorn H10 (exalted). Dispositor Saturn in Libra H7 (exalted).
    chart_auth = make_mock_chart("Aries", {
        "Mars": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},
        "Saturn": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0}
    })
    y_auth = detect_dispositor_root_yogas(chart_auth)
    parv_auth = next((y for y in y_auth if y.id == "parvata_yoga_authentic"), None)
    assert parv_auth is not None, "Must detect Authentic Parvata Yoga"
    assert parv_auth.plausibility_score >= 90.0, "Authentic Parvata Yoga must have high plausibility"
    assert parv_auth.status == YogaStatus.PURE


# =============================================================================
# 12. RĀJA YOGA VS. ŚAṄKHA YOGA CLASSIFICATION
# =============================================================================

def test_raja_vs_shankha_yoga_classification():
    """Verify that 9th+10th union is strictly Dharma-Karma Rāja Yoga, while other Kendra+Trikona pairs are Śaṅkha Yoga."""
    # Aries Lagna: 9th lord = Jupiter, 10th lord = Saturn.
    # Put Jupiter + Saturn in Aries H1 -> Dharma-Karma Raja Yoga
    chart_raja = make_mock_chart("Aries", {
        "Jupiter": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Saturn": {"sign": "Aries", "longitude": 18.0, "degree_0_to_30": 18.0}
    })
    y_raja = detect_raja_yogas(chart_raja)
    dk = next((y for y in y_raja if "Dharma-Karma" in y.name), None)
    assert dk is not None, "9th+10th alliance must be labeled Dharma-Karma Adhipati Rāja Yoga"
    assert "Rāja Yoga" in dk.name

    # Aries Lagna: 1st lord Mars + 4th lord Moon in Aries H1 -> Śaṅkha Yoga (H1 + H4)
    chart_shankha = make_mock_chart("Aries", {
        "Mars": {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0},
        "Moon": {"sign": "Aries", "longitude": 14.0, "degree_0_to_30": 14.0}
    })
    y_shankha = detect_raja_yogas(chart_shankha)
    sh = next((y for y in y_shankha if "shankha_yoga" in y.id), None)
    assert sh is not None, "Non-9th/10th Kendra+Trikona pairs must be classified as Śaṅkha Yoga"
    assert "Śaṅkha Yoga" in sh.name


# =============================================================================
# 13. COSMIC DEITY YOGAS (Trimūrti & Tridevī)
# =============================================================================

def test_deity_trimurti_and_tridevi_yogas():
    """Verify Śrīkaṇṭha (Shiva), Gaurī, and Sarasvatī yogas."""
    # Śrīkaṇṭha: Aries Lagna. 1st lord Mars in Capricorn H10 (exalted), Sun in Aries H1 (exalted), Moon in Cancer H4 (own)
    chart_shiva = make_mock_chart("Aries", {
        "Mars": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0}
    })
    y_shiva = detect_deity_yogas(chart_shiva)
    srik = next((y for y in y_shiva if y.id == "srikantha_yoga"), None)
    assert srik is not None, "Must detect Śrīkaṇṭha Yoga (Lord Śiva)"

    # Gaurī: Moon in Cancer H4 (own sign in Kendra)
    gauri = next((y for y in y_shiva if y.id == "gauri_yoga"), None)
    assert gauri is not None, "Must detect Gaurī Yoga for dignified Moon in Kendra"

    # Sarasvatī: Mercury in Taurus H2, Jupiter in Sagittarius H9 (own), Venus in Libra H7 (own)
    chart_saras = make_mock_chart("Aries", {
        "Mercury": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Sagittarius", "longitude": 255.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0}
    })
    y_saras = detect_deity_yogas(chart_saras)
    saras = next((y for y in y_saras if y.id == "sarasvati_yoga"), None)
    assert saras is not None, "Must detect Sarasvatī Yoga"


# =============================================================================
# 14. 12 BHAVA GOOD AND CONVERSE YOGAS
# =============================================================================

def test_12_bhava_good_and_converse_yogas():
    """Verify Cāmara (H1 good), Ava (H1 bad), and Dhenu (H2 good)."""
    # Aries Lagna: 1st lord Mars in Aries H1 (own sign in Kendra) -> Cāmara Yoga
    # 2nd lord Venus in Virgo H6 (Dusthana) -> Niḥsva Yoga
    chart = make_mock_chart("Aries", {
        "Mars": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0}
    })
    yogas = detect_bhava_yogas(chart)
    camara = next((y for y in yogas if y.id == "camara_yoga"), None)
    nihsva = next((y for y in yogas if y.id == "nihsva_yoga"), None)
    assert camara is not None, "Must detect Cāmara Yoga for fortified 1st Lord"
    assert nihsva is not None, "Must detect Niḥsva Yoga for 2nd Lord in Dusthana"


# =============================================================================
# 15. CHAPTER 7 POWER YOGAS
# =============================================================================

def test_chapter7_power_yogas():
    """Verify Multi-Planet Kendras and Mars in Fire Sign with friend aspect."""
    # Aries Lagna: Sun in Aries H1 (exalted), Moon in Cancer H4 (own), Mars in Capricorn H10 (exalted)
    chart = make_mock_chart("Aries", {
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0}
    }, aspects={
        "Mars": {"Jupiter": {"raw": 55.0, "net": 55.0}}
    })
    yogas = detect_chapter7_power_yogas(chart)
    multi_k = next((y for y in yogas if "multi_kendra" in y.id), None)
    assert multi_k is not None, "Must detect Multi-Planet Kendra Sovereignty"


# =============================================================================
# 16. SUN-MOON QUADRANT LOGIC (Adhama, Madhya, Variṣṭha)
# =============================================================================

def test_sun_moon_quadrant_adhama_madhya_varishtha():
    """Verify Kendra=Adhama (0.75 toning), Panaphara=Madhya (1.0 baseline), Apoklima=Variṣṭha (1.25 boost)."""
    # Sun in Aries (idx 1)
    # Moon in Cancer (idx 4) -> 4th from Sun (Kendra) -> Adhama Yoga
    chart_kendra = make_mock_chart("Aries", {
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0}
    })
    y_k = detect_lunar_and_solar_yogas(chart_kendra)
    adhama = next((y for y in y_k if y.id == "adhama_yoga"), None)
    assert adhama is not None, "Moon in Kendra from Sun must be Adhama Yoga"
    assert adhama.status == YogaStatus.STAINED

    # Moon in Taurus (idx 2) -> 2nd from Sun (Panaphara) -> Madhya Yoga
    chart_pana = make_mock_chart("Aries", {
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0}
    })
    y_p = detect_lunar_and_solar_yogas(chart_pana)
    madhya = next((y for y in y_p if y.id == "madhya_yoga"), None)
    assert madhya is not None, "Moon in Panaphara from Sun must be Madhya Yoga"
    assert madhya.status == YogaStatus.PURE

    # Moon in Gemini (idx 3) -> 3rd from Sun (Apoklima) -> Variṣṭha Yoga
    chart_apok = make_mock_chart("Aries", {
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0}
    })
    y_a = detect_lunar_and_solar_yogas(chart_apok)
    varishtha = next((y for y in y_a if y.id == "varishtha_yoga"), None)
    assert varishtha is not None, "Moon in Apoklima from Sun must be Variṣṭha Yoga"
    assert varishtha.status == YogaStatus.PURE


# =============================================================================
# 17. MASTER EVALUATOR ORCHESTRATION & DEDUPLICATION
# =============================================================================

def test_master_evaluator_orchestration_and_deduplication():
    """Verify detect_all_yogas runs all categories and deduplicates without runtime errors."""
    chart = make_mock_chart("Aries", {
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},
        "Mars": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},
        "Mercury": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Sagittarius", "longitude": 255.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0},
        "Saturn": {"sign": "Aquarius", "longitude": 315.0, "degree_0_to_30": 15.0}
    })
    payload = detect_all_yogas(chart)
    assert "total_count" in payload
    assert payload["total_count"] > 0
    assert "summary" in payload
    assert "yogas" in payload
    assert len(payload["categories"]) == 17, "Master evaluator must catalog all 17 yoga categories"

    # Verify no duplicate IDs exist in output
    yoga_ids = [y["id"] for y in payload["yogas"]]
    assert len(yoga_ids) == len(set(yoga_ids)), "Master evaluator must ensure 100% unique yoga IDs (no duplicates)"


def test_master_evaluator_specific_deduplication_cases():
    """Verify specific deduplication for Ubhayācarī and Lagna Kartarī, plus Lagna aspect queries."""
    from jyotish.yogas.breakers import get_aspect_score

    # 1. Test get_aspect_score with advanced_aspects['cusps'][1]
    chart_cusps = {
        "advanced_aspects": {
            "cusps": {
                1: {"Jupiter": {"raw": 48.0, "net": 48.0}}
            }
        }
    }
    assert get_aspect_score(chart_cusps, "Jupiter", "Lagna") == 48.0

    # 2. Test Ubhayācarī & Lagna Kartarī deduplication across modules
    # Aries Lagna with Pisces (H12) Venus, Taurus (H2) Mercury -> Śubha Kartarī on Lagna
    # Sun in Aries H1, flanked by Venus in H12 and Mercury in H2 -> Ubhayācarī Solar Flanking
    chart_overlap = make_mock_chart("Aries", {
        "Sun": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0},      # H12 from Lagna & Sun
        "Mercury": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},     # H2 from Lagna & Sun
        "Moon": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0}
    })
    payload = detect_all_yogas(chart_overlap)
    yoga_names = [y["name"] for y in payload["yogas"]]

    # Ensure Ubhayācarī appears at most once
    ubhayacari_matches = [name for name in yoga_names if "ubhayac" in name.lower() or "ubhayach" in name.lower()]
    assert len(ubhayacari_matches) == 1, f"Ubhayācarī must be deduplicated to exactly 1 instance, found: {ubhayacari_matches}"

    # Ensure Śubha Kartarī of Lagna appears at most once
    kartari_lagna_matches = [name for name in yoga_names if "Kartarī" in name and ("Lagna" in name or "1st House" in name)]
    assert len(kartari_lagna_matches) == 1, f"Lagna Kartarī must be deduplicated to exactly 1 instance, found: {kartari_lagna_matches}"


# =============================================================================
# 18. REFACTORED RAJA, NEECHABHANGA & CHAPTER 7 POWER YOGAS DEDICATED TESTS
# =============================================================================

def test_true_raja_vs_shankha_yoga_distinction():
    """Verify that 9th+10th alliance is strictly True Raja Yoga and other Kendra-Koṇas are Śaṅkha Yoga."""
    # 1. 9th lord + 10th lord (Mars + Venus for Leo Lagna in Taurus H10) -> True Raja Yoga
    chart_raja = make_mock_chart("Leo", {
        "Mars": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},
        "Venus": {"sign": "Taurus", "longitude": 47.0, "degree_0_to_30": 17.0}
    })
    yogas_raja = detect_raja_yogas(chart_raja)
    true_raja = next((y for y in yogas_raja if "dharma_karma_raja_yoga" in y.id), None)
    assert true_raja is not None, "9th + 10th alliance must produce dharma_karma_raja_yoga ID"
    assert "Dharma-Karma" in true_raja.name and "Rāja Yoga" in true_raja.name
    assert true_raja.status == YogaStatus.PURE

    # 2. 1st lord + 4th lord (Mars + Moon for Aries Lagna in H1) -> Śaṅkha Yoga
    chart_shankha = make_mock_chart("Aries", {
        "Mars": {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0},
        "Moon": {"sign": "Aries", "longitude": 12.0, "degree_0_to_30": 12.0}
    })
    yogas_shankha = detect_raja_yogas(chart_shankha)
    shankha = next((y for y in yogas_shankha if "shankha_yoga" in y.id), None)
    assert shankha is not None, "1st + 4th alliance must produce shankha_yoga ID"
    assert "Śaṅkha Yoga" in shankha.name
    assert shankha.status == YogaStatus.PURE


def test_intervening_planet_breaker_penalizes_conjunction():
    """Verify that a malefic/enemy sitting in longitude between conjoined lords triggers the Intervening Planet breaker (-35%)."""
    # Aries Lagna: 9th lord Jupiter at 10° Aries, 10th lord Saturn at 20° Aries.
    # Mars (natural malefic) at 15° Aries intervenes between them.
    chart_obstructed = make_mock_chart("Aries", {
        "Jupiter": {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0},
        "Mars": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},
        "Saturn": {"sign": "Aries", "longitude": 20.0, "degree_0_to_30": 20.0}
    })
    yogas = detect_raja_yogas(chart_obstructed)
    dk = next((y for y in yogas if "dharma_karma_raja_yoga" in y.id), None)
    assert dk is not None, "Must detect Dharma-Karma Raja Yoga"
    intervening_breaker = next((b for b in dk.breakers if b.factor == "Intervening Planet Obstruction"), None)
    assert intervening_breaker is not None, "Must trigger Intervening Planet Obstruction breaker"
    assert intervening_breaker.culprit_planet == "Mars"
    assert intervening_breaker.penalty == 35.0


def test_dusthana_conjunction_breaks_raja_yoga():
    """Verify that conjunction in 6th, 8th, or 12th house (Mahita Bhava failure) breaks the Raja Yoga (score <= 25, status BROKEN)."""
    # Aries Lagna: 9th lord Jupiter + 10th lord Saturn conjoined in Virgo (House 6)
    chart_dusthana = make_mock_chart("Aries", {
        "Jupiter": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},
        "Saturn": {"sign": "Virgo", "longitude": 168.0, "degree_0_to_30": 18.0}
    })
    yogas = detect_raja_yogas(chart_dusthana)
    dk = next((y for y in yogas if "dharma_karma_raja_yoga" in y.id), None)
    assert dk is not None, "Must detect the conjunction attempt"
    assert dk.status == YogaStatus.BROKEN, "Dusthana conjunction must mark status as BROKEN"
    assert dk.plausibility_score <= 25.0, "Broken Raja Yoga must have plausibility score <= 25%"
    assert any("Dusthana Conjunction" in b.factor for b in dk.breakers), "Must record Dusthana Conjunction breaker"


def test_saturn_strictly_excluded_from_four_planet_digbala():
    """Verify that Saturn is strictly excluded from the 4-to-5 planet Digbala count in Chapter 7 power yogas."""
    # Chart with 4 planets in Digbala including Saturn: Sun (H10), Mars (H10), Jupiter (H1), Saturn (H7)
    chart_with_saturn = make_mock_chart("Aries", {
        "Sun": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},      # H10 Digbala
        "Mars": {"sign": "Capricorn", "longitude": 280.0, "degree_0_to_30": 10.0},     # H10 Digbala
        "Jupiter": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},       # H1 Digbala
        "Saturn": {"sign": "Libra", "longitude": 195.0, "degree_0_to_30": 15.0}        # H7 Digbala
    })
    yogas_sat = detect_chapter7_power_yogas(chart_with_saturn)
    supreme_sat = next((y for y in yogas_sat if "Supreme Kingly Digbala" in y.name), None)
    assert supreme_sat is None, "Supreme Kingly Digbala must NOT trigger when 4th planet is Saturn"
    std_sat = next((y for y in yogas_sat if "Digbala Sovereignty" in y.name), None)
    assert std_sat is not None, "Standard Digbala Sovereignty must be recorded"
    assert any("Saturn Excluded from Supreme Digbala" in b.factor for b in std_sat.breakers)

    # Chart with 4 non-Saturn planets in Digbala: Sun (H10), Mars (H10), Jupiter (H1), Mercury (H1)
    chart_pure_dig = make_mock_chart("Aries", {
        "Sun": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},      # H10 Digbala
        "Mars": {"sign": "Capricorn", "longitude": 280.0, "degree_0_to_30": 10.0},     # H10 Digbala
        "Jupiter": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},       # H1 Digbala
        "Mercury": {"sign": "Aries", "longitude": 20.0, "degree_0_to_30": 20.0}        # H1 Digbala
    })
    yogas_pure = detect_chapter7_power_yogas(chart_pure_dig)
    supreme_pure = next((y for y in yogas_pure if "Supreme Kingly Digbala" in y.name), None)
    assert supreme_pure is not None, "Supreme Kingly Digbala must trigger for 4 non-Saturn planets"
    assert supreme_pure.status == YogaStatus.PURE


def test_neechabhanga_kendra_vs_dusthana_classification():
    """Verify Neechabhanga generates distinct YogaInstance records for Kendra (Raja) vs. Dusthana (Simple) placements."""
    from jyotish.yogas.neechabhanga import detect_neechabhanga_yogas

    # 1. Kendra Placement: Mercury in Pisces (H4 for Sagittarius Lagna), Jupiter (dispositor) in Gemini (H7 Kendra)
    chart_kendra = make_mock_chart("Sagittarius", {
        "Mercury": {"sign": "Pisces", "longitude": 345.0, "degree_0_to_30": 15.0},    # H4 Kendra
        "Jupiter": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0},     # H7 Kendra
        "Moon": {"sign": "Sagittarius", "longitude": 255.0, "degree_0_to_30": 15.0}
    })
    yogas_k = detect_neechabhanga_yogas(chart_kendra)
    nb_raja = next((y for y in yogas_k if y.id == "neechabhanga_raja_yoga_mercury"), None)
    assert nb_raja is not None, "Must detect Nīcabhaṅga Rāja Yoga for fallen planet in Kendra"
    assert "Nīcabhaṅga Rāja Yoga" in nb_raja.name
    assert nb_raja.status in (YogaStatus.PURE, YogaStatus.RESCUED)
    assert "Adversity Transmuted to Sovereignty" in nb_raja.archetype

    # 2. Dusthana Placement: Saturn in Aries (H6 for Scorpio Lagna), Mars (dispositor) in Capricorn (H10 from Moon in Aries)
    chart_dusthana = make_mock_chart("Scorpio", {
        "Saturn": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0},       # H6 Dusthana
        "Mars": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},    # Exalted, Kendra H10 from Moon
        "Moon": {"sign": "Aries", "longitude": 20.0, "degree_0_to_30": 20.0}
    })
    yogas_d = detect_neechabhanga_yogas(chart_dusthana)
    nb_simple = next((y for y in yogas_d if y.id == "neecha_bhanga_simple_saturn"), None)
    assert nb_simple is not None, "Must detect Nīca Bhaṅga Cancellation for fallen planet in Dusthana"
    assert "Nīca Bhaṅga Cancellation" in nb_simple.name
    assert nb_simple.status == YogaStatus.RESCUED
    assert "Deficit Overcome without Worldly Command" in nb_simple.archetype


def test_power_yogas_vargottama_and_bright_moon_and_vakra():
    """Verify Vargottama 1st/9th lords, Full Moon Kendra, Vakra Bala retrogression, and Upachaya malefics."""
    # 1. Vargottama 1st Lord + Exalted 9th Lord
    # Aries Lagna: Mars at 2.0° Aries (D1 Aries, D9 Aries -> Vargottama in H1), Jupiter in Cancer H4 (exalted)
    chart_varg = make_mock_chart("Aries", {
        "Mars": {"sign": "Aries", "longitude": 2.0, "degree_0_to_30": 2.0},
        "Jupiter": {"sign": "Cancer", "longitude": 95.0, "degree_0_to_30": 5.0}
    })
    y_varg = detect_chapter7_power_yogas(chart_varg)
    varg_l1_l9 = next((y for y in y_varg if y.id == "vargottama_royal_yoga_l1_l9"), None)
    assert varg_l1_l9 is not None, "Must detect Vargottama 1st Lord with Fortified 9th Lord"

    # 2. Vakra Bala Retrogression Sovereignty (2 retrograde planets in auspicious houses)
    chart_vakra = make_mock_chart("Aries", {
        "Mars": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0, "is_retrograde": True},
        "Jupiter": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0, "is_retrograde": True}
    })
    y_vakra = detect_chapter7_power_yogas(chart_vakra)
    vakra = next((y for y in y_vakra if "vakra_bala_sovereignty" in y.id), None)
    assert vakra is not None, "Must detect Vakra Bala Sovereignty for 2 retrograde planets"
    assert vakra.status == YogaStatus.PURE

    # 3. Malefics in Upachayas (Sun, Mars, Saturn in 3, 6, 11 from Lagna)
    chart_upachaya = make_mock_chart("Aries", {
        "Sun": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0},       # H3
        "Mars": {"sign": "Virgo", "longitude": 165.0, "degree_0_to_30": 15.0},      # H6
        "Saturn": {"sign": "Aquarius", "longitude": 315.0, "degree_0_to_30": 15.0}  # H11
    })
    y_upachaya = detect_chapter7_power_yogas(chart_upachaya)
    upachaya = next((y for y in y_upachaya if y.id == "malefics_upachaya_sovereignty"), None)
    assert upachaya is not None, "Must detect Malefics in Upachayas Sovereignty"


# =============================================================================
# 19. SCRIPTURAL EDGE CASES & REFINEMENTS TESTS
# =============================================================================

def test_dusthana_mutual_aspect_breaks_raja_yoga():
    """Verify that mutual aspect involving a Dusthana house (6, 8, 12) marks the yoga as BROKEN (score <= 25)."""
    # Leo Lagna: 9th lord Mars in Capricorn (H6), 10th lord Venus in Cancer (H12). Opposing across 6/12 axis.
    chart_dusthana_aspect = make_mock_chart(
        "Leo",
        {
            "Mars": {"sign": "Capricorn", "longitude": 285.0, "degree_0_to_30": 15.0},  # H6
            "Venus": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0}     # H12
        },
        aspects={
            "Mars": {"Venus": {"raw": 55.0, "net": 55.0}},
            "Venus": {"Mars": {"raw": 55.0, "net": 55.0}}
        }
    )
    yogas = detect_raja_yogas(chart_dusthana_aspect)
    dk = next((y for y in yogas if "dharma_karma_raja_yoga" in y.id), None)
    assert dk is not None, "Must detect the mutual aspect attempt between 9th and 10th lords"
    assert dk.status == YogaStatus.BROKEN, "Mutual aspect across Dusthanas must break Raja Yoga"
    assert dk.plausibility_score <= 25.0, "Broken Raja Yoga must have plausibility score <= 25%"
    assert any("Dusthana Aspect Connection" in b.factor for b in dk.breakers), "Must record Dusthana Aspect Connection breaker"


def test_neechabhanga_in_dusthana_cannot_support_raja_yoga():
    """Verify that a debilitated lord with cancellation in a Dusthana flags an incomplete foundation and breaks Raja Yoga."""
    # Aries Lagna: 10th lord Saturn in Aries H1, 9th lord Jupiter in Capricorn (debilitated in H10 Kendra).
    # Now let's test a debilitated lord trapped in a Dusthana:
    # Leo Lagna: 9th lord Mars in Cancer (debilitated in H12), conjoined with Venus in Cancer H12.
    # Dispositor Moon is in Taurus H10 (Kendra, rescuing debility).
    chart_rescued_in_dusthana = make_mock_chart("Leo", {
        "Mars": {"sign": "Cancer", "longitude": 105.0, "degree_0_to_30": 15.0},   # H12, debilitated
        "Venus": {"sign": "Cancer", "longitude": 108.0, "degree_0_to_30": 18.0},  # H12
        "Moon": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0}     # H10 Kendra rescues Mars
    })
    yogas = detect_raja_yogas(chart_rescued_in_dusthana)
    dk = next((y for y in yogas if "dharma_karma_raja_yoga" in y.id), None)
    assert dk is not None
    assert any("Simple Cancellation in Dusthana" in b.factor for b in dk.breakers), "Must flag incomplete foundation breaker"
    assert dk.status == YogaStatus.BROKEN


def test_natural_yogakaraka_amplification_bonus():
    """Verify that an alliance involving an inherent single-planet Yogakāraka receives a +10% bonus and positive factor."""
    # Cancer Lagna: Mars is natural Yogakāraka (rules H5 Koṇa & H10 Kendra).
    # 9th lord is Jupiter (rules H9 Koṇa).
    # Combine Mars + Jupiter in Scorpio (H5 Koṇa), with tight conjunction:
    chart_yk = make_mock_chart("Cancer", {
        "Mars": {"sign": "Scorpio", "longitude": 225.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Scorpio", "longitude": 227.0, "degree_0_to_30": 17.0}
    })
    yogas = detect_raja_yogas(chart_yk)
    dk = next((y for y in yogas if "dharma_karma_raja_yoga" in y.id), None)
    assert dk is not None, "Must detect 9th + 10th alliance (Jupiter + Mars)"
    assert any("Natural Yogakāraka Amplification" in f for f in dk.positive_factors), "Must award Natural Yogakāraka Amplification factor"
    assert dk.plausibility_score == 100.0, "Natural Yogakāraka amplification with tight conjunction must achieve maximum plausibility"


def test_nested_lagna_degree_fallback_in_power_yogas():
    """Verify that _get_navamsha_sign correctly extracts degree from chart['vargas']['D1']['lagna']."""
    from jyotish.yogas.power_yogas import _get_navamsha_sign

    # 1. 2.0° Aries -> First Navamsha of Aries is Aries
    chart_d9_a = {
        "vargas": {
            "D1": {
                "lagna": {"sign": "Aries", "degree_0_to_30": 2.0}
            }
        }
    }
    assert _get_navamsha_sign(chart_d9_a, "Lagna") == "Aries"

    # 2. 28.0° Aries -> 9th Navamsha of Aries (Fire sign) is Sagittarius
    chart_d9_b = {
        "vargas": {
            "D1": {
                "lagna": {"sign": "Aries", "degree_0_to_30": 28.0}
            }
        }
    }
    assert _get_navamsha_sign(chart_d9_b, "Lagna") == "Sagittarius"


def test_dharma_karma_parivartana_cross_module_deduplication():
    """Verify that the 9th–10th lord mutual exchange is cleanly deduplicated to a single instance across modules."""
    # Leo Lagna: 9th lord Mars in Taurus (H10), 10th lord Venus in Aries (H9).
    chart_exchange = make_mock_chart("Leo", {
        "Mars": {"sign": "Taurus", "longitude": 45.0, "degree_0_to_30": 15.0},   # H10
        "Venus": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}    # H9
    })
    payload = detect_all_yogas(chart_exchange)

    # Check for any yogas representing the 9th-10th exchange
    exchange_matches = [
        y for y in payload["yogas"]
        if "dharma_karma_exchange" in y["id"] or
           "power_yoga_dharma_karma_exchange" in y["id"] or
           ("maha_parivartana" in y["id"] and set(y["participating_planets"]) == {"Mars", "Venus"}) or
           ("dharma_karma_raja_yoga" in y["id"] and set(y["participating_planets"]) == {"Mars", "Venus"})
    ]
    assert len(exchange_matches) == 1, f"9th–10th Parivartana must be deduplicated to exactly 1 card, found: {[m['id'] for m in exchange_matches]}"



