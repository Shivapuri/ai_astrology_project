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

def test_bhava_chalita_aspects():
    bases = load_baselines()
    bhava = bases.get("aspects_bhava_chalita", {})
    
    chart = generate_kala_chart(
        name="Angelina Jolie", year=DOB_YEAR, month=DOB_MONTH, day=DOB_DAY,
        hour=DOB_HOUR, minute=DOB_MINUTE, latitude=LAT, longitude=LON, timezone_offset=TZ
    )
    
    adv_cusps = chart.get("advanced_aspects", {}).get("cusps", {})
    
    for aspecting in PLANETS:
        for house_num in range(1, 13):
            exp_list = bhava.get(aspecting, {}).get(str(house_num), [])
            exp_val = exp_list[0].get("value", 0.0) if exp_list else 0.0
            
            calc_val = adv_cusps.get(house_num, {}).get(aspecting, {}).get("raw", 0.0)
            
            diff = abs(calc_val - float(exp_val))
            
            assert diff <= 1.5, f"Mismatch for {aspecting} aspecting House {house_num}: expected {exp_val}, got {calc_val:.2f}"
            
def test_equal_houses_aspects():
    bases = load_baselines()
    bhava = bases.get("aspects_equal_houses", {})
    
    chart = generate_kala_chart(
        name="Angelina Jolie", year=DOB_YEAR, month=DOB_MONTH, day=DOB_DAY,
        hour=DOB_HOUR, minute=DOB_MINUTE, latitude=LAT, longitude=LON, timezone_offset=TZ
    )
    
    adv_cusps = chart.get("advanced_aspects", {}).get("equal_cusps", {})
    
    for aspecting in PLANETS:
        for house_num in range(1, 13):
            exp_list = bhava.get(aspecting, {}).get(str(house_num), [])
            exp_val = exp_list[0].get("value", 0.0) if exp_list else 0.0
            
            calc_val = adv_cusps.get(house_num, {}).get(aspecting, {}).get("raw", 0.0)
            
            diff = abs(calc_val - float(exp_val))
            
            assert diff <= 1.5, f"Mismatch for {aspecting} aspecting Equal House {house_num}: expected {exp_val}, got {calc_val:.2f}"

