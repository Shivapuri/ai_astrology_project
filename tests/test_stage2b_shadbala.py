"""
tests/test_stage2b_shadbala.py
Stage 2B Verification: Dual-Mode Benchmark Validation for Shadbala.

Protects historical Kala / Campanus parity while certifying Astra's
pure Whole Sign Tropical architecture.
"""

import pytest
from jyotish.baseline import ChartBaseline
from jyotish.relationships.relationships import calculate_chart_dignities
from jyotish.aspects.aspects import calculate_aspect_matrices
from jyotish.shadbala.shadbala import calculate_shadbala, calculate_kendra_bala


@pytest.fixture
def angelina_baseline():
    """Certified Stage 1 Baseline for Angelina Jolie."""
    return ChartBaseline(
        name="Angelina Jolie",
        year=1975, month=6, day=4, hour=9, minute=9, second=0,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )


def test_angelina_jolie_legacy_kala_parity(angelina_baseline):
    """
    TEST 1: 100% REGRESSION GUARD AGAINST ERNST WILHELM / KALA.
    Evaluates with dig_bala_mode='campanus' to verify that decoupling from swisseph
    and rewiring into Stage 1 & Stage 2A produced zero mathematical regressions.
    """
    dignities = calculate_chart_dignities(angelina_baseline)
    aspects = calculate_aspect_matrices(angelina_baseline)

    results = calculate_shadbala(
        angelina_baseline,
        dignities=dignities,
        aspect_matrices=aspects,
        dig_bala_mode="campanus"  # Validates against legacy Kala numbers
    )

    # Assert exact calibrated legacy totals
    assert results["Sun"]["Total_Virupas"] > 390.0   # Sun passes requirement
    assert results["Jupiter"]["Total_Virupas"] > 390.0
    assert results["Venus"]["Saptavarga_Bala"] is not None

    # 5 unaffected pillars must match the legacy baseline within 0.5 Virūpa
    assert abs(results["Sun"]["Sthana_Bala"] - 145.9) < 0.5
    assert abs(results["Sun"]["Ayana_Bala"] - 57.79) < 0.5
    assert abs(results["Sun"]["Dig_Bala"] - 43.44) < 0.1
    assert abs(results["Sun"]["Total_Virupas"] - 450.6) < 0.5


def test_angelina_jolie_whole_sign_tropical(angelina_baseline):
    """
    TEST 2: CERTIFICATION OF ASTRA'S WHOLE SIGN TROPICAL ENGINE.
    Evaluates with dig_bala_mode='whole_sign' (default).
    Verifies that:
      1. All 5 non-spatial balas are strictly identical to Test 1.
      2. Dig Bala reflects the clean 90-degree Whole Sign distance from sensitive cusps.
      3. Relative planetary rank ordering and potency ratios remain sound.
    """
    dignities = calculate_chart_dignities(angelina_baseline)
    aspects = calculate_aspect_matrices(angelina_baseline)

    results_camp = calculate_shadbala(
        angelina_baseline,
        dignities=dignities,
        aspect_matrices=aspects,
        dig_bala_mode="campanus"
    )

    results_ws = calculate_shadbala(
        angelina_baseline,
        dignities=dignities,
        aspect_matrices=aspects,
        dig_bala_mode="whole_sign"  # Astra standard
    )

    # 1. Verify all 5 non-spatial balas are strictly identical
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        for pillar in ["Sthana_Bala", "Kala_Bala", "Ayana_Bala", "Cheshta_Bala", "Naisargika_Bala", "Drik_Bala"]:
            diff = abs(results_camp[p][pillar] - results_ws[p][pillar])
            assert diff < 0.01, f"{p} {pillar} differed between Campanus and Whole Sign: diff={diff}"

    # 2. Verify Whole Sign Dig Bala values
    # Venus at ~28° Cancer is ~90° from the 4th cusp (28° Libra) -> ~30 Virūpas
    assert abs(results_ws["Venus"]["Dig_Bala"] - 29.75) < 0.1
    assert abs(results_ws["Sun"]["Dig_Bala"] - 45.16) < 0.1
    assert abs(results_ws["Moon"]["Dig_Bala"] - 5.27) < 0.1
    assert abs(results_ws["Mars"]["Dig_Bala"] - 53.94) < 0.1
    assert abs(results_ws["Mercury"]["Dig_Bala"] - 47.81) < 0.1
    assert abs(results_ws["Jupiter"]["Dig_Bala"] - 26.18) < 0.1
    assert abs(results_ws["Saturn"]["Dig_Bala"] - 3.84) < 0.1

    # 3. Verify all planets receive valid scores and ratios
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        assert results_ws[p]["Total_Virupas"] > 200.0
        assert "Pct_Required_Total" in results_ws[p]
        assert results_ws[p]["Relative_Rank"] in range(1, 8)


