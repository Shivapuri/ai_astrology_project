"""
Tests for Astra Nakshatra Foundation Report Engine (tests/test_report_engine.py)

Validates:
- All 27 Nakshatras complete lore and classification database
- 4-step Prominence-scaled Nakshatra scoring system
- Side-by-side Ascendant & Moon Nakshatra descriptive dossiers (No Automated Synthesis)
- Nakshatra Dominance Leaderboard and 6-Group Temperament Balance (16.7% Baseline)
- Complete purge of downstream engines from generate_report_payload
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
    get_detailed_nakshatra_dossier,
    compute_ascendant_and_moon_nakshatras,
    get_detailed_sign_dossier,
    compute_rising_rashi_and_navamsha,
    compute_elemental_and_modal_balance,
    generate_report_payload,
    ZODIAC_SIGNS
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


def test_get_detailed_nakshatra_dossier_all_27():
    """Verify that all 27 nakshatras generate complete, rich descriptive dossiers."""
    for nak_name in NAKSHATRA_DATABASE:
        dossier = get_detailed_nakshatra_dossier(nak_name, pada=2)
        assert dossier["name"] == nak_name
        assert dossier["pada"] == 2
        assert len(dossier["sanskrit_meaning"]) > 0, f"Empty meaning for {nak_name}"
        assert len(dossier["deity"]) > 0, f"Empty deity for {nak_name}"
        assert len(dossier["symbol"]) > 0, f"Empty symbol for {nak_name}"
        assert len(dossier["group"]) > 0, f"Empty group for {nak_name}"
        assert len(dossier["group_label"]) > 0, f"Empty group_label for {nak_name}"
        assert len(dossier["keywords"]) >= 2, f"Too few keywords for {nak_name}"
        assert len(dossier["description"]) > 20, f"Short description for {nak_name}"


def test_compute_ascendant_and_moon_nakshatras_structure():
    """Verify side-by-side Ascendant and Moon dossiers contain NO automated synthesis or friction scores."""
    mock_vargas = {"D1": {"lagna": {"sign": "Aries"}}}
    mock_nakshatras = {
        "Lagna": {"nakshatra": "Uttara Ashadha", "pada": 1},
        "Moon": {"nakshatra": "Rohini", "pada": 3}
    }

    asc_moon = compute_ascendant_and_moon_nakshatras(mock_vargas, mock_nakshatras)

    # Must contain ONLY ascendant and moon
    assert set(asc_moon.keys()) == {"ascendant", "moon"}

    # Assert no automated synthesis / friction math exists
    for key in ["synthesis", "friction_score", "state", "panchadha_maitri", "tattva_status"]:
        assert key not in asc_moon, f"Forbidden key {key} found in ascendant_and_moon"
        assert key not in asc_moon["ascendant"], f"Forbidden key {key} found in ascendant dossier"
        assert key not in asc_moon["moon"], f"Forbidden key {key} found in moon dossier"

    # Verify Ascendant properties
    asc = asc_moon["ascendant"]
    assert asc["name"] == "Uttara Ashadha"
    assert asc["pada"] == 1
    assert "Action / Ahaṃkāra" in asc["role"]
    assert asc["group"] == "Dhruva"
    assert "Fortified Determination" in asc["keywords"]

    # Verify Moon properties
    moon = asc_moon["moon"]
    assert moon["name"] == "Rohini"
    assert moon["pada"] == 3
    assert "Perception / Manas" in moon["role"]
    assert moon["group"] == "Dhruva"
    assert len(moon["description"]) > 20


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


def test_nakshatra_prominence_scaled_scoring():
    """Verify that Prominence scaling weights occupancy dynamically."""
    mock_nakshatras = {
        "Lagna": {"nakshatra": "Bharani", "pada": 1},
        "Moon": {"nakshatra": "Rohini", "pada": 2},
        "Sun": {"nakshatra": "Pushya", "pada": 3},
        "Mars": {"nakshatra": "Bharani", "pada": 4},
        "Saturn": {"nakshatra": "Swati", "pada": 1}
    }

    # Custom prominence map:
    mock_prominence = {
        "Moon": 1.25,
        "Sun": 1.50,
        "Mars": 2.30,
        "Saturn": 0.65
    }

    res = compute_nakshatra_dominance({}, mock_nakshatras, None, prominence_map=mock_prominence)
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


def test_universal_catalyst_rule():
    """Verify that Krittika distributes points to all 6 groups simultaneously."""
    mock_nakshatras = {
        "Sun": {"nakshatra": "Krittika", "pada": 1}  # Sun base weight = 2.0 pts
    }
    res = compute_nakshatra_dominance({}, mock_nakshatras, None)
    tb = res["temperament_breakdown"]
    assert len(tb) == 6
    for item in tb:
        assert item["points"] == 2.0
        assert item["status"] == "Balanced"  # Each is exactly 1/6 (16.7%), zero deviation
    assert "Krittika" in res["universal_catalysts"]


def test_compute_rising_rashi_and_navamsha():
    """Verify side-by-side Rising Rāśi and Rising Navāṁśa sign dossiers and Vargottama detection."""
    # Test non-vargottama
    mock_vargas = {
        "D1": {"lagna": {"sign": "Capricorn", "degree_0_to_30": 14.5}},
        "D9": {"lagna": {"sign": "Leo", "degree_0_to_30": 2.25}}
    }
    rising = compute_rising_rashi_and_navamsha(mock_vargas)

    assert set(rising.keys()) == {"rashi", "navamsha", "is_vargottama", "vargottama_note"}
    assert rising["is_vargottama"] is False
    assert rising["vargottama_note"] is None

    # Check Rashi dossier
    rashi = rising["rashi"]
    assert rashi["sign"] == "Capricorn"
    assert rashi["ruler"] == "Saturn"
    assert rashi["element"] == "Earth"
    assert "Movable" in rashi["modality"]
    assert rashi["degree_in_sign"] == 14.5
    assert rashi["degree_formatted"] == "14° 30'"
    assert "Physical Body" in rashi["role"]
    assert len(rashi["pillars"]) > 0
    for col in rashi["pillars"]:
        assert "category" in col
        assert "keywords" in col
        assert len(col["keywords"]) > 0

    # Check Navamsha dossier
    nav = rising["navamsha"]
    assert nav["sign"] == "Leo"
    assert nav["ruler"] == "Sun"
    assert nav["element"] == "Fire"
    assert "Fixed" in nav["modality"]
    assert "Inner Soul Trajectory" in nav["role"]
    assert len(nav["pillars"]) > 0

    # Test Vargottama case
    mock_vargas_varg = {
        "D1": {"lagna": {"sign": "Aries", "degree_0_to_30": 2.5}},
        "D9": {"lagna": {"sign": "Aries", "degree_0_to_30": 22.5}}
    }
    rising_varg = compute_rising_rashi_and_navamsha(mock_vargas_varg)
    assert rising_varg["is_vargottama"] is True
    assert "Vargottama Lagna" in rising_varg["vargottama_note"]
    assert rising_varg["rashi"]["sign"] == "Aries"
    assert rising_varg["navamsha"]["sign"] == "Aries"


def test_compute_elemental_and_modal_balance_structure():
    """Verify 4 elements (25.0% baseline) and 3 modalities (33.3% baseline) calculation."""
    mock_vargas = {
        "D1": {
            "lagna": {"sign": "Aries"},
            "grahas": {
                "Sun": {"sign": "Leo"},
                "Moon": {"sign": "Cancer"},
                "Mars": {"sign": "Scorpio"},
                "Mercury": {"sign": "Virgo"},
                "Jupiter": {"sign": "Sagittarius"},
                "Venus": {"sign": "Libra"},
                "Saturn": {"sign": "Aquarius"},
                "Rahu": {"sign": "Taurus"},
                "Ketu": {"sign": "Scorpio"}
            }
        }
    }
    prom_map = {"Sun": 1.5, "Moon": 1.2, "Mars": 1.0, "Mercury": 1.0, "Jupiter": 1.4, "Venus": 1.0, "Saturn": 1.0, "Rahu": 1.0, "Ketu": 1.0}
    bal = compute_elemental_and_modal_balance(mock_vargas, prom_map)

    assert "elements" in bal
    assert "modalities" in bal
    assert bal["elements"]["baseline_pct"] == 25.0
    assert bal["modalities"]["baseline_pct"] == 33.3

    elem_breakdown = bal["elements"]["breakdown"]
    assert len(elem_breakdown) == 4
    elem_names = [e["element"] for e in elem_breakdown]
    assert set(elem_names) == {"Fire", "Earth", "Air", "Water"}
    for e in elem_breakdown:
        assert e["baseline_pct"] == 25.0
        assert e["status"] in ["Surplus", "Deficit", "Balanced"]
        assert "points" in e
        assert "percentage" in e
        assert "display_name" in e
        assert "sanskrit" in e
        assert "root_traits" in e
        assert "nature" in e
        assert "color" in e
        assert "bg" in e

    modal_breakdown = bal["modalities"]["breakdown"]
    assert len(modal_breakdown) == 3
    modal_names = [m["modality"] for m in modal_breakdown]
    assert set(modal_names) == {"Rajas (Movable)", "Tamas (Fixed)", "Sattva (Dual)"}
    for m in modal_breakdown:
        assert m["baseline_pct"] == 33.3
        assert m["status"] in ["Surplus", "Deficit", "Balanced"]
        assert "points" in m
        assert "percentage" in m
        assert "display_name" in m
        assert "sanskrit" in m
        assert "nature" in m
        assert "color" in m
        assert "bg" in m


def test_generate_kala_chart_report_payload_streamlined():
    """
    Verify that generate_report_payload outputs all foundational sections,
    elemental and modal balances, planetary rankings, and flowchart assets.
    """
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

    # 1. Assert payload contains all 9 required top-level keys
    expected_top_keys = {
        "title",
        "ascendant_and_moon",
        "rising_signs",
        "nakshatra_dominance",
        "balance_of_nakshatra_types",
        "elemental_and_modal_balance",
        "planetary_rankings",
        "significations_data",
        "flowcharts"
    }
    assert set(rep.keys()) == expected_top_keys, f"Report payload keys mismatch: {set(rep.keys())}"
    assert rep["title"] in ["Astra Chart Assessment Report", "Nakshatra Foundation Report"]

    # 2. Assert rising_signs structure
    rising_signs = rep["rising_signs"]
    assert set(rising_signs.keys()) == {"rashi", "navamsha", "is_vargottama", "vargottama_note"}
    assert rising_signs["rashi"]["sign"]
    assert rising_signs["rashi"]["ruler"]
    assert rising_signs["rashi"]["element"]
    assert rising_signs["rashi"]["modality"]
    assert len(rising_signs["rashi"]["pillars"]) > 0
    assert rising_signs["navamsha"]["sign"]
    assert isinstance(rising_signs["is_vargottama"], bool)

    # 3. Assert ascendant_and_moon contains keys ["ascendant", "moon"] and NO automated synthesis
    asc_moon = rep["ascendant_and_moon"]
    assert set(asc_moon.keys()) == {"ascendant", "moon"}
    for forbidden in ["synthesis", "friction_score", "state", "panchadha_maitri", "summary"]:
        assert forbidden not in asc_moon
        assert forbidden not in asc_moon["ascendant"]
        assert forbidden not in asc_moon["moon"]

    # Verify dossier completeness in real chart
    assert asc_moon["ascendant"]["name"]
    assert asc_moon["ascendant"]["sanskrit_meaning"]
    assert asc_moon["ascendant"]["deity"]
    assert asc_moon["ascendant"]["symbol"]
    assert asc_moon["ascendant"]["group"]
    assert len(asc_moon["ascendant"]["keywords"]) >= 2
    assert len(asc_moon["ascendant"]["description"]) > 20

    # 4. Assert balance_of_nakshatra_types contains exactly 6 categories with baseline_pct == 16.7
    balance = rep["balance_of_nakshatra_types"]
    assert balance["baseline_pct"] == 16.7
    tb = balance["temperament_breakdown"]
    assert len(tb) == 6
    for item in tb:
        assert item["baseline_pct"] == 16.7
        assert item["status"] in ["Surplus", "Deficit", "Balanced"]
        assert "points" in item
        assert "percentage" in item
        assert "group" in item
        assert "display_name" in item

    assert balance["dominant_temperament"] is not None

    # 5. Assert nakshatra_dominance structure
    nak_dom = rep["nakshatra_dominance"]
    assert "leaderboard" in nak_dom
    assert "dominant_nakshatra" in nak_dom
    assert "total_points" in nak_dom
    assert len(nak_dom["leaderboard"]) > 0
    assert nak_dom["total_points"] > 0

    # 6. Assert elemental_and_modal_balance structure
    elem_modal = rep["elemental_and_modal_balance"]
    assert "elements" in elem_modal
    assert "modalities" in elem_modal
    assert elem_modal["elements"]["baseline_pct"] == 25.0
    assert elem_modal["modalities"]["baseline_pct"] == 33.3
    assert len(elem_modal["elements"]["breakdown"]) == 4
    assert len(elem_modal["modalities"]["breakdown"]) == 3

    # 7. Assert planetary_rankings structure
    rankings = rep["planetary_rankings"]
    assert "leaderboard" in rankings
    assert "chart_commander" in rankings
    assert "prominence_map" in rankings
    assert len(rankings["leaderboard"]) >= 7
    top_commander = rankings["chart_commander"]
    assert "planet" in top_commander
    assert "prominence_score" in top_commander
    assert "shadbala_ratio" in top_commander
    assert "dignity_mood" in top_commander
    assert "opportunity_reasons" in top_commander

    # 8. Assert flowcharts and significations_data
    assert "planets" in rep["flowcharts"]
    assert "signs" in rep["flowcharts"]
    assert "houses" in rep["flowcharts"]
    assert "planets" in rep["significations_data"]
    assert "signs" in rep["significations_data"]
    assert "houses" in rep["significations_data"]

    # 9. Assert purged automated narrative essays and synthesis engines do NOT exist in the payload
    purged_keys = [
        "polarity_core",
        "operational_axis",
        "environmental_tally",
        "contextual_yogas",
        "background_canvas",
        "planetary_interpretations",
        "synthesis_ingredients",
        "harmonic_overlays"
    ]
    for key in purged_keys:
        assert key not in rep, f"Purged key '{key}' still exists in report payload!"

