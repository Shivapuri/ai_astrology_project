"""
Tests for 7 Nakshatra Balance Types & Temperament Dossiers
Verifies:
- All 7 canonical temperament classes (Chara, Laghu, Mridu, Dhruva, Ugra, Tikshna, Mishra)
- Exactly 27 nakshatras distributed across the 7 groups with zero duplicates
- All positive & negative attributes and synthesis properties
- Integration with compute_nakshatra_dominance in report_engine
"""

import pytest
from jyotish.nakshatras.lore import (
    NAKSHATRA_TEMPERAMENT_DOSSIER,
    get_temperament_dossier,
    NAKSHATRA_DATABASE,
    ALL_NAKSHATRA_GROUPS
)
from jyotish.report.report_engine import compute_nakshatra_dominance


def test_temperament_dossier_structure_and_completeness():
    """Verify that all 7 canonical groups are defined with complete metadata."""
    expected_groups = ["Chara", "Laghu", "Mridu", "Dhruva", "Ugra", "Tikshna", "Mishra"]
    assert set(NAKSHATRA_TEMPERAMENT_DOSSIER.keys()) == set(expected_groups)

    all_stars = []
    for grp in expected_groups:
        dossier = get_temperament_dossier(grp)
        assert dossier, f"Missing dossier for {grp}"
        assert "label" in dossier and len(dossier["label"]) > 2
        assert "sanskrit" in dossier and len(dossier["sanskrit"]) > 2
        assert "essence" in dossier and len(dossier["essence"]) > 5
        assert "nakshatras" in dossier and len(dossier["nakshatras"]) >= 2
        assert "positives" in dossier and len(dossier["positives"]) == 4
        assert "negatives" in dossier and len(dossier["negatives"]) == 4

        # Two-Tier properties: Macro Psychology & Thermodynamics
        assert "macro_psychology" in dossier and len(dossier["macro_psychology"]) > 20
        assert "thermodynamics" in dossier
        therm = dossier["thermodynamics"]
        for key in ["surplus", "balanced", "deficit"]:
            assert key in therm and len(therm[key]) > 15, f"Missing/short {key} in thermodynamics for {grp}"

        # Two-Tier properties: Stars Detail
        assert "stars_detail" in dossier
        stars_det = dossier["stars_detail"]
        assert len(stars_det) == len(dossier["nakshatras"])

        for star in dossier["nakshatras"]:
            assert star in NAKSHATRA_DATABASE, f"Unknown star {star} in group {grp}"
            assert NAKSHATRA_DATABASE[star]["group"] == grp, f"Star {star} group mismatch with database"
            all_stars.append(star)

            assert star in stars_det, f"Missing star {star} in stars_detail for group {grp}"
            s_info = stars_det[star]
            assert "title" in s_info and len(s_info["title"]) > 5
            assert "span" in s_info and len(s_info["span"]) > 5
            assert "deity_symbol" in s_info and len(s_info["deity_symbol"]) > 5
            assert "positives" in s_info and len(s_info["positives"]) == 4
            assert "negatives" in s_info and len(s_info["negatives"]) == 4

    # All 27 nakshatras must be accounted for exactly once
    assert len(all_stars) == 27
    assert len(set(all_stars)) == 27


def test_temperament_breakdown_dossier_integration():
    """Verify that report_engine attaches the dossier and updated sanskrit labels."""
    mock_nakshatras = {
        "Lagna": {"nakshatra": "Shravana", "pada": 1},  # Chara (4pts)
        "Moon": {"nakshatra": "Swati", "pada": 2},      # Chara (8pts)
        "Sun": {"nakshatra": "Ardra", "pada": 3},       # Tikshna (2pts)
        "Mars": {"nakshatra": "Rohini", "pada": 4}      # Dhruva (1pt)
    }

    res = compute_nakshatra_dominance({}, mock_nakshatras, None)
    tb = res["temperament_breakdown"]
    assert len(tb) == 6

    tb_map = {item["group"]: item for item in tb}
    
    # Check Chara
    chara = tb_map["Chara"]
    assert chara["sanskrit"] == "Cara / Cala"
    assert chara["points"] == 12.0  # Lagna (4) + Moon (8)
    assert chara["status"] == "Surplus"
    assert "dossier" in chara
    assert chara["dossier"]["label"] == "Mobile"
    assert "Punarvasu" in chara["dossier"]["nakshatras"]

    # Check Laghu
    laghu = tb_map["Laghu"]
    assert laghu["sanskrit"] == "Kṣipra / Laghu"
    assert laghu["points"] == 0.0
    assert laghu["status"] == "Deficit"
    assert "dossier" in laghu
    assert "Ashwini" in laghu["dossier"]["nakshatras"]


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


def test_temperament_relationship_matrix():
    """Verify classical Resonances and Dissonances between temperament groups."""
    from jyotish.nakshatras.lore import get_temperament_relationship
    res = get_temperament_relationship("Tikshna", "Ugra")
    assert res is not None
    assert res["type"] == "Resonance"

    res_alias = get_temperament_relationship("Laghu", "Chara")
    assert res_alias is not None
    assert res_alias["type"] == "Resonance"

    diss = get_temperament_relationship("Tikshna", "Mridu")
    assert diss is not None
    assert diss["type"] == "Dissonance"

    diss2 = get_temperament_relationship("Dhruva", "Laghu")
    assert diss2 is not None
    assert diss2["type"] == "Dissonance"

