"""
tests/test_baseline.py
Unit tests for refined Combustion (Astangata) and Conjunction (Yuti) mechanics
per Sūrya Siddhānta and Phaladīpikā.
"""

import pytest
from jyotish.baseline import ChartBaseline
from jyotish.aspects.aspects import calculate_advanced_graha_aspects
from jyotish.baseline_tables import (
    CONJUNCTION_MAX_ORB,
    CROSS_BORDER_ATTENUATION,
    COMBUSTION_ORBS,
    COMBUSTION_ORBS_RETROGRADE
)


class MockBaseline:
    """Mock container providing coordinates and shortest_distance_matrix for ChartBaseline properties."""
    def __init__(self, coordinates, shortest_distance_matrix):
        self.coordinates = coordinates
        self.shortest_distance_matrix = shortest_distance_matrix

    @property
    def combustion_status(self):
        return ChartBaseline.combustion_status.func(self)

    @property
    def conjunctions(self):
        return ChartBaseline.conjunctions.func(self)


def test_retrograde_venus_combustion_orb():
    """
    Test retrograde Venus:
    Surya Siddhanta orb contracts from 10.0° (direct) to 8.0° (retrograde).
    At 9.0° separation:
    - Direct Venus is combust (9.0° <= 10.0°).
    - Retrograde Venus is NOT combust (9.0° > 8.0°).
    At 6.0° separation:
    - Retrograde Venus is combust (6.0° <= 8.0°).
    """
    coords_direct = {
        "Sun": {"sign_index": 0, "sign": "Aries"},
        "Venus": {"sign_index": 0, "sign": "Aries", "is_retrograde": False},
        "Moon": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Mars": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Mercury": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Jupiter": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Saturn": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
    }
    dist_direct = {"Sun": {"Venus": 9.0, "Moon": 50.0, "Mars": 50.0, "Mercury": 50.0, "Jupiter": 50.0, "Saturn": 50.0}}

    mock_direct = MockBaseline(coords_direct, dist_direct)
    status_direct = mock_direct.combustion_status["Venus"]
    assert status_direct["orb_limit"] == 10.0
    assert status_direct["combustion_orb"] == 10.0
    assert status_direct["is_combust"] is True
    assert status_direct["combustion_ratio"] == 0.1

    # Retrograde Venus at 9.0° separation
    coords_retro = {
        "Sun": {"sign_index": 0, "sign": "Aries"},
        "Venus": {"sign_index": 0, "sign": "Aries", "is_retrograde": True},
        "Moon": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Mars": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Mercury": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Jupiter": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Saturn": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
    }
    mock_retro = MockBaseline(coords_retro, dist_direct)
    status_retro = mock_retro.combustion_status["Venus"]
    assert status_retro["orb_limit"] == 8.0
    assert status_retro["combustion_orb"] == 8.0
    assert status_retro["is_combust"] is False
    assert status_retro["combustion_ratio"] == 0.0

    # Retrograde Venus at 6.0° separation
    dist_retro_combust = {"Sun": {"Venus": 6.0, "Moon": 50.0, "Mars": 50.0, "Mercury": 50.0, "Jupiter": 50.0, "Saturn": 50.0}}
    mock_retro_combust = MockBaseline(coords_retro, dist_retro_combust)
    status_retro_combust = mock_retro_combust.combustion_status["Venus"]
    assert status_retro_combust["is_combust"] is True
    assert status_retro_combust["orb_limit"] == 8.0
    assert status_retro_combust["combustion_ratio"] == 0.25  # 1.0 - (6.0 / 8.0)
    assert status_retro_combust["potency_loss_pct"] == 25.0
    assert status_retro_combust["sun_absorption_factor"] == 0.25


