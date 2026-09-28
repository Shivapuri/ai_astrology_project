"""
tests/test_varga_environment.py
Unit tests for the 10-Varga (Daśavarga) Macro Environment & Thermodynamic Balance Engine.
"""

import pytest
from jyotish.report.varga_environment import (
    compute_varga_environment,
    compute_environmental_tally,
    DASAVARGA_ENVIRONMENTAL_WEIGHTS,
    TOTAL_DASAVARGA_WEIGHT,
    ELEMENT_MAP,
    GUNA_MAP,
    POLARITY_MAP
)


def test_dasavarga_weights_configuration():
    """
    Verify that the Daśavarga weights match Vic DiCara's model:
    - 10 charts total
    - D1 = 2.0
    - D60 = 3.33
    - D2, D3, D7, D9, D10, D12, D16, D30 = 1.0 each
    - Total sum = 13.33
    """
    expected_charts = {"D1", "D60", "D2", "D3", "D7", "D9", "D10", "D12", "D16", "D30"}
    assert set(DASAVARGA_ENVIRONMENTAL_WEIGHTS.keys()) == expected_charts
    assert len(DASAVARGA_ENVIRONMENTAL_WEIGHTS) == 10

    assert DASAVARGA_ENVIRONMENTAL_WEIGHTS["D1"] == 2.0
    assert DASAVARGA_ENVIRONMENTAL_WEIGHTS["D60"] == 3.33

    for v in ["D2", "D3", "D7", "D9", "D10", "D12", "D16", "D30"]:
        assert DASAVARGA_ENVIRONMENTAL_WEIGHTS[v] == 1.0

    calc_sum = round(sum(DASAVARGA_ENVIRONMENTAL_WEIGHTS.values()), 2)
    assert calc_sum == 13.33
    assert TOTAL_DASAVARGA_WEIGHT == 13.33


def test_varga_environment_prominence_scaling():
    """
    Verify that an entity's points in each varga are scaled by its Prominence Score:
    Contribution = Prominence * (W_v / 13.33).
    """
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries"},  # Fire (Lagna prom = 1.0)
            "grahas": {
                "Mars": {"sign": "Aries"},     # Fire (High prominence)
                "Venus": {"sign": "Taurus"},   # Earth (Baseline prominence)
                "Sun": {"sign": "Taurus"},
                "Moon": {"sign": "Taurus"},
                "Mercury": {"sign": "Taurus"},
                "Jupiter": {"sign": "Taurus"},
                "Saturn": {"sign": "Taurus"},
                "Rahu": {"sign": "Taurus"},
                "Ketu": {"sign": "Taurus"}
            }
        }
    }

    mock_prominence = {
        "Mars": 2.50,
        "Venus": 1.00,
        "Sun": 1.00,
        "Moon": 1.00,
        "Mercury": 1.00,
        "Jupiter": 1.00,
        "Saturn": 1.00,
        "Rahu": 1.00,
        "Ketu": 1.00
    }

    res = compute_varga_environment(mock_vargas, prominence_map=mock_prominence)
    elem = res["elements"]

    # When higher vargas are missing, they default to D1 sign.
    # Fire bodies: Lagna (prom 1.0) + Mars (prom 2.5) = 3.50 total points.
    # Earth bodies: 8 bodies * 1.0 prom = 8.00 total points.
    # Total points = 11.50
    assert elem["counts"]["Fire"] == 2
    assert elem["counts"]["Earth"] == 8
    assert elem["points"]["Fire"] == 3.50
    assert elem["points"]["Earth"] == 8.00


def test_lagna_boost_parameter():
    """
    Verify that the Lagna boost parameter scales Lagna's contribution.
    """
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Leo"},  # Fire
            "grahas": {p: {"sign": "Taurus"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
        }
    }

    # Default lagna_boost = 1.0 -> Lagna contributes 1.0
    res_default = compute_varga_environment(mock_vargas, lagna_boost=1.0)
    assert res_default["elements"]["points"]["Fire"] == 1.0

    # Boosted lagna_boost = 1.5 -> Lagna contributes 1.5
    res_boosted = compute_varga_environment(mock_vargas, lagna_boost=1.5)
    assert res_boosted["elements"]["points"]["Fire"] == 1.5


