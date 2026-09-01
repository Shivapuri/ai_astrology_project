import pytest
from jyotish.shadbala.shadbala import calculate_cheshta_bala, calculate_nathonnatha_bala
from jyotish.aspects.aspects import get_graha_drishti as calculate_drishti_value

def test_drishti_value():
    # 180 degrees should be 60
    assert calculate_drishti_value("Sun", 0, 180) == 60.0
    # 120 degrees should be 30
    assert calculate_drishti_value("Sun", 0, 120) == 30.0
    # < 30 degrees should be 0
    assert calculate_drishti_value("Sun", 0, 15) == 0.0
    
def test_nathonnatha_bala():
    # Sun at MC (Midday) gets 60
    assert calculate_nathonnatha_bala("Sun", 90.0, 90.0) == 60.0
    # Moon at IC (Midnight) gets 60
    assert calculate_nathonnatha_bala("Moon", 270.0, 90.0) == 60.0
    # Mercury always 60
    assert calculate_nathonnatha_bala("Mercury", 45.0, 100.0) == 60.0

from jyotish.generate_jyotish import generate_kala_chart

def test_shadbala_6_pillars():
    chart = generate_kala_chart(
        name="Angelina Jolie", year=1975, month=6, day=4,
        hour=9, minute=9, latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )
    shadbala_data = chart.get('shadbala', {})
    
    expected_shadbala = {
        'Sun': {'Sthana_Bala': 145.86, 'Dig_Bala': 43.5, 'Kala_Bala': 139.39, 'Cheshta_Bala': 58.02, 'Naisargika_Bala': 60.0, 'Drik_Bala': 12.07, 'Total_Virupas': 458.84, 'Subha_Phala': 6.56, 'Asubha_Phala': 53.44, 'Ishta_Phala': 48.44, 'Kashta_Phala': 11.56},
        'Moon': {'Sthana_Bala': 296.36, 'Dig_Bala': 1.82, 'Kala_Bala': 57.67, 'Cheshta_Bala': 20.11, 'Naisargika_Bala': 51.4, 'Drik_Bala': -3.71, 'Total_Virupas': 423.65, 'Subha_Phala': 22.03, 'Asubha_Phala': 37.97, 'Ishta_Phala': 36.73, 'Kashta_Phala': 23.27},
        'Mars': {'Sthana_Bala': 275.76, 'Dig_Bala': 57.28, 'Kala_Bala': 91.8, 'Cheshta_Bala': 27.16, 'Naisargika_Bala': 17.1, 'Drik_Bala': -1.93, 'Total_Virupas': 467.17, 'Subha_Phala': 23.44, 'Asubha_Phala': 36.56, 'Ishta_Phala': 31.46, 'Kashta_Phala': 28.54},
        'Mercury': {'Sthana_Bala': 212.44, 'Dig_Bala': 49.14, 'Kala_Bala': 272.35, 'Cheshta_Bala': 55.03, 'Naisargika_Bala': 25.7, 'Drik_Bala': 17.86, 'Total_Virupas': 632.52, 'Subha_Phala': 18.75, 'Asubha_Phala': 41.25, 'Ishta_Phala': 43.73, 'Kashta_Phala': 16.27},
        'Jupiter': {'Sthana_Bala': 199.14, 'Dig_Bala': 29.83, 'Kala_Bala': 233.77, 'Cheshta_Bala': 19.84, 'Naisargika_Bala': 34.3, 'Drik_Bala': -7.44, 'Total_Virupas': 509.44, 'Subha_Phala': 11.25, 'Asubha_Phala': 48.75, 'Ishta_Phala': 26.99, 'Kashta_Phala': 33.01},
        'Venus': {'Sthana_Bala': 199.61, 'Dig_Bala': 29.78, 'Kala_Bala': 120.29, 'Cheshta_Bala': 35.01, 'Naisargika_Bala': 42.8, 'Drik_Bala': 50.17, 'Total_Virupas': 477.66, 'Subha_Phala': 22.5, 'Asubha_Phala': 37.5, 'Ishta_Phala': 27.31, 'Kashta_Phala': 32.69},
        'Saturn': {'Sthana_Bala': 224.13, 'Dig_Bala': 3.42, 'Kala_Bala': 60.64, 'Cheshta_Bala': 12.02, 'Naisargika_Bala': 8.6, 'Drik_Bala': 41.85, 'Total_Virupas': 350.66, 'Subha_Phala': 15.0, 'Asubha_Phala': 45.0, 'Ishta_Phala': 20.57, 'Kashta_Phala': 39.43}
    }
    
    for p, expected_vals in expected_shadbala.items():
        calc_vals = shadbala_data.get(p, {})
        for key, exp_val in expected_vals.items():
            calc_val = calc_vals.get(key, 0.0)
            assert abs(exp_val - calc_val) <= 0.5, f"{p} {key} mismatch: Expected {exp_val}, Got {calc_val}"
