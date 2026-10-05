"""
tests/test_core_engine_lock.py
=============================================================================
ASTRA CORE CALCULUS - GOLDEN MASTER REGRESSION TRIPWIRE (HEMISPHERE A)
=============================================================================
Freezes Stage 1 through Stage 3 foundational calculation engines against
unauthorized modifications or algorithmic regressions.

Certified against standard benchmark:
Subject: Angelina Jolie
Date: June 4, 1975, 09:09 PDT (16:09 UTC)
Location: Los Angeles, CA (34°03'08" N, 118°14'37" W)
Settings: Tropical Zodiac, Campanus Cusps, Dhruva Galactic Center
=============================================================================
"""

import pytest
from jyotish.baseline import ChartBaseline
from jyotish.relationships.relationships import calculate_chart_dignities
from jyotish.aspects.aspects import calculate_aspect_matrices
from jyotish.shadbala.shadbala import calculate_shadbala
from jyotish.bhavas.bhava_bala import calculate_bhava_bala
from jyotish.pipeline import ChartPipeline


@pytest.fixture(scope="module")
def jolie_baseline():
    """Certified Angelina Jolie astronomical baseline."""
    return ChartBaseline(
        name="Angelina Jolie",
        year=1975,
        month=6,
        day=4,
        hour=9,
        minute=9,
        second=0,
        latitude=34.0522,
        longitude=-118.2437,
        timezone_offset=-7.0
    )


def test_core_lock_shadbala(jolie_baseline):
    """
    Tripwire 1: Ṣaḍbala Total Virūpas for Sun and Moon.
    Asserts exact values within ±0.1 Virūpa.
    """
    dignities = calculate_chart_dignities(jolie_baseline)
    aspect_matrices = calculate_aspect_matrices(jolie_baseline)
    sb = calculate_shadbala(
        jolie_baseline,
        dignities=dignities,
        aspect_matrices=aspect_matrices,
        dig_bala_mode="campanus"
    )

    # Sun Ṣaḍbala Total
    sun_virupas = sb["Sun"]["Total_Virupas"]
    assert abs(sun_virupas - 450.7) <= 0.1, (
        f"Core freeze violated: Sun Ṣaḍbala changed from 450.7 to {sun_virupas}"
    )

    # Moon Ṣaḍbala Total
    moon_virupas = sb["Moon"]["Total_Virupas"]
    assert abs(moon_virupas - 383.5) <= 0.1, (
        f"Core freeze violated: Moon Ṣaḍbala changed from 383.5 to {moon_virupas}"
    )


def test_core_lock_bhava_bala(jolie_baseline):
    """
    Tripwire 2: Bhāva Bala Total Virūpas for House 1 (Tanu) and House 10 (Karma).
    Asserts exact values within ±0.1 Virūpa.
    """
    dignities = calculate_chart_dignities(jolie_baseline)
    aspect_matrices = calculate_aspect_matrices(jolie_baseline)
    sb = calculate_shadbala(
        jolie_baseline,
        dignities=dignities,
        aspect_matrices=aspect_matrices,
        dig_bala_mode="campanus"
    )
    bb = calculate_bhava_bala(
        baseline=jolie_baseline,
        shadbala_results=sb,
        aspect_matrices=aspect_matrices
    )

    # House 1 Total Virūpas
    h1_virupas = bb[1]["total_virupas"]
    assert abs(h1_virupas - 488.12) <= 0.1, (
        f"Core freeze violated: House 1 Bhāva Bala changed from 488.12 to {h1_virupas}"
    )

    # House 10 Total Virūpas
    h10_virupas = bb[10]["total_virupas"]
    assert abs(h10_virupas - 509.01) <= 0.1, (
        f"Core freeze violated: House 10 Bhāva Bala changed from 509.01 to {h10_virupas}"
    )


def test_core_lock_graha_drishti(jolie_baseline):
    """
    Tripwire 3: Continuous 0–60 Virūpa Graha Dṛṣṭi rays for major aspects.
    Asserts exact values within ±0.1 Virūpa.
    """
    aspect_matrices = calculate_aspect_matrices(jolie_baseline)
    outgoing = aspect_matrices["graha_drishti"]["outgoing"]

    # Mars -> Sun (Aries to Gemini: ~62.71° separation, 4th house quadrant aspect)
    mars_to_sun = outgoing["Mars"]["Sun"]
    assert abs(mars_to_sun - 19.0724) <= 0.1, (
        f"Core freeze violated: Mars -> Sun aspect changed from 19.0724 to {mars_to_sun}"
    )

    # Jupiter -> Lagna (Aries to Cancer: ~104.83° separation, 4th/5th special trikona ramp)
    jupiter_to_lagna = outgoing["Jupiter"]["Lagna"]
    assert abs(jupiter_to_lagna - 50.7344) <= 0.1, (
        f"Core freeze violated: Jupiter -> Lagna aspect changed from 50.7344 to {jupiter_to_lagna}"
    )


def test_core_lock_relationships_and_dignities(jolie_baseline):
    """
    Tripwire 4: Pañcadhā Maitrī (Compound Friendship) and D1 Dignities.
    """
    dignities = calculate_chart_dignities(jolie_baseline)
    comp_rel = dignities["compound_relationships"]
    v_dig = dignities["varga_dignities"]["D1"]

    # Sun in Gemini: Host lord Mercury. Natural: Neutral. Temporary: Enemy. Compound: Enemy.
    assert comp_rel["Sun"]["Mercury"] == "Enemy", (
        f"Core freeze violated: Sun-Mercury compound relationship is {comp_rel['Sun']['Mercury']}, expected Enemy"
    )
    assert v_dig["Sun"]["dignity"] == "Enemy's Sign", (
        f"Core freeze violated: Sun D1 dignity is {v_dig['Sun']['dignity']}, expected Enemy's Sign"
    )

    # Mars in Aries (10°42'): Moolatrikona sign (0°-12°). Dignity: Moolatrikona.
    assert v_dig["Mars"]["dignity"] == "Moolatrikona", (
        f"Core freeze violated: Mars D1 dignity is {v_dig['Mars']['dignity']}, expected Moolatrikona"
    )

    # Sun natural to Mars: Friend. Temporary: Friend (11th house). Compound: Great Friend.
    assert comp_rel["Sun"]["Mars"] == "Great Friend", (
        f"Core freeze violated: Sun-Mars compound relationship is {comp_rel['Sun']['Mars']}, expected Great Friend"
    )


def test_core_lock_pipeline_integration():
    """
    Tripwire 5: ChartPipeline integration verifies all frozen modules pass
    cleanly into the master pipeline without schema breakage or duplicate loops.
    """
    pipeline = ChartPipeline(
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

    # Verify both modern and backward-compatible aspect payloads are exposed
    chart_dict = pipeline.to_dict()
    assert "aspect_matrices" in chart_dict
    assert "advanced_aspects" in chart_dict
    assert "dignities" in chart_dict
    assert "shadbala" in chart_dict
    assert "bhava_bala" in chart_dict

    # Verify pipeline properties match direct engine outputs
    assert abs(pipeline.shadbala["Sun"]["Total_Virupas"] - 450.7) <= 0.1
    assert abs(pipeline.bhava_bala[1]["total_virupas"] - 488.12) <= 0.1
    assert abs(pipeline.aspect_matrices["graha_drishti"]["outgoing"]["Mars"]["Sun"] - 19.0724) <= 0.1
    assert pipeline.dignities["varga_dignities"]["D1"]["Sun"]["dignity"] == "Enemy's Sign"