def test_d60_root_governance_weight():
    """
    Verify that D60 carries 3.33 weight (the heaviest single divisional chart),
    capable of shifting the thermodynamic balance even when physical D1 is different.
    """
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries"},  # Fire (Weight 2.0)
            "grahas": {p: {"sign": "Aries"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
        },
        "D60": {
            "lagna": {"sign": "Cancer"},  # Water (Weight 3.33)
            "grahas": {p: {"sign": "Cancer"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
        },
        # All other 8 vargas in Gemini (Air, 8.0 weight total)
        "D2": {"lagna": {"sign": "Gemini"}, "grahas": {p: {"sign": "Gemini"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}},
        "D3": {"lagna": {"sign": "Gemini"}, "grahas": {p: {"sign": "Gemini"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}},
        "D7": {"lagna": {"sign": "Gemini"}, "grahas": {p: {"sign": "Gemini"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}},
        "D9": {"lagna": {"sign": "Gemini"}, "grahas": {p: {"sign": "Gemini"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}},
        "D10": {"lagna": {"sign": "Gemini"}, "grahas": {p: {"sign": "Gemini"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}},
        "D12": {"lagna": {"sign": "Gemini"}, "grahas": {p: {"sign": "Gemini"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}},
        "D16": {"lagna": {"sign": "Gemini"}, "grahas": {p: {"sign": "Gemini"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}},
        "D30": {"lagna": {"sign": "Gemini"}, "grahas": {p: {"sign": "Gemini"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}}
    }

    res = compute_varga_environment(mock_vargas)
    elem = res["elements"]

    # 10 entities * 1.0 = 10.0 points total
    # D1 Fire: 10 * (2.0 / 13.33) = 1.50 pts
    # D60 Water: 10 * (3.33 / 13.33) = 2.50 pts (D60 alone exceeds D1!)
    # 8 Vargas Air: 10 * (8.0 / 13.33) = 6.00 pts
    assert elem["points"]["Fire"] == 1.50
    assert elem["points"]["Water"] == 2.50
    assert elem["points"]["Air"] == 6.00
    assert elem["dominant"] == "Air"
    assert elem["points"]["Water"] > elem["points"]["Fire"]


def test_deviation_thresholds_surplus_deficit_balanced():
    """
    Verify status classification:
    - Surplus: deviation > +2.0%
    - Deficit: deviation < -2.0%
    - Balanced: -2.0% <= deviation <= +2.0%
    """
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries"},  # Fire (Active)
            "grahas": {
                "Sun": {"sign": "Leo"},          # Fire (Active)
                "Moon": {"sign": "Sagittarius"}, # Fire (Active)
                "Mars": {"sign": "Taurus"},      # Earth (Passive)
                "Mercury": {"sign": "Virgo"},    # Earth (Passive)
                "Jupiter": {"sign": "Gemini"},   # Air (Active)
                "Venus": {"sign": "Libra"},      # Air (Active)
                "Saturn": {"sign": "Aquarius"},  # Air (Active)
                "Rahu": {"sign": "Cancer"},      # Water (Passive)
                "Ketu": {"sign": "Scorpio"}      # Water (Passive)
            }
        }
    }

    # 3 Fire (30%), 2 Earth (20%), 3 Air (30%), 2 Water (20%)
    res = compute_varga_environment(mock_vargas)
    elem = res["elements"]

    fire_meta = next(x for x in elem["breakdown"] if x["key"] == "Fire")
    earth_meta = next(x for x in elem["breakdown"] if x["key"] == "Earth")

    # Fire: 30.0% vs 25.0% baseline -> +5.0% deviation -> Surplus
    assert fire_meta["percentage"] == 30.0
    assert fire_meta["deviation_pct"] == 5.0
    assert fire_meta["status"] == "Surplus"

    # Earth: 20.0% vs 25.0% baseline -> -5.0% deviation -> Deficit
    assert earth_meta["percentage"] == 20.0
    assert earth_meta["deviation_pct"] == -5.0
    assert earth_meta["status"] == "Deficit"


def test_polarity_and_ayurvedic_doshas():
    """
    Verify that Polarities (Active/Passive) and Ayurvedic Doshas (Vata/Pitta/Kapha)
    are correctly tallied with their proper baseline percentages.
    """
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries"},       # Odd (Active), Fire (Pitta)
            "grahas": {
                "Sun": {"sign": "Gemini"},    # Odd (Active), Air (Vata)
                "Moon": {"sign": "Leo"},      # Odd (Active), Fire (Pitta)
                "Mars": {"sign": "Libra"},    # Odd (Active), Air (Vata)
                "Mercury": {"sign": "Aquarius"}, # Odd (Active), Air (Vata)
                "Jupiter": {"sign": "Sagittarius"}, # Odd (Active), Fire (Pitta)
                "Venus": {"sign": "Taurus"},  # Even (Passive), Earth (Kapha)
                "Saturn": {"sign": "Cancer"}, # Even (Passive), Water (Kapha)
                "Rahu": {"sign": "Virgo"},    # Even (Passive), Earth (Kapha)
                "Ketu": {"sign": "Pisces"}    # Even (Passive), Water (Kapha)
            }
        }
    }

    res = compute_varga_environment(mock_vargas)

    # Polarity: 6 Active (60.0%), 4 Passive (40.0%)
    pol = res["polarity"]
    assert pol["counts"]["Active"] == 6
    assert pol["counts"]["Passive"] == 4
    assert pol["dominant"] == "Active"

    active_meta = next(x for x in pol["breakdown"] if x["key"] == "Active")
    assert active_meta["percentage"] == 60.0
    assert active_meta["baseline_pct"] == 50.0
    assert active_meta["deviation_pct"] == 10.0
    assert active_meta["status"] == "Surplus"

    # Doshas: 3 Pitta (30.0%), 3 Vata (30.0%), 4 Kapha (40.0%)
    doshas = res["ayurvedic_doshas"]
    assert doshas["counts"]["Kapha"] == 4
    assert doshas["dominant"] == "Kapha"
    kapha_meta = next(x for x in doshas["breakdown"] if x["key"] == "Kapha")
    assert kapha_meta["percentage"] == 40.0
    assert kapha_meta["baseline_pct"] == 33.3
    assert kapha_meta["status"] == "Surplus"


def test_backward_compatibility_alias():
    """
    Verify that compute_environmental_tally returns the identical output as compute_varga_environment.
    """
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries"},
            "grahas": {p: {"sign": "Leo"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
        }
    }

    res1 = compute_varga_environment(mock_vargas)
    res2 = compute_environmental_tally(mock_vargas)

    assert res1 == res2
    assert "elements_breakdown" in res2
    assert "gunas_breakdown" in res2
    assert "polarity_breakdown" in res2
    assert "doshas_breakdown" in res2
    assert res2["total_varga_weight"] == 13.33
