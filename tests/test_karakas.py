"""
Unit and regression tests for jyotish.karakas module.
Verifies Chara Karakas, Functional Rulerships, and Yogakarakas against BPHS and Kala baselines.
"""

import pytest
from jyotish import karakas


def test_classical_yogakarakas_for_all_lagnas():
    """
    Verifies that ONLY the 6 classical Lagnas produce a single Yogakaraka (Kendra + Trikona),
    and that the planet identified matches BPHS Chapter 34 and PVR Narasimha Rao Table 30.
    """
    expected_yogakarakas = {
        "Aries": None,
        "Taurus": "Saturn",      # Rules 9 (Trikona) & 10 (Kendra)
        "Gemini": None,
        "Cancer": "Mars",        # Rules 5 (Trikona) & 10 (Kendra)
        "Leo": "Mars",           # Rules 4 (Kendra) & 9 (Trikona)
        "Virgo": None,
        "Libra": "Saturn",       # Rules 4 (Kendra) & 5 (Trikona)
        "Scorpio": None,
        "Sagittarius": None,
        "Capricorn": "Venus",    # Rules 5 (Trikona) & 10 (Kendra)
        "Aquarius": "Venus",     # Rules 4 (Kendra) & 9 (Trikona)
        "Pisces": None
    }
    
    for lagna, expected_yk in expected_yogakarakas.items():
        roles = karakas.calculate_functional_roles(lagna)
        found_yks = [p for p, data in roles.items() if data["is_yogakaraka"]]
        
        if expected_yk is None:
            assert len(found_yks) == 0, f"Expected no single Yogakaraka for {lagna}, found {found_yks}"
        else:
            assert found_yks == [expected_yk], f"For {lagna}, expected Yogakaraka {expected_yk}, got {found_yks}"
            # Verify ruled houses
            yk_data = roles[expected_yk]
            ruled = yk_data["ruled_houses"]
            assert any(h in [4, 7, 10] for h in ruled), f"{expected_yk} for {lagna} must rule a Kendra (4, 7, 10)"
            assert any(h in [5, 9] for h in ruled), f"{expected_yk} for {lagna} must rule a Trikona (5, 9)"


def test_badhaka_house_determination():
    """
    Verifies Badhaka house: Movable -> 11, Fixed -> 9, Dual -> 7.
    """
    # Movable (Aries) -> Badhaka house is 11 (Aquarius ruled by Saturn)
    roles_ar = karakas.calculate_functional_roles("Aries")
    assert roles_ar["Saturn"]["is_badhaka"] is True
    
    # Fixed (Taurus) -> Badhaka house is 9 (Capricorn ruled by Saturn)
    roles_ta = karakas.calculate_functional_roles("Taurus")
    assert roles_ta["Saturn"]["is_badhaka"] is True
    
    # Dual (Gemini) -> Badhaka house is 7 (Sagittarius ruled by Jupiter)
    roles_ge = karakas.calculate_functional_roles("Gemini")
    assert roles_ge["Jupiter"]["is_badhaka"] is True


def test_maraka_house_determination():
    """
    Verifies Maraka lords (Houses 2 and 7).
    """
    # For Cancer Lagna:
    # H2 is Leo (Sun), H7 is Capricorn (Saturn)
    roles_cn = karakas.calculate_functional_roles("Cancer")
    assert roles_cn["Sun"]["is_maraka"] is True
    assert roles_cn["Saturn"]["is_maraka"] is True
    assert roles_cn["Mars"]["is_maraka"] is False


def test_angelina_jolie_chara_karakas():
    """
    Verifies Chara Karakas against Kala's ground-truth printout for Angelina Jolie:
    AK: Venus (28°09')
    AmK: Mercury (22°19')
    BK: Jupiter (17°25')
    MK: Saturn (17°23')
    PK: Sun (13°25')
    GK: Moon (13°05')
    DK: Mars (10°42')
    """
    mock_d1_grahas = {
        "Sun": {"degree_0_to_30": 13.4167},       # 13°25'
        "Moon": {"degree_0_to_30": 13.0833},      # 13°05'
        "Mars": {"degree_0_to_30": 10.7000},      # 10°42'
        "Mercury": {"degree_0_to_30": 22.3167},   # 22°19'
        "Jupiter": {"degree_0_to_30": 17.4167},   # 17°25'
        "Venus": {"degree_0_to_30": 28.1500},     # 28°09'
        "Saturn": {"degree_0_to_30": 17.3833},    # 17°23'
        "Rahu": {"degree_0_to_30": 0.8833},       # 00°53'
        "Ketu": {"degree_0_to_30": 0.8833}        # 00°53'
    }
    
    ck = karakas.calculate_chara_karakas(mock_d1_grahas)
    
    assert ck["Venus"]["karaka"] == "AK"
    assert ck["Mercury"]["karaka"] == "AmK"
    assert ck["Jupiter"]["karaka"] == "BK"
    assert ck["Saturn"]["karaka"] == "MK"
    assert ck["Sun"]["karaka"] == "PK"
    assert ck["Moon"]["karaka"] == "GK"
    assert ck["Mars"]["karaka"] == "DK"
    
    assert ck["Rahu"]["karaka"] == "—"
    assert ck["Ketu"]["karaka"] == "—"
