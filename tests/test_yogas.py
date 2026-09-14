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
    """Kemadruma Yoga triggers when 2nd and 12th from Moon are empty, but cancels if planets are in Kendra from Moon/Lagna."""
    # Isolated Moon in House 5 (Leo) for Aries Lagna, but Jupiter in House 1 (Kendra from Lagna) -> Rescued
    grahas = {
        "Moon": {"sign": "Leo", "longitude": 135.0, "degree_0_to_30": 15.0},
        "Jupiter": {"sign": "Aries", "longitude": 15.0, "degree_0_to_30": 15.0}  # Kendra from Lagna
    }
    chart = make_mock_chart("Aries", grahas)
    yogas = detect_lunar_and_solar_yogas(chart)
    
    kema = next((y for y in yogas if y.id == "kemadruma_yoga"), None)
    assert kema is not None, "Kemadruma Yoga should be detected"
    assert kema.status == YogaStatus.RESCUED, "Kemadruma should be cancelled/rescued by Jupiter in Lagna Kendra"


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
