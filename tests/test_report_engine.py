"""
Tests for Astra Astrological Synthesis Report Engine
Validates:
- All 27 Nakshatras complete lore and classification database
- 4-step Nakshatra scoring system (Moon 8pts, Lagna 4pts, Sun 2pts, others 1pt, aspect refinement)
- Polarity Core (Ascendant ⟷ Moon) and Panchadha Maitri friction scoring
- Operational Axis & Vargottama detection
- End-to-end integration with generate_kala_chart
"""

import pytest
from jyotish.nakshatras.lore import (
    NAKSHATRA_DATABASE,
    get_nakshatra_lore,
    get_nakshatra_group,
    ALL_NAKSHATRA_GROUPS
)
from jyotish.report.report_engine import (
    compute_nakshatra_dominance,
    compute_polarity_core,
    compute_operational_axis,
    compute_environmental_tally,
    compute_planetary_prominence_rankings,
    generate_report_payload
)
from jyotish.generate_jyotish import generate_kala_chart


def test_all_27_nakshatras_database_completeness():
    """Verify that all 27 nakshatras have full psychological lore and valid groups."""
    assert len(NAKSHATRA_DATABASE) == 27
    expected_fields = [
        "name", "group", "group_description", "astronomical_star",
        "zodiacal_span", "presiding_deity", "symbol_etymology",
        "varahamihira_moon", "core_psychology", "real_world_manifestations"
    ]

    for name, data in NAKSHATRA_DATABASE.items():
        for field in expected_fields:
            assert field in data, f"Missing {field} in Nakshatra {name}"
            assert len(str(data[field])) > 3, f"Empty {field} in Nakshatra {name}"
        assert data["group"] in ALL_NAKSHATRA_GROUPS, f"Invalid group in {name}: {data['group']}"

    # Specific anchor spot checks
    assert NAKSHATRA_DATABASE["Ardra"]["group"] == "Tikshna"
    assert "Betelgeuse" in NAKSHATRA_DATABASE["Ardra"]["astronomical_star"]
    assert NAKSHATRA_DATABASE["Rohini"]["group"] == "Dhruva"
    assert "Aldebaran" in NAKSHATRA_DATABASE["Rohini"]["astronomical_star"]
    assert NAKSHATRA_DATABASE["Mrigashira"]["group"] == "Mridu"
    assert NAKSHATRA_DATABASE["Pushya"]["group"] == "Laghu"
    assert NAKSHATRA_DATABASE["Swati"]["group"] == "Chara"
    assert NAKSHATRA_DATABASE["Krittika"]["group"] == "Mishra"


def test_nakshatra_alias_resolution():
    """Verify alias normalization for common variant spellings."""
    assert get_nakshatra_lore("Ashvini")["name"] == "Ashwini"
    assert get_nakshatra_lore("Mrigashirsha")["name"] == "Mrigashira"
    assert get_nakshatra_lore("Purvashadha")["name"] == "Purva Ashadha"
    assert get_nakshatra_lore("Shatataraka")["name"] == "Shatabhisha"


def test_nakshatra_4_step_scoring():
    """Verify canonical point weights: Moon=8, Lagna=4, Sun=2, others=1."""
    mock_nakshatras = {
        "Lagna": {"nakshatra": "Ardra", "pada": 1, "nakshatra_lord": "Rahu", "sub_lord": "Jupiter"},
        "Moon": {"nakshatra": "Rohini", "pada": 2, "nakshatra_lord": "Moon", "sub_lord": "Saturn"},
        "Sun": {"nakshatra": "Bharani", "pada": 3, "nakshatra_lord": "Venus", "sub_lord": "Sun"},
        "Mars": {"nakshatra": "Bharani", "pada": 4, "nakshatra_lord": "Venus", "sub_lord": "Mars"},
        "Mercury": {"nakshatra": "Mrigashira", "pada": 1, "nakshatra_lord": "Mars", "sub_lord": "Mercury"},
        "Jupiter": {"nakshatra": "Pushya", "pada": 2, "nakshatra_lord": "Saturn", "sub_lord": "Jupiter"},
        "Venus": {"nakshatra": "Ashlesha", "pada": 3, "nakshatra_lord": "Mercury", "sub_lord": "Venus"},
        "Saturn": {"nakshatra": "Swati", "pada": 4, "nakshatra_lord": "Rahu", "sub_lord": "Saturn"},
        "Rahu": {"nakshatra": "Ardra", "pada": 2, "nakshatra_lord": "Rahu", "sub_lord": "Ketu"},
        "Ketu": {"nakshatra": "Mula", "pada": 4, "nakshatra_lord": "Ketu", "sub_lord": "Venus"}
    }

    # Bharani has Sun (2) + Mars (1) = 3 base points
    # Ardra has Lagna (4) + Rahu (1) = 5 base points
    # Rohini has Moon (8) = 8 base points
    res = compute_nakshatra_dominance({}, mock_nakshatras, None)

    leaderboard = {item["nakshatra"]: item for item in res["leaderboard"]}
    assert leaderboard["Rohini"]["base_points"] == 8.0
    assert leaderboard["Ardra"]["base_points"] == 5.0
    assert leaderboard["Bharani"]["base_points"] == 3.0
    assert leaderboard["Mrigashira"]["base_points"] == 1.0

    # Rohini should be rank 1
    assert res["dominant_nakshatra"]["nakshatra"] == "Rohini"

    # Percentages sum to approx 100%
    tot_pct = sum(item["dominance_pct"] for item in res["leaderboard"])
    assert 99.0 <= tot_pct <= 101.0


