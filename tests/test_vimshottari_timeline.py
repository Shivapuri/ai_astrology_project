"""
Tests for Vimshottari Dasha Full Cycle Timeline (Phase 5).

Verifies all 9 Mahadashas and all 81 Antardashas across the 120-year cycle
against Ernst Wilhelm's Kala software ground-truth dataset:
'source-material/software-setup/sample-case/angelina_jolie_vimshottari_antardasas.csv'.
"""

import os
import csv
import pytest
import swisseph as swe
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.dashas.vimshottari import (
    calculate_vimshottari_timeline,
    DASHA_LORDS,
    DASHA_YEARS,
    SAURA_YEAR_DAYS,
    VIMSHOTTARI_CYCLE_YEARS
)

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "source-material", "software-setup", "sample-case", "angelina_jolie_vimshottari_antardasas.csv"
)

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

def test_mahadasha_order_and_years():
    """Verifies standard BPHS 120-year planetary allocations."""
    assert sum(DASHA_YEARS.values()) == VIMSHOTTARI_CYCLE_YEARS
    assert len(DASHA_LORDS) == 9
    expected_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    assert DASHA_LORDS == expected_order
    assert DASHA_YEARS["Sun"] == 6
    assert DASHA_YEARS["Moon"] == 10
    assert DASHA_YEARS["Mars"] == 7
    assert DASHA_YEARS["Rahu"] == 18
    assert DASHA_YEARS["Jupiter"] == 16
    assert DASHA_YEARS["Saturn"] == 19
    assert DASHA_YEARS["Mercury"] == 17
    assert DASHA_YEARS["Ketu"] == 7
    assert DASHA_YEARS["Venus"] == 20

def test_mahadasha_timeline_structure(aj_chart):
    """Verifies that the chart returns the full 9 Mahadashas with correct sequence."""
    dasha_data = aj_chart["vimshottari_dasha"]
    assert "at_birth" in dasha_data
    assert "mahadashas" in dasha_data
    assert "antardashas" in dasha_data

    assert dasha_data["at_birth"]["mahadasha"] == "Mercury"
    assert 11.30 <= dasha_data["at_birth"]["mahadasha_balance_years"] <= 11.33

    mahadashas = dasha_data["mahadashas"]
    assert len(mahadashas) == 9

    expected_sequence = ["Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn"]
    for i, md in enumerate(mahadashas):
        assert md["planet"] == expected_sequence[i]
        assert md["lord"] == expected_sequence[i]
        assert len(md["antardashas"]) == 9

def test_all_81_antardashas_csv_alignment(aj_chart):
    """
    Asserts all 81 Antardashas against the Kala ground-truth CSV dataset.
    
    Verifies:
    1. Period code and ruler names match exactly for all 81 rows.
    2. Start dates match Kala within <= 0.06 days (under 1.5 hours) dynamically.
    3. >= 95% of dates match on the exact same day dynamically.
    4. 100% of dates match on the exact same day when aligned from the Me/Me anchor,
       with start time matching within 1 minute.
    """
    dasha_data = aj_chart["vimshottari_dasha"]
    calc_antardashas = dasha_data["antardashas"]
    assert len(calc_antardashas) == 81, "Must contain all 81 Antardashas across the cycle"

    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        ground_truth = list(reader)

    assert len(ground_truth) == 81, f"Expected 81 rows in CSV, found {len(ground_truth)}"

    exact_day_matches = 0
    max_day_diff = 0.0

    for i, exp in enumerate(ground_truth):
        calc = calc_antardashas[i]

        # Period & Ruler check
        assert calc["period"] == exp["Period"], f"Row {i}: Period mismatch"
        assert calc["mahadasha_lord"][:2] == exp["MahaDasa_Lord"], f"Row {i}: MD Lord mismatch"
        assert calc["antardasha_lord"][:2] == exp["AntarDasa_Lord"], f"Row {i}: AD Lord mismatch"

        # Compare Julian Day difference
        exp_m, exp_d, exp_y = [int(x) for x in exp["Start_Date"].split("/")]
        exp_hh, exp_mm = [int(x) for x in exp["Start_Time"].split(":")]
        exp_jd = swe.julday(exp_y, exp_m, exp_d, exp_hh + exp_mm / 60.0, swe.GREG_CAL)

        diff_days = abs(calc["start_jd"] - exp_jd)
        if diff_days > max_day_diff:
            max_day_diff = diff_days

        # Dynamic date matching
        if calc["start_date_us"] == exp["Start_Date"]:
            exact_day_matches += 1

        # Proportional duration check: (MahaYears * AntarYears / 120) * 365.2422
        m_years = DASHA_YEARS[calc["mahadasha_lord"]]
        a_years = DASHA_YEARS[calc["antardasha_lord"]]
        expected_dur = (m_years * a_years / 120.0) * SAURA_YEAR_DAYS
        assert abs(calc["duration_days"] - expected_dur) <= 0.01, (
            f"Row {i} ({calc['period']}): duration {calc['duration_days']} != {expected_dur}"
        )

    # Statistical assertions across the 120-year cycle
    assert max_day_diff <= 0.06, f"Max day difference across 81 Antardashas too large: {max_day_diff} days"
    assert exact_day_matches >= 76, f"Only {exact_day_matches}/81 matched exact day (expected >= 76 / 95%)"

def test_antardasha_anchor_propagation_precision():
    """
    Verifies that when traced from the Me/Me anchor (09/26/1969 00:03),
    every single one of the 81 Antardashas matches Kala's start time to within 1 minute.
    """
    first_jd = swe.julday(1969, 9, 26, 0 + 3 / 60.0, swe.GREG_CAL)
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        ground_truth = list(csv.DictReader(f))

    current_jd = first_jd
    lord_idx = 8 # Mercury

    row_idx = 0
    for m_offset in range(9):
        m_idx = (lord_idx + m_offset) % 9
        m_lord = DASHA_LORDS[m_idx]
        m_years = DASHA_YEARS[m_lord]

        for a_offset in range(9):
            a_idx = (m_idx + a_offset) % 9
            a_lord = DASHA_LORDS[a_idx]
            a_years = DASHA_YEARS[a_lord]

            exp = ground_truth[row_idx]
            exp_m, exp_d, exp_y = [int(x) for x in exp["Start_Date"].split("/")]
            exp_hh, exp_mm = [int(x) for x in exp["Start_Time"].split(":")]
            exp_jd = swe.julday(exp_y, exp_m, exp_d, exp_hh + exp_mm / 60.0, swe.GREG_CAL)

            # Difference in minutes
            diff_mins = abs(current_jd - exp_jd) * 1440.0
            assert diff_mins <= 1.0, (
                f"Row {row_idx} ({exp['Period']}): time difference {diff_mins:.2f} mins exceeds 1 minute"
            )

            # Format date check
            y, m, d, _ = swe.revjul(current_jd, swe.GREG_CAL)
            calc_date_us = f"{m:02d}/{d:02d}/{y:04d}"
            assert calc_date_us == exp["Start_Date"], (
                f"Row {row_idx} ({exp['Period']}): date {calc_date_us} != expected {exp['Start_Date']}"
            )

            dur = (m_years * a_years / 120.0) * SAURA_YEAR_DAYS
            current_jd += dur
            row_idx += 1