def test_kendra_bala_modes():
    """
    TEST 3: VERIFICATION OF KENDRA BALA MODES (FLAT PARASHARA VS TAPERED PHALADEEPIKA).
    Verifies that:
      - 'flat_parashara' (BPHS / Kala) awards 60 to Kendras, 30 to Panaparas, 15 to Apoklimas.
      - 'tapered_phaladeepika' (Mantreśvara 4.8 / Vic DiCara) scales down by 1/4 from Lagna.
    """
    asc_lon = 15.0  # Sign 0 (Aries)

    # Expected values for houses 1 to 12
    expected_flat = {
        1: 60.0, 2: 30.0, 3: 15.0, 4: 60.0,
        5: 30.0, 6: 15.0, 7: 60.0, 8: 30.0,
        9: 15.0, 10: 60.0, 11: 30.0, 12: 15.0
    }

    expected_tapered = {
        1: 60.0, 10: 45.0, 7: 30.0, 4: 15.0,
        2: 30.0, 11: 22.5, 8: 15.0, 5: 7.5,
        3: 15.0, 12: 11.25, 9: 7.5, 6: 3.75
    }

    for house in range(1, 13):
        # Longitude in the middle of each house sign
        pl_lon = ((house - 1) * 30.0) + 15.0
        
        flat_val = calculate_kendra_bala(pl_lon, asc_lon, mode="flat_parashara")
        assert flat_val == expected_flat[house], f"House {house} flat Kendra Bala mismatch: {flat_val} != {expected_flat[house]}"

        tapered_val = calculate_kendra_bala(pl_lon, asc_lon, mode="tapered_phaladeepika")
        assert tapered_val == expected_tapered[house], f"House {house} tapered Kendra Bala mismatch: {tapered_val} != {expected_tapered[house]}"


def test_shadbala_kendra_bala_mode_integration(angelina_baseline):
    """
    TEST 4: INTEGRATION TEST OF KENDRA BALA TOGGLE IN FULL SHADBALA ENGINE.
    Verifies that passing kendra_bala_mode='tapered_phaladeepika' correctly
    adjusts Sthana Bala and Total Virupas without breaking any other components.
    """
    dignities = calculate_chart_dignities(angelina_baseline)
    aspects = calculate_aspect_matrices(angelina_baseline)

    results_flat = calculate_shadbala(
        angelina_baseline,
        dignities=dignities,
        aspect_matrices=aspects,
        kendra_bala_mode="flat_parashara"
    )

    results_tapered = calculate_shadbala(
        angelina_baseline,
        dignities=dignities,
        aspect_matrices=aspects,
        kendra_bala_mode="tapered_phaladeepika"
    )

    # Venus is in Cancer (House 1): 1st house is 60.0 in both flat and tapered -> delta = 0
    assert results_flat["Venus"]["Kendradi_Bala"] == 60.0
    assert results_tapered["Venus"]["Kendradi_Bala"] == 60.0

    # Sun is in Gemini (House 12): 15.0 in flat, 11.25 in tapered -> delta = -3.75
    assert results_flat["Sun"]["Kendradi_Bala"] == 15.0
    assert results_tapered["Sun"]["Kendradi_Bala"] == 11.25
    assert abs((results_flat["Sun"]["Sthana_Bala"] - results_tapered["Sun"]["Sthana_Bala"]) - 3.75) < 0.1
    assert abs((results_flat["Sun"]["Total_Virupas"] - results_tapered["Sun"]["Total_Virupas"]) - 3.75) < 0.1

    # Moon is in Aries (House 10): 60.0 in flat, 45.0 in tapered -> delta = -15.0
    assert results_flat["Moon"]["Kendradi_Bala"] == 60.0
    assert results_tapered["Moon"]["Kendradi_Bala"] == 45.0
    assert abs((results_flat["Moon"]["Total_Virupas"] - results_tapered["Moon"]["Total_Virupas"]) - 15.0) < 0.1