def test_polarity_core_friendship_and_tattvas():
    """Verify Polarity Core evaluates friendship and elemental friction."""
    # Test chart with Fire Lagna and Water Moon (High friction)
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries"},
            "grahas": {
                "Sun": {"sign": "Aries"},
                "Moon": {"sign": "Cancer"},
                "Mars": {"sign": "Aries"},
                "Mercury": {"sign": "Pisces"},
                "Jupiter": {"sign": "Cancer"},
                "Venus": {"sign": "Taurus"},
                "Saturn": {"sign": "Aquarius"},
                "Rahu": {"sign": "Gemini"},
                "Ketu": {"sign": "Sagittarius"}
            }
        }
    }
    mock_nakshatras = {
        "Lagna": {"nakshatra": "Ashwini", "nakshatra_lord": "Ketu", "pada": 1},
        "Moon": {"nakshatra": "Ashlesha", "nakshatra_lord": "Mercury", "pada": 4}
    }

    polarity = compute_polarity_core(mock_vargas, mock_nakshatras)
    rel_info = polarity["relationship"]

    assert polarity["ascendant_nakshatra"]["element"] == "Fire"
    assert polarity["moon_nakshatra"]["element"] == "Water"
    assert rel_info["tattva_harmonic"] is False
    assert "Severe Clashing" in rel_info["tattva_status"]
    assert rel_info["friction_score"] >= 50


def test_vargottama_lagna_detection():
    """Verify Vargottama Lagna check flags matching signs in D1 and D9."""
    vargas_vargottama = {
        "D1": {"lagna": {"sign": "Leo"}, "grahas": {}},
        "D9": {"lagna": {"sign": "Leo"}, "grahas": {}}
    }
    axis = compute_operational_axis(vargas_vargottama)
    assert axis["is_vargottama"] is True
    assert axis["vargottama_boost"] is not None

    vargas_non_varg = {
        "D1": {"lagna": {"sign": "Leo"}, "grahas": {}},
        "D9": {"lagna": {"sign": "Virgo"}, "grahas": {}}
    }
    axis_non = compute_operational_axis(vargas_non_varg)
    assert axis_non["is_vargottama"] is False
    assert axis_non["vargottama_boost"] is None


def test_generate_kala_chart_report_payload_integration():
    """Verify that full generate_kala_chart integration returns 'report' seamlessly."""
    chart = generate_kala_chart(
        name="Test Native",
        year=1980,
        month=8,
        day=15,
        hour=10,
        minute=30,
        latitude=13.0827,
        longitude=80.2707,
        timezone_offset=5.5
    )

    assert "report" in chart
    rep = chart["report"]
    assert "polarity_core" in rep
    assert "nakshatra_dominance" in rep
    assert "operational_axis" in rep
    assert "environmental_tally" in rep
    assert "planetary_rankings" in rep
    assert "synthesis_ingredients" in rep

    assert rep["polarity_core"]["ascendant_nakshatra"]["name"]
    assert rep["polarity_core"]["moon_nakshatra"]["name"]
    assert rep["nakshatra_dominance"]["dominant_nakshatra"]
    assert len(rep["nakshatra_dominance"]["temperament_breakdown"]) == 7
    assert rep["planetary_rankings"]["chart_commander"]