def test_retrograde_mercury_combustion_orb():
    """
    Test retrograde Mercury:
    Surya Siddhanta orb contracts from 14.0° (direct) to 12.0° (retrograde).
    At 13.0° separation:
    - Direct Mercury is combust (13.0° <= 14.0°).
    - Retrograde Mercury is NOT combust (13.0° > 12.0°).
    At 6.0° separation:
    - Retrograde Mercury is combust (6.0° <= 12.0°).
    """
    coords_direct = {
        "Sun": {"sign_index": 0, "sign": "Aries"},
        "Mercury": {"sign_index": 0, "sign": "Aries", "is_retrograde": False},
        "Moon": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Mars": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Jupiter": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Venus": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Saturn": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
    }
    dist_13 = {"Sun": {"Mercury": 13.0, "Moon": 50.0, "Mars": 50.0, "Jupiter": 50.0, "Venus": 50.0, "Saturn": 50.0}}

    mock_direct = MockBaseline(coords_direct, dist_13)
    status_direct = mock_direct.combustion_status["Mercury"]
    assert status_direct["orb_limit"] == 14.0
    assert status_direct["is_combust"] is True
    assert status_direct["combustion_ratio"] == round(1.0 - (13.0 / 14.0), 4)

    # Retrograde Mercury at 13.0° separation
    coords_retro = {
        "Sun": {"sign_index": 0, "sign": "Aries"},
        "Mercury": {"sign_index": 0, "sign": "Aries", "is_retrograde": True},
        "Moon": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Mars": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Jupiter": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Venus": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Saturn": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
    }
    mock_retro = MockBaseline(coords_retro, dist_13)
    status_retro = mock_retro.combustion_status["Mercury"]
    assert status_retro["orb_limit"] == 12.0
    assert status_retro["is_combust"] is False
    assert status_retro["combustion_ratio"] == 0.0

    # Retrograde Mercury at 6.0° separation
    dist_6 = {"Sun": {"Mercury": 6.0, "Moon": 50.0, "Mars": 50.0, "Jupiter": 50.0, "Venus": 50.0, "Saturn": 50.0}}
    mock_retro_combust = MockBaseline(coords_retro, dist_6)
    status_retro_combust = mock_retro_combust.combustion_status["Mercury"]
    assert status_retro_combust["is_combust"] is True
    assert status_retro_combust["orb_limit"] == 12.0
    assert status_retro_combust["combustion_ratio"] == 0.5  # 1.0 - (6.0 / 12.0)
    assert status_retro_combust["potency_loss_pct"] == 50.0
    assert status_retro_combust["sun_absorption_factor"] == 0.5


def test_cross_border_combustion():
    """
    Test cross-border combustion:
    Sun at 29° Aries (sign_index 0), Mars at 1° Taurus (sign_index 1).
    Separation = 2.0° <= Mars orb limit 17.0°.
    Must verify:
    - is_combust == True
    - same_sign == False
    - cross_border == True
    - severity == 'Deep (< 3°)'
    """
    coords = {
        "Sun": {"sign_index": 0, "sign": "Aries"},
        "Mars": {"sign_index": 1, "sign": "Taurus", "is_retrograde": False},
        "Moon": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
        "Mercury": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
        "Jupiter": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
        "Venus": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
        "Saturn": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
    }
    dist = {"Sun": {"Mars": 2.0, "Moon": 90.0, "Mercury": 90.0, "Jupiter": 90.0, "Venus": 90.0, "Saturn": 90.0}}

    mock = MockBaseline(coords, dist)
    mars_status = mock.combustion_status["Mars"]

    assert mars_status["is_combust"] is True
    assert mars_status["same_sign"] is False
    assert mars_status["cross_border"] is True
    assert mars_status["separation"] == 2.0
    assert mars_status["sun_distance"] == 2.0
    assert mars_status["orb_limit"] == 17.0
    assert mars_status["severity"] == "Deep (< 3°)"
    expected_ratio = round(1.0 - (2.0 / 17.0), 4)
    assert mars_status["combustion_ratio"] == expected_ratio
    assert mars_status["potency_loss_pct"] == round(expected_ratio * 100.0, 2)
    assert mars_status["sun_absorption_factor"] == expected_ratio


