import pytest
import csv
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

CODE_TO_DIGNITY = {
    "EX": "Exalted",
    "MT": "Moolatrikona",
    "OH": "Own Sign",
    "GF": "Great Friend's Sign",
    "F": "Friend's Sign",
    "N": "Neutral's Sign",
    "E": "Enemy's Sign",
    "GE": "Great Enemy's Sign",
    "DB": "Debilitated"
}

def load_dignities():
    expected = {}
    path = os.path.join(CSV_DIR, 'angelina_jolie_dignities.csv')
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        planets = headers[1:]
        for row in reader:
            varga = f"D{row[0]}"
            expected[varga] = {}
            for i, p in enumerate(planets):
                expected[varga][p] = CODE_TO_DIGNITY.get(row[i + 1].strip(), row[i + 1].strip())
    return expected

def test_dignities_baseline():
    expected = load_dignities()
    chart = generate_kala_chart(
        name="Angelina Jolie", year=DOB_YEAR, month=DOB_MONTH, day=DOB_DAY,
        hour=DOB_HOUR, minute=DOB_MINUTE, latitude=LAT, longitude=LON, timezone_offset=TZ
    )
    
    # Compare
    vargas = chart.get("vargas", {})
    for varga_name, expected_planets in expected.items():
        assert varga_name in vargas, f"Varga {varga_name} missing from calculated chart."
        calc_grahas = vargas[varga_name].get("grahas", {})
        for planet in PLANETS:
            exp_dig = expected_planets[planet]
            # Handle potential mismatch in key naming
            if planet not in calc_grahas: continue
            
            calc_dig = calc_grahas[planet]["dignity_breakdown"]["final_dignity"]
            assert calc_dig == exp_dig, f"Dignity mismatch for {planet} in {varga_name}. Expected {exp_dig}, Got {calc_dig}."

