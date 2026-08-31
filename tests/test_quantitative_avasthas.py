import pytest
import csv
import os
import re
from jyotish.generate_jyotish import generate_kala_chart

# Angelina Jolie Test Data
DOB_YEAR = 1975
DOB_MONTH = 6
DOB_DAY = 4
DOB_HOUR = 9
DOB_MINUTE = 9
LAT = 34.0522       # Los Angeles, CA
LON = -118.2437
TZ = -7.0           # PDT is UTC-7

CSV_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "source-material", "software-setup", "sample-case"
)

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

def parse_tagged_csv(filename):
    """
    Parses a tagged CSV file (e.g. angelina_jolie_cheshta.csv).
    Returns a dictionary matrix: matrix[giving_planet][receiving_planet] = parsed_data_list
    """
    matrix = {p: {} for p in PLANETS}
    filepath = os.path.join(CSV_DIR, filename)
    
    if not os.path.exists(filepath):
        pytest.skip(f"Baseline CSV {filename} not found.")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        col_planets = headers[1:8] # Extract exactly 7 planets
        
        for row in reader:
            giving_planet = row[0].strip()
            if giving_planet not in PLANETS:
                continue # Skip total rows or empty
                
            for i, cell in enumerate(row[1:8]):
                receiving_planet = col_planets[i].strip()
                if receiving_planet not in PLANETS:
                    continue
                
                # Extract all numbers and tags from the cell
                lines = cell.strip().split('\n')
                cell_data = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Regex to separate number and tag like [G], [R]
                    match = re.search(r'(.*?)(?:\[([GRBK])\])?$', line)
                    if match:
                        val_str = match.group(1).strip()
                        tag = match.group(2)
                        
                        try:
                            # Handle clean up of asterisks or weird OCR artifacts
                            val_str = val_str.replace('*', '').replace('+', '')
                            val = float(val_str)
                            cell_data.append({'value': val, 'color': tag})
                        except ValueError:
                            pass # Skip if unparseable
                            
                matrix[giving_planet][receiving_planet] = cell_data
                
    return matrix


@pytest.fixture(scope="module")
def aj_chart():
    """Generates the Angelina Jolie baseline chart once for all tests."""
    return generate_kala_chart(
        name="Angelina Jolie",
        year=DOB_YEAR,
        month=DOB_MONTH,
        day=DOB_DAY,
        hour=DOB_HOUR,
        minute=DOB_MINUTE,
        latitude=LAT,
        longitude=LON,
        timezone_offset=TZ, 
    )


@pytest.mark.skip(reason="Phase 5 WIP - Avasthas")
def test_cheshta_baseline_structure(aj_chart):
    """
    End-to-End test for Cheshta Avasthas against Angelina Jolie's baseline CSV.
    """
    calculated_matrices = aj_chart.get('avastha_matrix', {})
    d1_calculated = calculated_matrices.get('D1', {})
    calc_cheshta = d1_calculated.get('Cheshta', {})
    
    assert calc_cheshta, "Calculated Cheshta matrix is missing from context!"
    
    expected_cheshta = parse_tagged_csv('angelina_jolie_cheshta.csv')
    
    # Loop over the expected matrix and compare it to the calculated matrix
    for giver in PLANETS:
        for receiver in PLANETS:
            exp_cell = expected_cheshta[giver][receiver]
            
            # The backend structures it as dict[receiver][giver]
            calc_receiver_dict = calc_cheshta.get(receiver, {})
            calc_cell = calc_receiver_dict.get(giver)
            
            # Currently, the backend outputs a flat dict: {'top': '...', 'bottom': '...', 'color': '...'}
            # The expected data from CSV is a list of dicts: [{'value': 1.0, 'color': 'G'}, ...]
            
            if not exp_cell:
                # If the CSV cell is empty, the calculated cell should ideally be None or empty
                # assert not calc_cell, f"Expected empty cell for {giver}->{receiver}, but got {calc_cell}"
                continue
                
            # If the CSV has data, we expect the calculated cell to have data
            assert calc_cell is not None, f"Expected data for {giver}->{receiver}, but calculated was None."
            
            # Next Step for TDD:
            # You will need to align the structure of `calc_cell` in quantitative.py 
            # to match the 3-number diagonal / 2-number off-diagonal format of `exp_cell`.
            # For now, we print a useful failure if the Top values don't match.
            
            if giver != receiver:
                # Off-diagonal: Top value in CSV is the Modifier
                expected_modifier = exp_cell[0]['value']
                # Try to parse the calculated top value
                try:
                    calc_modifier = float(calc_cell.get('top', 0))
                except (ValueError, TypeError):
                    calc_modifier = 0.0
                    
                assert expected_modifier == calc_modifier, (
                    f"Modifier Mismatch for {giver} -> {receiver}: "
                    f"Expected {expected_modifier}, Got {calc_modifier}"
                )
