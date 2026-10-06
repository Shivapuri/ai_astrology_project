"""
tests/test_stage3_integration.py
================================
Unit tests verifying the Stage 3 Bhāva Bala and Stage 2A/2B pipeline adapter contracts.
Ensures that ChartPipeline.to_dict() provides complete, non-regressing schemas for all frontend consumers:
- aspects.js (aspect_matrices and advanced_aspects)
- rashi_drishti.js (aspect_matrices.rasi_drishti)
- shadbala_widget.js & app.js (dual-casing shadbala keys)
- varga_dignities.js (audited dignities stamped on vargas)
- bhava_bala.js & context_info.js (bhava_bala, harsha_bala, house_atmosphere)
"""

import pytest
from jyotish.pipeline import ChartPipeline


def test_pipeline_to_dict_stage3_contracts():
    pipeline = ChartPipeline(name="Angelina Jolie", year=1975, month=6, day=4, hour=9, minute=9)
    chart = pipeline.to_dict()

    # 1. Stage 3 Bhāva Bala & House Atmosphere contracts
    assert "bhava_bala" in chart
    assert "harsha_bala" in chart
    assert "house_atmosphere" in chart

    assert len(chart["bhava_bala"]) == 12
    assert 1 in chart["bhava_bala"]
    h1 = chart["bhava_bala"][1]
    assert "total_virupas" in h1
    assert "total_rupas" in h1
    assert "augmented_virupas" in h1
    assert "bhavadhipathi_bala" in h1
    assert "bhava_digbala" in h1
    assert "bhava_drishti_bala" in h1

    assert "dusthana_joy" in chart["harsha_bala"]
    assert 6 in chart["harsha_bala"]["dusthana_joy"]
    assert 8 in chart["harsha_bala"]["dusthana_joy"]
    assert 12 in chart["harsha_bala"]["dusthana_joy"]

    assert len(chart["house_atmosphere"]) == 12
    atm1 = chart["house_atmosphere"][1]
    assert "environmental_weather" in atm1
    assert "net_atmosphere_score" in atm1
    assert "classification" in atm1


def test_aspect_matrices_and_advanced_aspects_coexist():
    pipeline = ChartPipeline(name="Angelina Jolie", year=1975, month=6, day=4, hour=9, minute=9)
    chart = pipeline.to_dict()

    # 2. Both aspect_matrices and advanced_aspects must coexist for interactive ray tracing and fallback
    assert "aspect_matrices" in chart
    assert "advanced_aspects" in chart
    assert "varga_advanced_aspects" in chart

    am = chart["aspect_matrices"]
    assert "graha_drishti" in am
    assert "outgoing" in am["graha_drishti"]
    assert "incoming" in am["graha_drishti"]
    assert "cusp_drishti" in am
    assert "by_house" in am["cusp_drishti"]
    assert "rasi_drishti" in am
    assert "sign_to_signs" in am["rasi_drishti"]
    assert "benefic_malefic_totals" in am
    assert "planets" in am["benefic_malefic_totals"]
    assert "cusps" in am["benefic_malefic_totals"]

    adv = chart["advanced_aspects"]
    assert "planets" in adv
    assert "cusps" in adv
    assert "equal_cusps" in adv
    assert "totals" in adv
    assert "yutis" in adv


def test_shadbala_dual_casing_harmonization():
    pipeline = ChartPipeline(name="Angelina Jolie", year=1975, month=6, day=4, hour=9, minute=9)
    sb = pipeline.shadbala

    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for p in planets:
        p_data = sb[p]
        # PascalCase (for shadbala_widget.js 25-row breakdown grid)
        assert "Total_Virupas" in p_data
        assert "Total_Rupas" in p_data
        assert "Sthana_Bala" in p_data
        assert "Dig_Bala" in p_data
        assert "Kala_Bala" in p_data
        assert "Cheshta_Bala" in p_data
        assert "Naisargika_Bala" in p_data
        assert "Drik_Bala" in p_data
        assert "Required_Total" in p_data

        # Lowercase aliases (for app.js legacy table updateShadbalaTable)
        assert "sthana_bala" in p_data
        assert "dig_bala" in p_data
        assert "kala_bala" in p_data
        assert "cheshta_bala" in p_data
        assert "naisargika_bala" in p_data
        assert "drik_bala" in p_data
        assert "total_rupa" in p_data
        assert "total_virupas" in p_data
        assert "required_rupa" in p_data
        assert "ratio" in p_data

        # Values match
        assert p_data["sthana_bala"] == p_data["Sthana_Bala"]
        assert p_data["total_virupas"] == p_data["Total_Virupas"]
        assert p_data["total_rupa"] == p_data["Total_Rupas"]


def test_varga_dignities_stamped_on_vargas():
    pipeline = ChartPipeline(name="Angelina Jolie", year=1975, month=6, day=4, hour=9, minute=9)
    vargas = pipeline.vargas
    dignities = pipeline.dignities["varga_dignities"]

    for v_name in ["D1", "D9", "D10"]:
        assert v_name in vargas
        assert v_name in dignities
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            p_breakdown = vargas[v_name]["grahas"][p]["dignity_breakdown"]
            dig_ref = dignities[v_name][p]
            assert p_breakdown["final_dignity"] == dig_ref["dignity"]
            assert p_breakdown["sign_lord"] == dig_ref["sign_lord"]
            assert p_breakdown["natural_relationship"] == dig_ref["natural_relationship"]
            assert p_breakdown["compound_relationship"] == dig_ref["compound_relationship"]