def test_nakshatra_prominence_scaled_scoring():
    """Verify that Prominence scaling weights occupancy and aspect rays dynamically."""
    mock_nakshatras = {
        "Lagna": {"nakshatra": "Bharani", "pada": 1},
        "Moon": {"nakshatra": "Rohini", "pada": 2},
        "Sun": {"nakshatra": "Pushya", "pada": 3},
        "Mars": {"nakshatra": "Bharani", "pada": 4},
        "Saturn": {"nakshatra": "Swati", "pada": 1}
    }

    # Custom prominence map:
    # Mars is #1 Commander (2.30), Saturn is weak (0.65), Moon is strong (1.25), Sun is 1.50
    mock_prominence = {
        "Moon": 1.25,
        "Sun": 1.50,
        "Mars": 2.30,
        "Saturn": 0.65
    }

    # Aspects passed to compute_nakshatra_dominance are ignored (backwards-compatibility)
    mock_aspects = {
        "planets": {
            "Mars": {"Moon": {"raw": 30.0}, "Sun": {"raw": 0.0}}
        },
        "cusps": {}
    }

    res = compute_nakshatra_dominance({}, mock_nakshatras, mock_aspects, prominence_map=mock_prominence)
    leaderboard = {item["nakshatra"]: item for item in res["leaderboard"]}

    # Rohini (Moon): Base = 8.0 * 1.25 = 10.0
    assert leaderboard["Rohini"]["base_points"] == 10.0
    assert leaderboard["Rohini"]["total_points"] == 10.0

    # Bharani: Lagna (4.0 * 1.0 = 4.0) + Mars (1.0 * 2.30 = 2.30) = 6.30 points
    assert leaderboard["Bharani"]["base_points"] == 6.30
    assert leaderboard["Bharani"]["total_points"] == 6.30

    # Pushya (Sun): Base = 2.0 * 1.50 = 3.0
    assert leaderboard["Pushya"]["base_points"] == 3.0
    assert leaderboard["Pushya"]["total_points"] == 3.0

    # Swati (Saturn): Base = 1.0 * 0.65 = 0.65
    assert leaderboard["Swati"]["base_points"] == 0.65
    assert leaderboard["Swati"]["total_points"] == 0.65

    # Pure occupancy dominance ranking: Rohini (10.0) > Bharani (6.30) > Pushya (3.0) > Swati (0.65)
    assert res["dominant_nakshatra"]["nakshatra"] == "Rohini"
    assert leaderboard["Rohini"]["rank"] == 1
    assert leaderboard["Bharani"]["rank"] == 2
    assert leaderboard["Pushya"]["rank"] == 3
    assert leaderboard["Swati"]["rank"] == 4


def test_environmental_tally_prominence_weighted():
    """Verify that Macro Environmental Tally weights elements by Prominence score."""
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries"},  # Fire (baseline score 1.0)
            "grahas": {
                "Mars": {"sign": "Leo"},      # Fire (exalted prominence 2.50)
                "Sun": {"sign": "Taurus"},    # Earth (prominence 1.0)
                "Venus": {"sign": "Virgo"},   # Earth (prominence 1.0)
                "Mercury": {"sign": "Capricorn"}, # Earth (prominence 1.0)
                "Moon": {"sign": "Gemini"},   # Air (prominence 1.0)
                "Saturn": {"sign": "Libra"},  # Air (prominence 1.0)
                "Jupiter": {"sign": "Cancer"},# Water (prominence 1.0)
                "Rahu": {"sign": "Scorpio"},  # Water (prominence 1.0)
                "Ketu": {"sign": "Pisces"}    # Water (prominence 1.0)
            }
        }
    }

    mock_prominence = {
        "Mars": 2.50,
        "Sun": 1.0,
        "Venus": 1.0,
        "Mercury": 1.0,
        "Moon": 1.0,
        "Saturn": 1.0,
        "Jupiter": 1.0,
        "Rahu": 1.0,
        "Ketu": 1.0
    }

    tally = compute_environmental_tally(mock_vargas, prominence_map=mock_prominence)
    elem = tally["elements"]

    # Earth has 3 bodies with score 1.0 each = 3.0 pts
    # Fire has Lagna (1.0) + Mars (2.50) = 3.50 pts (even though only 2 bodies!)
    assert elem["counts"]["Earth"] == 3
    assert elem["counts"]["Fire"] == 2
    assert elem["points"]["Fire"] == 3.50
    assert elem["points"]["Earth"] == 3.00

    # Fire is dominant thermodynamically despite having fewer planets than Earth!
    assert elem["dominant"] == "Fire"


