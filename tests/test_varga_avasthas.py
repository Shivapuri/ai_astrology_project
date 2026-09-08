import pytest
import csv
import os
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.avasthas.quantitative import (
    calculate_varga_lajjitadi_net_modifiers,
    SHADVARGA_CHARTS,
    SAPTAVARGA_CHARTS,
    DASAVARGA_CHARTS,
    SHODASHAVARGA_CHARTS,
    MERCURY_SEPARATED_CHARTS,
)
from jyotish.avasthas.shayana import get_varga_amsa_factor

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

PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
PLANETS_9 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

ALL_VARGAS = [
    "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
    "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"
]


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


def test_16_varga_lajjitadi_net_modifiers(aj_chart):
    """
    Validates all 16 divisional charts and 7 classical grahas against Kala baseline:
    angelina_jolie_lajjitadi_varga_net_modifiers.csv
    """
    csv_path = os.path.join(CSV_DIR, "angelina_jolie_lajjitadi_varga_net_modifiers.csv")
    assert os.path.exists(csv_path), f"Baseline CSV not found: {csv_path}"

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected = {row["Varga"]: {p: float(row[p]) for p in PLANETS_7} for row in reader}

    calculated = calculate_varga_lajjitadi_net_modifiers(aj_chart)
    context_modifiers = aj_chart.get("varga_lajjitadi_net_modifiers", {})

    for varga in ALL_VARGAS:
        assert varga in calculated, f"Varga {varga} missing from calculate_varga_lajjitadi_net_modifiers output"
        assert varga in context_modifiers, f"Varga {varga} missing from vedic_context['varga_lajjitadi_net_modifiers']"
        assert varga in expected, f"Varga {varga} missing from baseline CSV"

        for p in PLANETS_7:
            exp_val = expected[varga][p]
            calc_val = calculated[varga][p]
            ctx_val = context_modifiers[varga][p]

            assert abs(calc_val - exp_val) <= 0.1, (
                f"{varga} - {p}: expected {exp_val:.1f}, got {calc_val:.1f}"
            )
            assert abs(ctx_val - exp_val) <= 0.1, (
                f"{varga} - {p} in context: expected {exp_val:.1f}, got {ctx_val:.1f}"
            )


def test_mercury_conjunction_break_shift(aj_chart):
    """
    Validates the exact +60.0 shift when Mercury separates from the Sun in D3:
    - D1 (conjoined): -14.7
    - D3 (separated): +45.3 (+60.0 Kshobhita penalty removed)
    """
    calculated = calculate_varga_lajjitadi_net_modifiers(aj_chart)
    d1_merc = calculated["D1"]["Mercury"]
    d3_merc = calculated["D3"]["Mercury"]

    assert abs(d1_merc - (-14.7)) <= 0.1, f"D1 Mercury expected -14.7, got {d1_merc}"
    assert abs(d3_merc - 45.3) <= 0.1, f"D3 Mercury expected 45.3, got {d3_merc}"
    assert abs((d3_merc - d1_merc) - 60.0) <= 0.1, (
        f"Shift between D3 and D1 Mercury expected +60.0, got {d3_merc - d1_merc}"
    )


