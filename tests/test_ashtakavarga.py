"""
Unit and regression tests for Ashtakavarga Engine (Ernst Wilhelm's Kala Methodology).
Validates BAV, SAV, Trikona Shodhana, Ekadhipatya Shodhana, and Shodhya Pindas
against Kala's baseline dataset: angelina_jolie_ashtakavarga_sarva.csv.
"""

import csv
import pytest
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.ashtakavarga import (
    calculate_bav,
    trikona_shodhana,
    ekadhipatya_shodhana,
    calculate_sarva_shodhana,
    calculate_sodhya_pindas,
    calculate_ashtakavarga_engine,
    ZODIAC_SIGNS
)

DOB_YEAR = 1975
DOB_MONTH = 6
DOB_DAY = 4
DOB_HOUR = 9
DOB_MINUTE = 9
LAT = 34.0522
LON = -118.2437
TZ = -7.0

CSV_PATH = 'source-material/software-setup/sample-case/angelina_jolie_ashtakavarga_sarva.csv'


@pytest.fixture(scope='module')
def aj_chart():
    return generate_kala_chart(
        name='Angelina Jolie',
        year=DOB_YEAR, month=DOB_MONTH, day=DOB_DAY,
        hour=DOB_HOUR, minute=DOB_MINUTE,
        latitude=LAT, longitude=LON, timezone_offset=TZ
    )


@pytest.fixture(scope='module')
def expected_sarva():
    data = {}
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # Contributor, Aries, ...
        for row in reader:
            if not row:
                continue
            name = row[0]
            vals = [int(v) for v in row[1:13]]
            data[name] = vals
    return data


def test_bhinna_ashtakavarga_grid(aj_chart, expected_sarva):
    """Verifies BAV bindus for all 7 planets and Lagna against Kala baseline."""
    av_data = aj_chart['ashtakavarga']
    bav = av_data['bav']

    for ent in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Lagna']:
        assert ent in bav, f'{ent} missing from calculated BAV'
        calc_bav = bav[ent]
        exp_bav = expected_sarva[ent]
        assert calc_bav == exp_bav, (
            f'BAV mismatch for {ent}: calc={calc_bav}, exp={exp_bav}'
        )


def test_sarvashtakavarga_total_and_points(aj_chart, expected_sarva):
    """Verifies Sarvashtakavarga total matches 337 points and exact 12 signs distribution."""
    av_data = aj_chart['ashtakavarga']
    sav = av_data['sarvashtakavarga']

    assert sav['total_points'] == 337, f'Expected 337 total points, got {sav["total_points"]}'
    assert sav['total_sav'] == expected_sarva['Total_SAV'], (
        f'SAV mismatch: calc={sav["total_sav"]}, exp={expected_sarva["Total_SAV"]}'
    )


def test_sarva_shodhana(aj_chart, expected_sarva):
    """Verifies Trikona and Ekadhipatya Shodhana on Sarvashtakavarga."""
    av_data = aj_chart['ashtakavarga']
    sav = av_data['sarvashtakavarga']

    assert sav['trikona_shodhana'] == expected_sarva['Trikona_Shodhana'], (
        f'SAV Trikona mismatch: calc={sav["trikona_shodhana"]}, exp={expected_sarva["Trikona_Shodhana"]}'
    )
    assert sav['ekadhipatya_shodhana'] == expected_sarva['Ekadhipatya_Shodhana'], (
        f'SAV Ekadhipatya mismatch: calc={sav["ekadhipatya_shodhana"]}, exp={expected_sarva["Ekadhipatya_Shodhana"]}'
    )


def test_individual_trikona_and_ekadhipatya(aj_chart):
    """Verifies individual Trikona and Ekadhipatya reductions against certified Kala tables."""
    av_data = aj_chart['ashtakavarga']
    trikona = av_data['trikona_shodhana']
    epatya = av_data['ekadhipatya_shodhana']

    # From angelina_jolie_ashtakavarga_tables.pdf:
    certified_tables = {
        'Sun': {
            'trikona': [2, 0, 0, 1, 0, 0, 0, 0, 2, 1, 2, 1],
            'epatya':  [2, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0]
        },
        'Moon': {
            'trikona': [3, 0, 0, 0, 0, 1, 1, 3, 2, 1, 0, 2],
            'epatya':  [3, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0]
        },
        'Mars': {
            'trikona': [3, 1, 0, 0, 0, 0, 2, 0, 0, 0, 3, 0],
            'epatya':  [3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 3, 0]
        },
        'Mercury': {
            'trikona': [3, 4, 0, 1, 2, 0, 5, 2, 0, 0, 7, 0],
            'epatya':  [3, 0, 0, 1, 2, 0, 1, 0, 0, 0, 7, 0]
        },
        'Jupiter': {
            'trikona': [2, 2, 0, 1, 0, 0, 1, 2, 1, 1, 1, 0],
            'epatya':  [2, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0]
        },
        'Venus': {
            'trikona': [2, 3, 0, 0, 2, 2, 2, 2, 0, 0, 5, 1],
            'epatya':  [2, 1, 0, 0, 2, 2, 0, 0, 0, 0, 5, 1]
        },
        'Saturn': {
            'trikona': [1, 1, 3, 0, 0, 3, 0, 0, 2, 0, 3, 2],
            'epatya':  [1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 3, 0]
        },
        'Lagna': {
            'trikona': [3, 0, 0, 1, 0, 4, 0, 0, 0, 0, 1, 1],
            'epatya':  [3, 0, 0, 1, 0, 4, 0, 0, 0, 0, 1, 1]
        }
    }

    for ent, exp in certified_tables.items():
        assert trikona[ent] == exp['trikona'], f'Trikona mismatch for {ent}'
        assert epatya[ent] == exp['epatya'], f'Ekadhipatya mismatch for {ent}'


def test_shodhya_pindas_calculation(aj_chart):
    """Verifies that Shodhya Pindas (Rasi Pinda, Graha Pinda, Yoga Pinda) calculate correctly."""
    av_data = aj_chart['ashtakavarga']
    pindas = av_data['sodhya_pindas']

    for p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        assert p in pindas, f'Pindas missing for {p}'
        p_data = pindas[p]
        assert p_data['rasi_pinda'] > 0
        assert p_data['graha_pinda'] >= 0
        assert p_data['yoga_pinda'] == p_data['rasi_pinda'] + p_data['graha_pinda']
