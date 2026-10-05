"""
tests/test_stage3_bhavas.py
Certification test suite for Astra Stage 3: Bhāva Bala & House Capacity.
Verifies pure DAG consumption across Stages 1 -> 2A -> 2B -> 3 with zero ephemeris calls.
"""

import pytest
from jyotish.baseline import ChartBaseline
from jyotish.relationships.relationships import calculate_chart_dignities
from jyotish.aspects.aspects import calculate_aspect_matrices
from jyotish.shadbala.shadbala import calculate_shadbala
from jyotish.bhavas.bhava_bala import (
    calculate_bhava_bala,
    calculate_bhava_dig_bala,
    calculate_bhava_drishti_bala,
    calculate_harsha_bala,
    calculate_house_atmosphere,
    generate_master_diagnostic_payload,
    get_sign_genus,
    SIGNS,
    SIGN_LORDS,
    ZERO_HOUSES,
    MASTER_DIAGNOSTIC_COLUMNS,
)


@pytest.fixture
def jolie_baseline():
    """Certified Angelina Jolie benchmark baseline container."""
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
        timezone_offset=-7.0,
        d10_mode="reverse",
        d24_mode="reverse"
    )


def test_stage3_full_dag_pipeline(jolie_baseline):
    """
    Certifies that Stage 3 seamlessly ingests Stage 1, Stage 2A, and Stage 2B outputs
    in a clean, deterministic DAG sequence.
    """
    # Stage 2A
    dignities = calculate_chart_dignities(jolie_baseline)
    aspects = calculate_aspect_matrices(jolie_baseline)

    # Stage 2B
    shadbala = calculate_shadbala(
        jolie_baseline,
        dignities=dignities,
        aspect_matrices=aspects
    )

    # Stage 3
    bhavas = calculate_bhava_bala(
        baseline=jolie_baseline,
        shadbala_results=shadbala,
        aspect_matrices=aspects
    )

    # 1. Structure Verification
    assert isinstance(bhavas, dict)
    assert len(bhavas) == 12

    for h in range(1, 13):
        assert h in bhavas
        b = bhavas[h]

        # 2. Check 3 Quantitative Pillars
        assert "bhavadhipathi_bala" in b
        assert "bhava_digbala" in b
        assert "bhava_drishti_bala" in b
        assert "total_virupas" in b
        assert "total_rupas" in b

        # Total Virupas must exactly match the sum of the 3 pillars
        expected_total = round(b["bhavadhipathi_bala"] + b["bhava_digbala"] + b["bhava_drishti_bala"], 2)
        assert b["total_virupas"] == expected_total
        assert b["total_rupas"] == round(expected_total / 60.0, 2)

        # 3. Check Phaladeepika Qualitative Diagnostics
        assert "classification" in b
        assert b["classification"] in ("Pusta", "Misra", "Hina")
        assert "lord_status" in b
        assert "sandhi_analysis" in b
        assert "kartari_yoga" in b
        assert "dpk_triad" in b
        assert "three_focal_points" in b
        assert "summary_verdict" in b


def test_bhava_dig_bala_all_genera():
    """
    Verifies Bhāva Digbala directional calculations (0 to 60 Virūpas)
    across all four biological sign genera per BPHS Ch. 27.
    """
    # 1. Nara (Human): Gemini (75°) -> Peak in H1 (60v), Zero in H7 (0v)
    assert get_sign_genus("Gemini", 15.0) == "Nara"
    assert calculate_bhava_dig_bala(1, 75.0) == 60.0
    assert calculate_bhava_dig_bala(7, 75.0) == 0.0
    assert calculate_bhava_dig_bala(4, 75.0) == 30.0

    # 2. Jalachara (Watery): Cancer (105°) -> Peak in H4 (60v), Zero in H10 (0v)
    assert get_sign_genus("Cancer", 15.0) == "Jalachara"
    assert calculate_bhava_dig_bala(4, 105.0) == 60.0
    assert calculate_bhava_dig_bala(10, 105.0) == 0.0

    # 3. Keeta (Insect): Scorpio (225°) -> Peak in H7 (60v), Zero in H1 (0v)
    assert get_sign_genus("Scorpio", 15.0) == "Keeta"
    assert calculate_bhava_dig_bala(7, 225.0) == 60.0
    assert calculate_bhava_dig_bala(1, 225.0) == 0.0

    # 4. Chathushpada (Quadruped): Aries (15°) -> Peak in H10 (60v), Zero in H4 (0v)
    assert get_sign_genus("Aries", 15.0) == "Chathushpada"
    assert calculate_bhava_dig_bala(10, 15.0) == 60.0
    assert calculate_bhava_dig_bala(4, 15.0) == 0.0


def test_phaladeepika_house_lord_protection_rule():
    """
    Verifies that when a house lord aspects its own house cusp,
    the ray is ALWAYS treated as positive/protective (+1.0),
    even if the lord is a natural malefic (Mars or Saturn).
    """
    # Scorpio cusp (225°) aspected by Mars (natural malefic):
    # Because Mars rules Scorpio, its aspect must be ADDED positively, not subtracted!
    drishti_own_lord = calculate_bhava_drishti_bala(
        bhava_madhya_lon=225.0,
        planet_positions={"Mars": 45.0},  # Opposition / strong aspect
        target_house_lord="Mars"
    )
    assert drishti_own_lord > 0.0

    # Conversely, an aspect on the same cusp from a malefic that does NOT rule it (e.g. Saturn):
    # Must be subtracted as negative pressure (-0.25)
    drishti_other_malefic = calculate_bhava_drishti_bala(
        bhava_madhya_lon=225.0,
        planet_positions={"Saturn": 45.0},
        target_house_lord="Mars"
    )
    assert drishti_other_malefic < 0.0


