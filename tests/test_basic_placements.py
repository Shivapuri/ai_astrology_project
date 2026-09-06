import pytest
import csv
import os
from jyotish.generate_jyotish import generate_kala_chart

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "source-material", "software-setup", "sample-case", "angelina_jolie_basic_placements.csv"
)

def parse_dm_to_deg(dm_str: str) -> float:
    parts = dm_str.strip().split(":")
    return float(parts[0]) + float(parts[1]) / 60.0

@pytest.fixture(scope="module")
def aj_chart():
    return generate_kala_chart(
        name="Angelina Jolie",
        year=1975,
        month=6,
        day=4,
        hour=9,
        minute=9,
        latitude=34.0522,
        longitude=-118.2437,
        timezone_offset=-7.0
    )

def test_planetary_coordinates_and_retrogrades(aj_chart):
    """Verifies D1 Tropical signs, degrees, arcminutes, and retrograde states."""
    d1 = aj_chart["vargas"]["D1"]
    grahas = d1["grahas"]
    lagna = d1["lagna"]
    
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity = row["Entity"]
            expected_sign = row["Sign"]
            expected_deg = parse_dm_to_deg(row["Degree_Min"])
            expected_retro = row["Retrograde"].lower() == "true"
            
            if entity == "Lagna":
                calc_sign = lagna["sign"]
                calc_deg = lagna["degree_0_to_30"]
                calc_retro = False
            else:
                calc_sign = grahas[entity]["sign"]
                calc_deg = grahas[entity]["degree_0_to_30"]
                calc_retro = grahas[entity]["is_retrograde"]
                
            assert calc_sign == expected_sign, f"{entity} sign mismatch: expected {expected_sign}, got {calc_sign}"
            assert abs(calc_deg - expected_deg) <= 0.025, (
                f"{entity} degree mismatch: expected {expected_deg:.3f} ({row['Degree_Min']}), got {calc_deg:.3f}"
            )
            assert calc_retro == expected_retro, f"{entity} retrograde status mismatch: expected {expected_retro}"

def test_nakshatras_and_padas(aj_chart):
    """Verifies Nakshatra names and Padas (1-4) matching Kala exactly."""
    naks = aj_chart["nakshatras"]["grahas"]
    
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity = row["Entity"]
            expected_nak = row["Nakshatra"]
            expected_pada = int(row["Pada"])
            
            assert entity in naks, f"{entity} missing from nakshatra data"
            calc_nak = naks[entity]["nakshatra"]
            calc_pada = naks[entity]["pada"]
            
            # Allow transliteration variants (e.g. Mrigashira vs Mrigasira)
            calc_nak_norm = calc_nak.replace("sh", "s")
            expected_nak_norm = expected_nak.replace("sh", "s")
            assert calc_nak_norm == expected_nak_norm, f"{entity} Nakshatra: expected {expected_nak}, got {calc_nak}"
            assert calc_pada == expected_pada, f"{entity} Pada: expected {expected_pada}, got {calc_pada}"

def test_campanus_house_cusps_precision(aj_chart):
    """Verifies that all 12 Campanus house cusps match Kala within arcminute precision."""
    cusps = aj_chart["vargas"]["D1"]["cusps"]
    assert len(cusps) == 12, "Must calculate exactly 12 house cusps"
    
    # Cusp 1 is the Ascendant (28°53' Cancer)
    assert cusps[0]["sign"] == "Cancer"
    assert abs(cusps[0]["degree_0_to_30"] - (28.0 + 53.0 / 60.0)) <= 0.025
    
    # Cusp 10 is the Midheaven / MC (17°53' Aries)
    assert cusps[9]["sign"] == "Aries"
    assert abs(cusps[9]["degree_0_to_30"] - (17.0 + 53.0 / 60.0)) <= 0.025

def test_navatara_and_sublords(aj_chart):
    """Verifies Navatara (Tara index) and Vimshottari Lord/Sublord combinations."""
    naks = aj_chart["nakshatras"]["grahas"]
    
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity = row["Entity"]
            expected_lord_sublord = row["Lord_Sublord"]
            expected_tara = int(row["Tara"])
            
            assert entity in naks, f"{entity} missing from nakshatra data"
            calc_lord_sublord = naks[entity]["lord_sublord"]
            calc_tara = naks[entity]["tara"]
            
            assert calc_lord_sublord == expected_lord_sublord, (
                f"{entity} Lord/Sublord: expected {expected_lord_sublord}, got {calc_lord_sublord}"
            )
            assert calc_tara == expected_tara, (
                f"{entity} Tara index: expected {expected_tara}, got {calc_tara}"
            )

def test_relative_motion_speeds(aj_chart):
    """Verifies relative motion speeds matching Kala software."""
    naks = aj_chart["nakshatras"]["grahas"]
    
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity = row["Entity"]
            expected_speed_str = row["Rel_Speed"]
            if expected_speed_str == "--":
                assert naks[entity]["relative_speed"] == "--"
            else:
                expected_speed = float(expected_speed_str.rstrip("%"))
                calc_speed = float(naks[entity]["relative_speed"].rstrip("%"))
                assert abs(calc_speed - expected_speed) <= 0.1, (
                    f"{entity} relative speed mismatch: expected {expected_speed}%, got {calc_speed}%"
                )
