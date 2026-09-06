"""
Unit and regression tests for Varga Vimshopaka Engine (Ernst Wilhelm's Kala Methodology).
Validates 20-point Vimshopaka dignity scoring across Shadvarga, Saptavarga, Dasavarga,
and Shodashavarga, as well as Vaisheshikamsa honorific classifications against:
angelina_jolie_varga_vimshopaka.csv and angelina_jolie_varga_vimshopaka.pdf.
"""

import csv
import pytest
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.vimshopaka import (
    calculate_varga_vimshopaka_engine,
    SCHEME_WEIGHTS,
    DIGNITY_POINTS,
    VAISHESHIKAMSA_HONORIFICS
)

DOB_YEAR = 1975
DOB_MONTH = 6
DOB_DAY = 4
DOB_HOUR = 9
DOB_MINUTE = 9
LAT = 34.0522
LON = -118.2437
TZ = -7.0

CSV_PATH = 'source-material/software-setup/sample-case/angelina_jolie_varga_vimshopaka.csv'


@pytest.fixture(scope='module')
def aj_chart():
    return generate_kala_chart(
        name='Angelina Jolie',
        year=DOB_YEAR, month=DOB_MONTH, day=DOB_DAY,
        hour=DOB_HOUR, minute=DOB_MINUTE,
        latitude=LAT, longitude=LON, timezone_offset=TZ
    )


@pytest.fixture(scope='module')
def baseline_vimshopaka():
    scores = {}
    honorifics = {}
    planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']

    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row:
                continue
            key = row[0]
            if key.startswith('Vaisheshikamsa_'):
                scheme = key.replace('Vaisheshikamsa_', '')
                honorifics[scheme] = {planets[i]: row[i+1] for i in range(7)}
            else:
                scores[key] = {planets[i]: float(row[i+1]) for i in range(7)}

    return {'scores': scores, 'honorifics': honorifics}


def test_varga_vimshopaka_scores(aj_chart, baseline_vimshopaka):
    """Verifies all 28 Vimshopaka scores across all 4 Parashari schemes matching baseline within 0.02."""
    v_data = aj_chart['varga_vimshopaka']
    calc_scores = v_data['scores']
    exp_scores = baseline_vimshopaka['scores']

    for scheme in ['Shadvarga', 'Saptavarga', 'Dasavarga', 'Shodasavarga']:
        assert scheme in calc_scores, f'Scheme {scheme} missing from calculated scores'
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            calc = calc_scores[scheme][planet]
            exp = exp_scores[scheme][planet]
            assert abs(calc - exp) <= 0.02, (
                f'Vimshopaka score mismatch in {scheme} for {planet}: calc={calc}, exp={exp}'
            )


def test_vaisheshikamsa_honorifics(aj_chart, baseline_vimshopaka):
    """Verifies all 28 Vaisheshikamsa honorific classifications matching Kala baseline."""
    v_data = aj_chart['varga_vimshopaka']
    calc_vaisheshikamsa = v_data['vaisheshikamsa']
    exp_honorifics = baseline_vimshopaka['honorifics']

    for scheme in ['Shadvarga', 'Saptavarga', 'Dasavarga', 'Shodasavarga']:
        assert scheme in calc_vaisheshikamsa, f'Scheme {scheme} missing from calculated Vaisheshikamsa'
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            calc = calc_vaisheshikamsa[scheme][planet]['honorific']
            exp = exp_honorifics[scheme][planet]
            assert calc == exp, (
                f'Vaisheshikamsa mismatch in {scheme} for {planet}: calc={calc}, exp={exp}'
            )


def test_scheme_weights_integrity():
    """Verifies that all Parashari scheme weights sum to exactly 20.0 points."""
    for scheme, weights in SCHEME_WEIGHTS.items():
        total_w = sum(weights.values())
        assert abs(total_w - 20.0) < 1e-9, f'Scheme {scheme} weights sum to {total_w}, expected 20.0'