def test_zero_swisseph_in_bhava_bala():
    """Ensures jyotish/bhavas/bhava_bala.py contains zero direct swisseph imports or calls."""
    import inspect
    import jyotish.bhavas.bhava_bala as bb_module
    src = inspect.getsource(bb_module)
    assert "import swisseph" not in src
    assert "swe." not in src


def test_harsha_bala_computation(jolie_baseline):
    """
    Certifies Harsha Bala (Strength of Cheerfulness) computation across 4 sources
    per P.V.R. Narasimha Rao Ch. 28.3, and evaluates Dusthana Harsha/Viparita joy.
    """
    harsha_data = calculate_harsha_bala(jolie_baseline)

    assert "planets" in harsha_data
    assert "dusthana_joy" in harsha_data

    planets = harsha_data["planets"]
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        assert p in planets
        entry = planets[p]
        assert "sthana_bala_units" in entry
        assert "uccha_swakshetra_units" in entry
        assert "stree_purusha_units" in entry
        assert "dina_ratri_units" in entry
        assert "total_units" in entry
        assert "strength_category" in entry

        # Units per source are 0.0 or 5.0
        assert entry["sthana_bala_units"] in (0.0, 5.0)
        assert entry["uccha_swakshetra_units"] in (0.0, 5.0)
        assert entry["stree_purusha_units"] in (0.0, 5.0)
        assert entry["dina_ratri_units"] in (0.0, 5.0)

        # Sum check
        assert entry["total_units"] == (
            entry["sthana_bala_units"] +
            entry["uccha_swakshetra_units"] +
            entry["stree_purusha_units"] +
            entry["dina_ratri_units"]
        )
        assert 0.0 <= entry["total_units"] <= 20.0

    # Dusthana joy checks for houses 6, 8, 12
    dj = harsha_data["dusthana_joy"]
    for h in [6, 8, 12]:
        assert h in dj
        assert "yoga_name" in dj[h]
        assert "is_active" in dj[h]
        assert "effect" in dj[h]
    assert dj[6]["yoga_name"] == "Harsha"
    assert dj[8]["yoga_name"] == "Sarala"
    assert dj[12]["yoga_name"] == "Vimala"


def test_house_atmosphere_model(jolie_baseline):
    """
    Certifies the synthesized 12-House Atmosphere & Environmental Weather model.
    Verifies that each house produces a calibrated score, weather, and influence factors.
    """
    from jyotish.relationships.relationships import calculate_chart_dignities
    from jyotish.aspects.aspects import calculate_aspect_matrices
    from jyotish.shadbala.shadbala import calculate_shadbala

    dignities = calculate_chart_dignities(jolie_baseline)
    aspects = calculate_aspect_matrices(jolie_baseline)
    shadbala = calculate_shadbala(jolie_baseline, dignities=dignities, aspect_matrices=aspects)
    bhavas = calculate_bhava_bala(jolie_baseline, shadbala, aspects)

    atmosphere = calculate_house_atmosphere(jolie_baseline, bhavas, aspect_matrices=aspects)

    assert len(atmosphere) == 12
    for h in range(1, 13):
        assert h in atmosphere
        atm = atmosphere[h]
        assert "net_atmosphere_score" in atm
        assert -100.0 <= atm["net_atmosphere_score"] <= 100.0
        assert "classification" in atm
        assert "environmental_weather" in atm
        assert "auspicious_influences" in atm
        assert "inauspicious_influences" in atm
        assert "verdict" in atm
        assert isinstance(atm["auspicious_influences"], list)
        assert isinstance(atm["inauspicious_influences"], list)

        # Check attached atmosphere and harsha inside bhava_results
        assert "atmosphere" in bhavas[h]
        assert "harsha_bala" in bhavas[h]


def test_master_diagnostic_payload_generation(jolie_baseline):
    """
    Certifies that Stage 3 produces the authoritative 9-column Master Diagnostic
    payload matching ADR-006 design standards directly from the backend pipeline.
    """
    payload = generate_master_diagnostic_payload(jolie_baseline, varga="D1")

    assert "columns" in payload
    assert "rows" in payload
    assert "summary" in payload

    # Exact 9-column geometry verification
    assert payload["columns"] == MASTER_DIAGNOSTIC_COLUMNS
    assert len(payload["columns"]) == 9

    # 9 planetary rows (Sun through Ketu)
    assert len(payload["rows"]) == 9
    for row in payload["rows"]:
        assert "planet" in row
        assert "glyph" in row
        assert "graha_karaka" in row
        assert "longitude_bhava" in row
        assert "dignity_sambandha" in row
        assert "dispositor" in row
        assert "shadbala" in row
        assert "drishti_yuti" in row
        assert "nakshatra_pada" in row
        assert "avasthas" in row
        assert "archetype_vitality" in row

        # Check subfields
        assert 1.0 <= row["archetype_vitality"]["vitality_score"] <= 10.0
        assert row["graha_karaka"]["chara_karaka"] != ""
        assert row["longitude_bhava"]["whole_sign_house"] in range(1, 13)