def test_environmental_tally_shadvarga_weighted():
    """
    Verify that Macro Environmental Tally aggregates elements and gunas
    across the Shadvarga matrix (D1:6, D9:5, D3:4, D2:2, D12:2, D30:1).
    """
    # Native with Aries (Fire/Movable) Lagna in D1, but Pisces (Water/Dual) in D9
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries"},
            "grahas": {p: {"sign": "Aries"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
        },
        "D9": {
            "lagna": {"sign": "Pisces"},
            "grahas": {p: {"sign": "Pisces"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
        },
        "D3": {
            "lagna": {"sign": "Cancer"},
            "grahas": {p: {"sign": "Cancer"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
        },
        "D2": {
            "lagna": {"sign": "Cancer"},
            "grahas": {p: {"sign": "Cancer"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
        },
        "D12": {
            "lagna": {"sign": "Cancer"},
            "grahas": {p: {"sign": "Cancer"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
        },
        "D30": {
            "lagna": {"sign": "Cancer"},
            "grahas": {p: {"sign": "Cancer"} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
        }
    }

    mock_prominence = {p: 1.0 for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}

    tally = compute_environmental_tally(mock_vargas, prominence_map=mock_prominence)
    elem = tally["elements"]
    guna = tally["gunas"]

    # 10 entities total with Prominence 1.0 each. Total Shadvarga points = 10.0
    # D1 (Weight 6/20 = 0.30): All 10 bodies in Aries (Fire, Movable) -> 3.0 pts Fire
    # D9 (Weight 5/20 = 0.25): All 10 bodies in Pisces (Water, Dual) -> 2.5 pts Water
    # D3, D2, D12, D30 (Remaining 9/20 = 0.45): In Cancer (Water, Movable) -> 4.5 pts Water
    # Total Water = 2.5 + 4.5 = 7.0 pts (70.0%)
    # Total Fire = 3.0 pts (30.0%)

    assert elem["counts"]["Fire"] == 10  # D1 count is 10
    assert elem["counts"]["Water"] == 0   # D1 count is 0
    assert elem["points"]["Fire"] == 3.0
    assert elem["points"]["Water"] == 7.0
    assert elem["percentages"]["Water"] == 70.0
    assert elem["percentages"]["Fire"] == 30.0
    assert elem["dominant"] == "Water"  # Deep Shadvarga water dominates surface fire!

    # Movable (Aries 3.0 + Cancer 4.5 = 7.5 pts), Dual (Pisces 2.5 pts)
    assert guna["points"]["Rajas (Movable)"] == 7.5
    assert guna["points"]["Sattva (Dual)"] == 2.5
    assert guna["dominant"] == "Rajas (Movable)"

    # Visual bi-directional breakdown metrics
    assert "breakdown" in elem
    assert len(elem["breakdown"]) == 4
    water_meta = next(x for x in elem["breakdown"] if x["key"] == "Water")
    assert water_meta["percentage"] == 70.0
    assert water_meta["baseline_pct"] == 25.0
    assert water_meta["deviation_pct"] == 45.0
    assert water_meta["status"] == "Surplus"

    fire_meta = next(x for x in elem["breakdown"] if x["key"] == "Fire")
    assert fire_meta["percentage"] == 30.0
    assert fire_meta["baseline_pct"] == 25.0
    assert fire_meta["deviation_pct"] == 5.0

    earth_meta = next(x for x in elem["breakdown"] if x["key"] == "Earth")
    assert earth_meta["percentage"] == 0.0
    assert earth_meta["deviation_pct"] == -25.0
    assert earth_meta["status"] == "Deficit"

    assert len(guna["breakdown"]) == 3
    assert len(tally["ayurvedic_doshas"]["breakdown"]) == 3




def test_atmakaraka_prominence_weight_and_fallback():
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries", "longitude": 10.0},
            "grahas": {
                "Sun": {"sign": "Aries", "longitude": 5.0, "degree_0_to_30": 5.0},
                # Mars has highest degree (28.0°) -> Atma Karaka
                "Mars": {"sign": "Capricorn", "longitude": 298.0, "degree_0_to_30": 28.0},
                "Moon": {"sign": "Taurus", "longitude": 34.0, "degree_0_to_30": 4.0},
                "Mercury": {"sign": "Gemini", "longitude": 70.0, "degree_0_to_30": 10.0},
                "Jupiter": {"sign": "Cancer", "longitude": 95.0, "degree_0_to_30": 5.0},
                "Venus": {"sign": "Pisces", "longitude": 350.0, "degree_0_to_30": 20.0},
                "Saturn": {"sign": "Libra", "longitude": 200.0, "degree_0_to_30": 20.0},
            },
            "cusps": [{"longitude": i * 30.0} for i in range(12)]
        }
    }
    
    mock_shadbala = {
        p: {"Total_Rupas": 5.0, "Total_Virupas": 300.0, "Pct_Required_Total": 100.0}
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    }

    rankings = compute_planetary_prominence_rankings(mock_vargas, mock_shadbala, {})
    mars_rank = next(item for item in rankings["leaderboard"] if item["planet"] == "Mars")

    # Verify Mars gains the +0.30 Atmakaraka bonus via dynamic fallback
    assert any("Atmakaraka Soul Signifier (+0.30)" in r for r in mars_rank["opportunity_reasons"])


def test_jaimini_ak_and_amk_prominence_scoring():
    """Verify that Atmakaraka gets +0.30, Amatyakaraka gets +0.15, and AK-AmK connection adds +0.15."""
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries", "longitude": 10.0},
            "grahas": {
                # Sun at 28.5° -> Atmakaraka (AK) in Leo (H5)
                "Sun": {"sign": "Leo", "longitude": 148.5, "degree_0_to_30": 28.5},
                # Mars at 24.0° -> Amatyakaraka (AmK) in Leo (H5 - conjunct AK!)
                "Mars": {"sign": "Leo", "longitude": 144.0, "degree_0_to_30": 24.0},
                # Venus at 20.0° -> Bhratrikaraka (BK) in Taurus (H2)
                "Venus": {"sign": "Taurus", "longitude": 50.0, "degree_0_to_30": 20.0},
                # Mercury at 15.0° -> Matrikaraka (MK) in Gemini (H3)
                "Mercury": {"sign": "Gemini", "longitude": 75.0, "degree_0_to_30": 15.0},
                # Jupiter at 10.0° -> Putrakaraka (PK) in Cancer (H4)
                "Jupiter": {"sign": "Cancer", "longitude": 100.0, "degree_0_to_30": 10.0},
                # Saturn at 5.0° -> Gnatikaraka (GK) in Libra (H7)
                "Saturn": {"sign": "Libra", "longitude": 185.0, "degree_0_to_30": 5.0},
                # Moon at 1.0° -> Darakaraka (DK) in Aries (H1)
                "Moon": {"sign": "Aries", "longitude": 1.0, "degree_0_to_30": 1.0}
            },
            "cusps": [{"longitude": i * 30.0} for i in range(12)]
        }
    }

    mock_shadbala = {
        p: {"Total_Rupas": 5.0, "Total_Virupas": 300.0, "Pct_Required_Total": 100.0}
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    }

    rankings = compute_planetary_prominence_rankings(mock_vargas, mock_shadbala, {})
    board = {item["planet"]: item for item in rankings["leaderboard"]}

    sun_reasons = board["Sun"]["opportunity_reasons"]
    mars_reasons = board["Mars"]["opportunity_reasons"]
    venus_reasons = board["Venus"]["opportunity_reasons"]

    # 1. Sun is AK (+0.30) and conjunct AmK (+0.15)
    assert any("Atmakaraka Soul Signifier (+0.30)" in r for r in sun_reasons)
    assert any("Jaimini Raja Yoga: AK-AmK Connection (+0.15)" in r for r in sun_reasons)

    # 2. Mars is AmK (+0.15) and conjunct AK (+0.15)
    assert any("Amatyakaraka Executive Mind (+0.15)" in r for r in mars_reasons)
    assert any("Jaimini Raja Yoga: AK-AmK Connection (+0.15)" in r for r in mars_reasons)

    # 3. Venus (BK) and lower Karakas must NOT receive arbitrary Jaimini stage bonuses
    assert not any("Karaka" in r for r in venus_reasons)


