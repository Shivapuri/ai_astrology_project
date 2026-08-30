import pytest
import json
import os
from jyotish.generate_jyotish import generate_kala_chart

DOB_YEAR = 1975
DOB_MONTH = 6
DOB_DAY = 4
DOB_HOUR = 9
DOB_MINUTE = 9
LAT = 34.0522
LON = -118.2437
TZ = -7.0

CSV_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "source-material", "software-setup", "sample-case"
)

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

def load_baselines():
    path = os.path.join(CSV_DIR, 'angelina_jolie_baselines.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_graha_drishti_baseline():
    bases = load_baselines()
    expected = bases.get("aspects_planets", {})
    
    chart = generate_kala_chart(
        name="Angelina Jolie", year=DOB_YEAR, month=DOB_MONTH, day=DOB_DAY,
        hour=DOB_HOUR, minute=DOB_MINUTE, latitude=LAT, longitude=LON, timezone_offset=TZ
    )
    
    advanced = chart.get("advanced_aspects", {}).get("planets", {})
    
    matches = 0
    
    for aspecting in PLANETS:
        for aspected in PLANETS:
            if aspecting == aspected: continue
            
            exp_list = expected.get(aspecting, {}).get(aspected, [])
            exp_val = exp_list[0].get("value", 0.0) if exp_list else 0.0
            
            # if expected is Y (Yuti), Kala does not calculate numerical aspect (0.0 points)
            if exp_val == "Y":
                exp_val = 0.0
            else:
                try:
                    exp_val = float(exp_val)
                except:
                    exp_val = 0.0
            
            calc_val = advanced.get(aspected, {}).get(aspecting, {}).get("raw", 0.0)
            
            # Since Kala truncates decimals for the UI tables in the new screenshots,
            # we allow a 1.5 tolerance.
            diff = abs(calc_val - exp_val)
            
            if diff <= 1.5:
                matches += 1
            else:
                
                assert False, f"Mismatch for {aspecting} aspecting {aspected}: expected {exp_val}, got {calc_val}"
                
    assert matches > 15, "Should have matches for standard aspects"

def test_graha_drishti_totals():
    bases = load_baselines()
    expected = bases.get("aspects_planets", {})
    
    chart = generate_kala_chart(
        name="Angelina Jolie", year=DOB_YEAR, month=DOB_MONTH, day=DOB_DAY,
        hour=DOB_HOUR, minute=DOB_MINUTE, latitude=LAT, longitude=LON, timezone_offset=TZ
    )
    
    totals = chart.get("advanced_aspects", {}).get("totals", {}).get("planets", {})
    
    for aspected in PLANETS:
        exp_plus_list = expected.get("+", {}).get(aspected, [])
        exp_plus = float(exp_plus_list[0].get("value", 0.0)) if exp_plus_list else 0.0
        
        exp_minus_list = expected.get("-", {}).get(aspected, [])
        exp_minus = float(exp_minus_list[0].get("value", 0.0)) if exp_minus_list else 0.0
        
        calc_plus = totals.get(aspected, {}).get("plus", 0.0)
        calc_minus = totals.get(aspected, {}).get("minus", 0.0)
        
        assert abs(calc_plus - exp_plus) <= 1.5, f"Plus Total mismatch for {aspected}: expected {exp_plus}, got {calc_plus}"
        assert abs(calc_minus - exp_minus) <= 1.5, f"Minus Total mismatch for {aspected}: expected {exp_minus}, got {calc_minus}"

def test_graha_drishti_yutis():
    bases = load_baselines()
    expected = bases.get("aspects_planets", {})
    
    chart = generate_kala_chart(
        name="Angelina Jolie", year=DOB_YEAR, month=DOB_MONTH, day=DOB_DAY,
        hour=DOB_HOUR, minute=DOB_MINUTE, latitude=LAT, longitude=LON, timezone_offset=TZ
    )
    
    yutis = chart.get("advanced_aspects", {}).get("yutis", {})
    
    for aspecting in PLANETS:
        for aspected in PLANETS:
            if aspecting == aspected: continue
            
            exp_list = expected.get(aspecting, {}).get(aspected, [])
            exp_val = exp_list[0].get("value", "") if exp_list else ""
            
            is_yuti_calc = aspected in yutis.get(aspecting, [])
            is_yuti_exp = (exp_val == "Y")
            
            assert is_yuti_calc == is_yuti_exp, f"Yuti mismatch for {aspecting} aspecting {aspected}: expected {is_yuti_exp}, got {is_yuti_calc}"

