import pytest
import os
import sys
import subprocess
from scripts.analyze_ascendant import evaluate_ascendant
from jyotish import native_manager
from app import compute_chart_data

CHARTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "Charts.jsonl")

def test_evaluate_ascendant_shivapuri():
    native = native_manager.get_native_by_id(CHARTS_FILE, "shivapuri")
    assert native is not None, "Shivapuri chart must exist in database"
    
    chart = compute_chart_data(native)
    res = evaluate_ascendant(chart)

    # 1. Rising sign & degree
    assert res["rising_sign"] == "Leo"
    assert 9.0 <= res["rising_degree"] <= 10.0
    assert res["sign_meta"]["element"] == "Fire (Agni)"
    assert res["sign_meta"]["ruler"] == "Sun"

    # 2. Lagnesha
    assert res["lagnesha"]["planet"] == "Sun"
    assert res["lagnesha"]["sign"] == "Scorpio"
    assert res["lagnesha"]["house_whole_sign"] == 4

    # 3. Sun as Sthira Karaka
    assert res["sun_karaka"]["sign"] == "Scorpio"
    assert "shadbala_pct" in res["sun_karaka"]

    # 4. Functional matrix for Leo
    # Leo has Mars as Yogakaraka (rules 4 and 9)
    assert res["functional_matrix"]["yogakaraka"] == "Mars"
    assert "Sun" in res["functional_matrix"]["functional_benefics"]
    assert "Jupiter" in res["functional_matrix"]["functional_benefics"]
    assert "Saturn" in res["functional_matrix"]["trishadaya_troublemakers"]

    # 5. Sudarshana Chakra
    assert res["sudarshana_chakra"]["janma_lagna"] == "Leo"
    assert res["sudarshana_chakra"]["chandra_lagna"] == "Capricorn"
    assert res["sudarshana_chakra"]["surya_lagna"] == "Scorpio"

    # 6. Official Master Graha Diagnostics (Lagna Vitality)
    assert res["vitality_score"] == 5.1
    assert res["vitality_tier"] == "Strained Horizon"
    assert res["archetype"] == "The Contemplative Seeker"
    assert res["pillar_scores"]["pillar_1_captain"] == -0.9
    assert res["pillar_scores"]["pillar_4_skylight"] == 0.9

def test_analyze_ascendant_cli():
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "analyze_ascendant.py")
    res = subprocess.run([sys.executable, script_path, "--native", "Shivapuri"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "ASCENDANT (LAGNA) & 1ST HOUSE REPORT" in res.stdout
    assert "Leo" in res.stdout

def test_generate_ascendant_report():
    from scripts.generate_ascendant_report import generate_report
    out_file = generate_report("Shivapuri")
    assert os.path.exists(out_file)
    assert out_file.endswith("Ascendant_Interpretation.md")
    
    # Check folder structure for 6 tiers
    person_dir = os.path.dirname(out_file)
    raw_dir = os.path.join(person_dir, "raw_sources")
    assert os.path.isdir(raw_dir)
    assert os.path.isdir(os.path.join(raw_dir, "tier_1_horizon_degree"))
    assert os.path.isdir(os.path.join(raw_dir, "tier_2_lagnesha"))
    assert os.path.isdir(os.path.join(raw_dir, "tier_3_sun_karaka"))
    assert os.path.isdir(os.path.join(raw_dir, "tier_4_field_inhabitants"))
    assert os.path.isdir(os.path.join(raw_dir, "tier_5_aspects_skylight"))
    assert os.path.isdir(os.path.join(raw_dir, "tier_6_rising_sign_nakshatra"))

    with open(out_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "The Contemplative Seeker" in content
    assert "5.1 / 10.0" in content
    assert "Part 1: Tier 1 Report" in content
    assert "Part 2: Tier 2 Report" in content
    assert "Part 3: Tier 3 Report — The Sthira Karaka" in content
    assert "Double Confluence (Karaka-Lord Identity" in content
    assert "Part 8: Master Holistic Synthesis" in content