def test_parashari_varga_scheme_clustering(aj_chart):
    """
    Verifies that the 16 divisional charts adhere strictly to the 4 Parashari Varga schemes:
    1. Shadvarga (D1, D2, D3, D9, D12, D30)
    2. Saptavarga (D7)
    3. Dasavarga (D10, D16, D60)
    4. Shodashavarga (D4, D20, D24, D27, D40, D45)
    """
    calculated = calculate_varga_lajjitadi_net_modifiers(aj_chart)

    # Shadvarga baselines for Sun (18.0) and Mars (98.3)
    for v in ["D1", "D2", "D9", "D30"]:
        assert calculated[v]["Sun"] == 18.0
        assert calculated[v]["Mars"] == 98.3
        assert calculated[v]["Mercury"] == -14.7

    for v in ["D3", "D12"]:
        assert calculated[v]["Sun"] == 18.0
        assert calculated[v]["Mars"] == 98.3
        assert calculated[v]["Mercury"] == 45.3

    # Saptavarga (D7)
    assert calculated["D7"]["Sun"] == 21.6
    assert calculated["D7"]["Mars"] == 110.1

    # Dasavarga (D10, D16, D60)
    for v in ["D10", "D16", "D60"]:
        assert calculated[v]["Sun"] == 26.8
        assert calculated[v]["Mars"] == 103.3
        assert calculated[v]["Mercury"] == 42.1

    # Shodashavarga (D4, D20, D24, D27, D40, D45)
    for v in ["D4", "D20", "D24", "D27", "D40", "D45"]:
        assert calculated[v]["Sun"] == 27.3
        assert calculated[v]["Moon"] == 48.3
        assert calculated[v]["Mars"] == 97.6


def test_multi_varga_shayanadi_states(aj_chart):
    """
    Verifies that all 16 divisional charts have dynamic, populated Shayanadi activity states
    and Cheshtadi sub-states for all 9 planets (including Ketu).
    """
    vargas = aj_chart.get("vargas", {})
    assert len(vargas) == 16, f"Expected 16 vargas, got {len(vargas)}"

    distinct_states = set()

    for v_name in ALL_VARGAS:
        assert v_name in vargas, f"Varga {v_name} missing from chart context"
        grahas = vargas[v_name].get("grahas", {})

        for p in PLANETS_9:
            assert p in grahas, f"{p} missing in {v_name}"
            avasthas_dict = grahas[p].get("avasthas", {})
            assert "shayanadi" in avasthas_dict, f"Shayanadi missing for {p} in {v_name}"

            sh = avasthas_dict["shayanadi"]
            assert 1 <= sh["avastha_number"] <= 12, f"Invalid avastha number in {v_name} {p}"
            assert sh["state"], f"State label empty in {v_name} {p}"
            assert sh["sanskrit"], f"Sanskrit empty in {v_name} {p}"
            assert sh["sub_state_type"] in ("Drishti", "Cheshta", "Vicheshta"), (
                f"Invalid sub-state {sh['sub_state_type']} in {v_name} {p}"
            )
            assert sh["sub_state_multiplier"] in (0.10, 0.50, 1.00), (
                f"Invalid multiplier {sh['sub_state_multiplier']} in {v_name} {p}"
            )

            distinct_states.add((v_name, p, sh["avastha_number"], sh["sub_state_type"]))

    # Confirm that states are dynamic across vargas (not static duplicates of D1)
    d1_sun = vargas["D1"]["grahas"]["Sun"]["avasthas"]["shayanadi"]["avastha_number"]
    d2_sun = vargas["D2"]["grahas"]["Sun"]["avasthas"]["shayanadi"]["avastha_number"]
    d4_sun = vargas["D4"]["grahas"]["Sun"]["avasthas"]["shayanadi"]["avastha_number"]
    d60_sun = vargas["D60"]["grahas"]["Sun"]["avasthas"]["shayanadi"]["avastha_number"]

    sun_numbers = {d1_sun, d2_sun, d4_sun, d60_sun}
    assert len(sun_numbers) > 1, f"Sun states across vargas should vary dynamically, got: {sun_numbers}"


def test_varga_amsa_factor_bounds():
    """
    Verifies that get_varga_amsa_factor strictly produces integers between 1 and 4.
    """
    for harmonic in [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]:
        for deg in [0.0, 0.001, 7.5, 14.999, 15.0, 22.5, 29.999]:
            amsa = get_varga_amsa_factor(deg, harmonic)
            assert 1 <= amsa <= 4, f"Amsa factor {amsa} out of [1, 4] for deg={deg}, harmonic={harmonic}"


