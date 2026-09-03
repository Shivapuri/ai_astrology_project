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
    
    # Ground truth values directly from Kala Vedic Astrology Software (Tables -> Shad Bala)
    expected_shadbala = {
        'Sun': {
            'Sthana_Bala': 145.9, 'Dig_Bala': 43.44, 'Kala_Bala': 81.4, 'Ayana_Bala': 57.79,
            'Cheshta_Bala': 57.79, 'Naisargika_Bala': 60.0, 'Drik_Bala': 4.4, 'Total_Virupas': 450.6,
            'Total_Rupas': 7.51, 'Relative_Rank': 5,
            'Subha_Phala': 6.56, 'Asubha_Phala': 53.44, 'Ishta_Phala': 48.44, 'Kashta_Phala': 11.56
        },
        'Moon': {
            'Sthana_Bala': 251.4, 'Dig_Bala': 2.18, 'Kala_Bala': 38.6, 'Ayana_Bala': 23.46,
            'Cheshta_Bala': 20.11, 'Naisargika_Bala': 51.43, 'Drik_Bala': -3.7, 'Total_Virupas': 383.5,
            'Total_Rupas': 6.39, 'Relative_Rank': 6,
            'Subha_Phala': 22.03, 'Asubha_Phala': 37.97, 'Ishta_Phala': 36.73, 'Kashta_Phala': 23.27
        },
        'Mars': {
            'Sthana_Bala': 260.8, 'Dig_Bala': 57.67, 'Kala_Bala': 58.4, 'Ayana_Bala': 35.35,
            'Cheshta_Bala': 27.22, 'Naisargika_Bala': 17.14, 'Drik_Bala': -1.9, 'Total_Virupas': 454.6,
            'Total_Rupas': 7.58, 'Relative_Rank': 4,
            'Subha_Phala': 23.44, 'Asubha_Phala': 36.56, 'Ishta_Phala': 31.46, 'Kashta_Phala': 28.54
        },
        'Mercury': {
            'Sthana_Bala': 197.4, 'Dig_Bala': 49.28, 'Kala_Bala': 245.1, 'Ayana_Bala': 58.98,
            'Cheshta_Bala': 56.22, 'Naisargika_Bala': 25.71, 'Drik_Bala': 5.7, 'Total_Virupas': 638.5,
            'Total_Rupas': 10.64, 'Relative_Rank': 1,
            'Subha_Phala': 18.75, 'Asubha_Phala': 41.25, 'Ishta_Phala': 43.73, 'Kashta_Phala': 16.27
        },
        'Jupiter': {
            'Sthana_Bala': 199.1, 'Dig_Bala': 30.01, 'Kala_Bala': 151.6, 'Ayana_Bala': 38.71,
            'Cheshta_Bala': 19.90, 'Naisargika_Bala': 34.29, 'Drik_Bala': -7.4, 'Total_Virupas': 466.2,
            'Total_Rupas': 7.77, 'Relative_Rank': 3,
            'Subha_Phala': 11.25, 'Asubha_Phala': 48.75, 'Ishta_Phala': 26.99, 'Kashta_Phala': 33.01
        },
        'Venus': {
            'Sthana_Bala': 204.6, 'Dig_Bala': 29.36, 'Kala_Bala': 76.6, 'Ayana_Bala': 56.25,
            'Cheshta_Bala': 35.10, 'Naisargika_Bala': 42.86, 'Drik_Bala': 31.4, 'Total_Virupas': 476.2,
            'Total_Rupas': 7.94, 'Relative_Rank': 2,
            'Subha_Phala': 22.5, 'Asubha_Phala': 37.5, 'Ishta_Phala': 27.31, 'Kashta_Phala': 32.69
        },
        'Saturn': {
            'Sthana_Bala': 239.1, 'Dig_Bala': 3.68, 'Kala_Bala': 58.4, 'Ayana_Bala': 2.32,
            'Cheshta_Bala': 11.97, 'Naisargika_Bala': 8.57, 'Drik_Bala': 20.4, 'Total_Virupas': 344.5,
            'Total_Rupas': 5.74, 'Relative_Rank': 7,
            'Subha_Phala': 15.0, 'Asubha_Phala': 45.0, 'Ishta_Phala': 20.57, 'Kashta_Phala': 39.43
        }
    }
    
    for p, expected_vals in expected_shadbala.items():
        calc_vals = shadbala_data.get(p, {})
        for key, exp_val in expected_vals.items():
            calc_val = calc_vals.get(key, 0.0)
            tol = 1.5 if key in ['Cheshta_Bala', 'Total_Virupas', 'Total_Rupas'] else 0.5
            assert abs(exp_val - calc_val) <= tol, f"{p} {key} mismatch: Expected {exp_val}, Got {calc_val}"

def test_shadbala_benchmarks_and_ranks():
    chart = generate_kala_chart(
        name="Angelina Jolie", year=1975, month=6, day=4,
        hour=9, minute=9, latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )
    sb = chart.get('shadbala', {})
    
    # Expected relative ranks (1 to 7) matching Kala software
    expected_ranks = {
        'Mercury': 1,
        'Venus': 2,
        'Jupiter': 3,
        'Mars': 4,
        'Sun': 5,
        'Moon': 6,
        'Saturn': 7
    }
    
    for planet, exp_rank in expected_ranks.items():
        assert planet in sb, f"Planet {planet} missing from Shadbala!"
        calc_rank = sb[planet].get('Relative_Rank')
        assert calc_rank == exp_rank, f"Rank mismatch for {planet}: Expected #{exp_rank}, got #{calc_rank}"
        
        # Verify required threshold values
        assert sb[planet]['Required_Total'] in [300.0, 330.0, 360.0, 390.0, 420.0]
        assert sb[planet]['Pct_Required_Total'] > 100.0, f"{planet} percentage should be over 100% in Angelina Jolie chart"
