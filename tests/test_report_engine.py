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
