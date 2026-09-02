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
        return matrix
        
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        col_planets = headers[1:8] # Extract exactly 7 planets
        
        for row in reader:
            giving_planet = row[0].strip()
            if giving_planet not in PLANETS:
                continue 
                
            for i, cell in enumerate(row[1:8]):
                receiving_planet = col_planets[i].strip()
                if receiving_planet not in PLANETS:
                    continue
                
                # Extract all numbers and tags from the cell (e.g. '11.7[R]', '32.7[R]+92.7[G]')
                matches = re.findall(r'([+-]?\d+\.?\d*)\s*\[([A-Z])\]', cell)
                cell_data = []
                for val_str, tag in matches:
                    try:
                        val = float(val_str)
                        cell_data.append({'value': abs(val), 'color': tag})
                    except ValueError:
                        pass
                            
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

MATRIX_TARGETS = [
    ("Uccha", "angelina_jolie_uccha.csv"),
    ("Dig", "angelina_jolie_dig.csv"),
    ("Cheshta", "angelina_jolie_cheshta.csv"),
    ("Subha", "angelina_jolie_subha.csv"),
    ("Ishta", "angelina_jolie_ishta.csv")
]

@pytest.mark.parametrize("matrix_name, csv_filename", MATRIX_TARGETS)
def test_quantitative_avasthas_matrix(aj_chart, matrix_name, csv_filename):
    calculated_matrices = aj_chart.get('avastha_matrix', {})
    d1_calculated = calculated_matrices.get('D1', {})
    calc_matrix = d1_calculated.get(matrix_name, {})
    
    assert calc_matrix, f"Calculated {matrix_name} matrix is missing from context!"
    
    expected_matrix = parse_tagged_csv(csv_filename)
    
    # 1. Check Baselines (Diagonals) and Net Modifiers (Off-Diagonals)
    for giver in PLANETS:
        for receiver in PLANETS:
            exp_cell = expected_matrix[giver][receiver]
            calc_cell = calc_matrix.get(receiver, {}).get(giver)
            
            if giver == receiver:
                # Baseline Check
                if exp_cell:
                    exp_baseline = exp_cell[0]['value']
                    try:
                        calc_baseline = calc_cell.get('base', 0)
                    except (ValueError, TypeError):
                        calc_baseline = 0.0
                    
                    assert abs(exp_baseline - calc_baseline) <= 1.5, f"{matrix_name} - {giver} Baseline: Expected {exp_baseline}, Got {calc_baseline}"
            else:
                # Net Modifier Check
                exp_net = 0.0
                if exp_cell:
                    num_mods = len(exp_cell) // 2
                    modifiers = exp_cell[:num_mods]
                    for item in modifiers:
                        val = item['value']
                        color = item['color']
                        if color == 'G':
                            exp_net += val
                        elif color in ('R', 'K'):
                            exp_net -= val
                        
                calc_net = 0.0
                if calc_cell:
                    try:
                        calc_net = calc_cell.get('net_pull', 0)
                    except (ValueError, TypeError):
                        calc_net = 0.0
                
                assert abs(exp_net - calc_net) <= 0.5, f"{matrix_name} - {giver} -> {receiver} Net Modifier: Expected {exp_net:.1f}, Got {calc_net:.1f}"