def test_continuous_combustion_ratio_cazimi_and_half_orb():
    """
    Test continuous combustion_ratio gradient:
    - Exact Cazimi separation 0.0° yields 1.0 (100% absorption, 100% potency loss).
    - Separation at half orb limit yields ~0.5 (50% absorption, 50% potency loss).
    - Separation at full orb limit yields 0.0 (marginal boundary).
    - Separation beyond orb limit yields 0.0.
    """
    coords = {
        "Sun": {"sign_index": 3, "sign": "Cancer"},
        "Jupiter": {"sign_index": 3, "sign": "Cancer", "is_retrograde": False},
        "Moon": {"sign_index": 3, "sign": "Cancer", "is_retrograde": False},
        "Mars": {"sign_index": 3, "sign": "Cancer", "is_retrograde": False},
        "Mercury": {"sign_index": 3, "sign": "Cancer", "is_retrograde": False},
        "Venus": {"sign_index": 3, "sign": "Cancer", "is_retrograde": False},
        "Saturn": {"sign_index": 3, "sign": "Cancer", "is_retrograde": False},
    }

    # Cazimi (0.0° separation) for Jupiter (orb 11.0°)
    dist_cazimi = {"Sun": {"Jupiter": 0.0, "Moon": 50.0, "Mars": 50.0, "Mercury": 50.0, "Venus": 50.0, "Saturn": 50.0}}
    mock_cazimi = MockBaseline(coords, dist_cazimi)
    jup_cazimi = mock_cazimi.combustion_status["Jupiter"]
    assert jup_cazimi["is_combust"] is True
    assert jup_cazimi["combustion_ratio"] == 1.0
    assert jup_cazimi["potency_loss_pct"] == 100.0
    assert jup_cazimi["sun_absorption_factor"] == 1.0
    assert jup_cazimi["severity"] == "Deep (< 3°)"
    assert jup_cazimi["same_sign"] is True
    assert jup_cazimi["cross_border"] is False

    # Half orb limit (5.5° separation for Jupiter)
    dist_half = {"Sun": {"Jupiter": 5.5, "Moon": 50.0, "Mars": 50.0, "Mercury": 50.0, "Venus": 50.0, "Saturn": 50.0}}
    mock_half = MockBaseline(coords, dist_half)
    jup_half = mock_half.combustion_status["Jupiter"]
    assert jup_half["is_combust"] is True
    assert jup_half["combustion_ratio"] == 0.5
    assert jup_half["potency_loss_pct"] == 50.0
    assert jup_half["sun_absorption_factor"] == 0.5
    assert jup_half["severity"] == "Moderate"

    # Full orb boundary (11.0° separation)
    dist_orb = {"Sun": {"Jupiter": 11.0, "Moon": 50.0, "Mars": 50.0, "Mercury": 50.0, "Venus": 50.0, "Saturn": 50.0}}
    mock_orb = MockBaseline(coords, dist_orb)
    jup_orb = mock_orb.combustion_status["Jupiter"]
    assert jup_orb["is_combust"] is True
    assert jup_orb["combustion_ratio"] == 0.0
    assert jup_orb["potency_loss_pct"] == 0.0

    # Beyond orb limit (11.5° separation)
    dist_beyond = {"Sun": {"Jupiter": 11.5, "Moon": 50.0, "Mars": 50.0, "Mercury": 50.0, "Venus": 50.0, "Saturn": 50.0}}
    mock_beyond = MockBaseline(coords, dist_beyond)
    jup_beyond = mock_beyond.combustion_status["Jupiter"]
    assert jup_beyond["is_combust"] is False
    assert jup_beyond["combustion_ratio"] == 0.0
    assert jup_beyond["potency_loss_pct"] == 0.0
    assert jup_beyond["severity"] == "None"


def test_non_combust_bodies_default_values():
    """
    Verifies default telemetry for non-combust bodies (Sun, Rahu, Ketu):
    combustion_ratio: 0.0, potency_loss_pct: 0.0, sun_absorption_factor: 0.0,
    same_sign: False, cross_border: False, is_combust: False.
    """
    coords = {
        "Sun": {"sign_index": 0, "sign": "Aries"},
        "Moon": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
        "Mars": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
        "Mercury": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
        "Jupiter": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
        "Venus": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
        "Saturn": {"sign_index": 5, "sign": "Virgo", "is_retrograde": False},
    }
    dist = {"Sun": {"Moon": 90.0, "Mars": 90.0, "Mercury": 90.0, "Jupiter": 90.0, "Venus": 90.0, "Saturn": 90.0}}
    mock = MockBaseline(coords, dist)
    status = mock.combustion_status

    for body in ["Sun", "Rahu", "Ketu"]:
        b_data = status[body]
        assert b_data["is_combust"] is False
        assert b_data["combustion_ratio"] == 0.0
        assert b_data["potency_loss_pct"] == 0.0
        assert b_data["sun_absorption_factor"] == 0.0
        assert b_data["same_sign"] is False
        assert b_data["cross_border"] is False
        assert b_data["severity"] == "None"