def test_swami_shivapuri_dynamic_varga_modifiers():
    """
    Verifies that calculate_varga_lajjitadi_net_modifiers produces dynamic, distinct,
    chart-specific results for a second chart (Swami Shivapuri) and does not mirror Angelina Jolie.
    """
    sp_chart = generate_kala_chart(
        name="Swami Shivapuri",
        year=1983,
        month=11,
        day=10,
        hour=22,
        minute=20,
        latitude=52.20296,
        longitude=8.0448,
        timezone_offset=1.0,
    )
    sp_modifiers = calculate_varga_lajjitadi_net_modifiers(sp_chart)
    assert len(sp_modifiers) == 16, f"Expected 16 vargas in modifiers, got {len(sp_modifiers)}"

    # Assert that Swami Shivapuri's modifiers are distinct from Angelina Jolie's baseline
    # E.g. AJ D1 Sun is 18.0, whereas Shivapuri D1 Sun should be ~38.1
    assert abs(sp_modifiers["D1"]["Sun"] - 38.1) <= 0.2, (
        f"Swami Shivapuri D1 Sun expected ~38.1, got {sp_modifiers['D1']['Sun']}"
    )
    assert sp_modifiers["D1"]["Sun"] != 18.0, "Shivapuri modifiers should not match hardcoded AJ baseline"

    # Verify D7 modifiers differ according to Saptavarga Vimshopaka
    assert abs(sp_modifiers["D7"]["Sun"] - 33.7) <= 0.2, (
        f"Swami Shivapuri D7 Sun expected ~33.7, got {sp_modifiers['D7']['Sun']}"
    )


def test_divisional_diagonal_starting_strength_not_frozen(aj_chart):
    """
    Verifies that divisional charts (e.g. D7 Saptamsa, D9 Navamsa) dynamically display
    the planet's Vimshopaka dignity on the diagonal rather than being frozen to D1 ShadBala.
    """
    matrices_aj = aj_chart.get("avastha_matrix", {})
    assert "D1" in matrices_aj and "D7" in matrices_aj and "D9" in matrices_aj

    # In D1, ShadBala diagonal is Rasi ShadBala virupas (~450.7 for Sun)
    d1_sun_base = matrices_aj["D1"]["ShadBala"]["Sun"]["Sun"]["base"]
    assert abs(d1_sun_base - 450.7) <= 0.5, f"D1 Sun ShadBala base expected ~450.7, got {d1_sun_base}"

    # In D7, diagonal base must be Saptavarga Vimshopaka dignity (9.1), NOT 450.7!
    d7_sun_base = matrices_aj["D7"]["ShadBala"]["Sun"]["Sun"]["base"]
    assert abs(d7_sun_base - 9.1) <= 0.2, f"D7 Sun base expected 9.1 (Vimsho.), got {d7_sun_base}"
    assert d7_sun_base != d1_sun_base, "D7 diagonal base must not be frozen to D1 ShadBala!"

    # In D9, diagonal base must be Shadvarga Vimshopaka dignity (7.6), NOT 450.7!
    d9_sun_base = matrices_aj["D9"]["ShadBala"]["Sun"]["Sun"]["base"]
    assert abs(d9_sun_base - 7.6) <= 0.2, f"D9 Sun base expected 7.6 (Vimsho.), got {d9_sun_base}"
    assert d9_sun_base != d1_sun_base, "D9 diagonal base must not be frozen to D1 ShadBala!"

    # Verify Vimshopaka baseline mode is available in avastha_matrices
    assert "Vimshopaka" in matrices_aj["D1"], "Vimshopaka mode missing from D1 avastha_matrix"
    assert "Vimshopaka" in matrices_aj["D7"], "Vimshopaka mode missing from D7 avastha_matrix"
    assert matrices_aj["D1"]["Vimshopaka"]["Sun"]["Sun"]["base"] == 7.6
    assert matrices_aj["D7"]["Vimshopaka"]["Sun"]["Sun"]["base"] == 9.1