def test_calculate_advanced_graha_aspects_yuti_dict_mode():
    """
    Tests calculate_advanced_graha_aspects:
    - Backwards-compatible string list returned by default.
    - Dictionary format returned when requested (yuti_format='dict' or as_dict=True).
    - Cross-border conjunction detected within 10.0° orb across sign borders.
    """
    planets_data = {
        "Sun": {"longitude": 29.0, "sign": "Aries"},
        "Mars": {"longitude": 31.0, "sign": "Taurus"},
        "Jupiter": {"longitude": 125.0, "sign": "Leo"},
        "Rahu": {"longitude": 128.0, "sign": "Leo"},
        "Lagna": {"longitude": 122.0, "sign": "Leo"},
        "MC": {"longitude": 129.0, "sign": "Leo"},
        "Saturn": {"longitude": 215.0, "sign": "Scorpio"},
    }

    # 1. Default list format
    res_list = calculate_advanced_graha_aspects(planets_data, {})
    assert isinstance(res_list["yutis"]["Sun"], list)
    # Cross-border conjunction: Mars is at 31° (2° away from Sun at 29°)
    assert "Mars" in res_list["yutis"]["Sun"]
    assert "Sun" in res_list["yutis"]["Mars"]
    # Same sign conjunction in Leo
    assert "Rahu" in res_list["yutis"]["Jupiter"]
    assert "Jupiter" in res_list["yutis"]["Rahu"]
    # Sensitive points excluded from conjoined lists
    assert "Lagna" not in res_list["yutis"]["Jupiter"]
    assert "MC" not in res_list["yutis"]["Jupiter"]

    # yuti_details always provides structured breakdown
    sun_mars_detail = res_list["yuti_details"]["Sun"]["Mars"]
    assert sun_mars_detail["same_sign"] is False
    assert sun_mars_detail["cross_border"] is True
    assert sun_mars_detail["boundary_factor"] == 0.75
    assert sun_mars_detail["separation"] == 2.0
    assert sun_mars_detail["orb_band"] == "Exact (Intimate)"
    assert sun_mars_detail["effective_potency"] == 0.6  # (1 - 2/10) * 0.75 = 0.8 * 0.75 = 0.6

    # 2. Dictionary format when requested
    res_dict = calculate_advanced_graha_aspects(planets_data, {}, as_dict=True)
    assert isinstance(res_dict["yutis"]["Sun"], dict)
    assert "Mars" in res_dict["yutis"]["Sun"]
    assert res_dict["yutis"]["Sun"]["Mars"]["cross_border"] is True
    assert res_dict["yutis"]["Sun"]["Mars"]["effective_potency"] == 0.6


def test_same_sign_wide_conjunction_vs_tight_orb():
    """
    Tests semantic distinction between tight orb conjunction (<= 10.0°)
    and wide same-sign co-presence (> 10.0°):
    - Venus at 2.0° Aries, Jupiter at 17.0° Aries (separation 15.0°).
    - same_sign is True, forming a classical whole-sign Rāśi Yuti bond.
    - separation > CONJUNCTION_MAX_ORB (10.0°), so effective_potency is 0.0 and is_orb_conjunction is False.
    """
    planets_data = {
        "Venus": {"longitude": 2.0, "sign": "Aries"},
        "Jupiter": {"longitude": 17.0, "sign": "Aries"},
        "Sun": {"longitude": 100.0, "sign": "Cancer"},
    }
    res = calculate_advanced_graha_aspects(planets_data, {})
    # Venus and Jupiter are in the same sign (Rāśi Yuti)
    assert "Jupiter" in res["yutis"]["Venus"]
    assert "Venus" in res["yutis"]["Jupiter"]

    detail = res["yuti_details"]["Venus"]["Jupiter"]
    assert detail["same_sign"] is True
    assert detail["separation"] == 15.0
    assert detail["is_orb_conjunction"] is False
    assert detail["effective_potency"] == 0.0
    assert detail["orb_band"] == "Wide"

