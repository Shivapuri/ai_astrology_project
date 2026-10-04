"""
tests/test_stage2a_aspects.py
Stage 2A Verification: Mathematical Invariants, Whole-Sign Cusps, and Rāśi/Graha Dṛṣṭi Integration.

Verifies:
1. Mathematical Invariant Tests:
   - 7th house opposition (180° separation) = 60.0 Virūpas for all 7 physical planets.
   - 6th house blind spot (150° separation) = 0.0 Virūpas for all 7 physical planets.
   - Mars 4th (90°) and 8th (210°) aspects = 60.0 Virūpas.
   - Jupiter 5th (120°) and 9th (240°) aspects = 60.0 Virūpas.
   - Saturn 3rd (60°) and 10th (270°) aspects = 60.0 Virūpas.
   - Rahu and Ketu cast 0.0 Virūpas across all angles.
2. Whole-Sign Cusp Alignment:
   - Native Shivapuri (Lagna: Leo 9° 36'):
     House 1 cusp = 129.5988° (Leo)
     House 4 cusp = 219.5988° (Scorpio)
     House 7 cusp = 309.5988° (Aquarius)
     House 10 cusp = 39.5988° (Taurus)
3. Rāśi Dṛṣṭi Rule Verification:
   - Aries (Moveable) aspects Leo, Scorpio, Aquarius (NOT Taurus).
   - Taurus (Fixed) aspects Cancer, Libra, Capricorn (NOT Aries).
   - Gemini (Dual) aspects Virgo, Sagittarius, Pisces (NOT Gemini).
4. Stage 2A Master Orchestrator (calculate_aspect_matrices):
   - Dual-indexed Graha Dṛṣṭi (outgoing and incoming O(1) maps).
   - Dual-indexed Cusp Dṛṣṭi (by_planet and by_house O(1) maps).
   - Rāśi Dṛṣṭi planet-to-planet and house-to-planets mappings.
   - Dynamic Benefic/Malefic breakdown (+ / - Net Virūpas) for planets and cusps.
5. Multi-Varga Helper (calculate_varga_aspects):
   - Direct consumption of baseline.vargas[varga] without manual unpacking.
"""

import pytest
from jyotish.baseline import (
    ChartBaseline,
    ALL_BODIES,
    PLANETS_ORDER,
    ZODIAC_SIGNS,
)
from jyotish.aspects.aspects import (
    get_graha_drishti,
    get_rasi_drishti,
    calculate_aspect_matrices,
    calculate_varga_aspects,
    PHYSICAL_PLANETS,
    NON_CASTING_BODIES,
)


def test_graha_drishti_mathematical_invariants():
    """
    Verifies classical Parāśarī mathematical invariants for Graha Dṛṣṭi:
    - 7th house opposition (180°) = 60.0 Virūpas for all 7 planets.
    - 6th house blind spot (150°) = 0.0 Virūpas.
    - Mars special aspects (90° & 210°) = 60.0 Virūpas.
    - Jupiter special aspects (120° & 240°) = 60.0 Virūpas.
    - Saturn special aspects (60° & 270°) = 60.0 Virūpas.
    - Rahu and Ketu cast 0.0 Virūpas.
    """
    # 1. 7th house opposition (180° separation) equals exactly 60.0 Virūpas for all 7 planets
    for p in PHYSICAL_PLANETS:
        val = get_graha_drishti(p, 0.0, 180.0)
        assert val == 60.0, f"{p} at 180° opposition must be 60.0 Virūpas, got {val}"

    # 2. 6th house blind spot (150° separation) equals exactly 0.0 Virūpas
    for p in PHYSICAL_PLANETS:
        val = get_graha_drishti(p, 0.0, 150.0)
        assert val == 0.0, f"{p} at 150° blind spot must be 0.0 Virūpas, got {val}"

    # 3. Mars 4th (90°) and 8th (210°) aspects equal exactly 60.0 Virūpas
    assert get_graha_drishti("Mars", 0.0, 90.0) == 60.0, "Mars 4th aspect (90°) must be 60.0 Virūpas"
    assert get_graha_drishti("Mars", 0.0, 210.0) == 60.0, "Mars 8th aspect (210°) must be 60.0 Virūpas"

    # 4. Jupiter 5th (120°) and 9th (240°) aspects equal exactly 60.0 Virūpas
    assert get_graha_drishti("Jupiter", 0.0, 120.0) == 60.0, "Jupiter 5th aspect (120°) must be 60.0 Virūpas"
    assert get_graha_drishti("Jupiter", 0.0, 240.0) == 60.0, "Jupiter 9th aspect (240°) must be 60.0 Virūpas"

    # 5. Saturn 3rd (60°) and 10th (270°) aspects equal exactly 60.0 Virūpas
    assert get_graha_drishti("Saturn", 0.0, 60.0) == 60.0, "Saturn 3rd aspect (60°) must be 60.0 Virūpas"
    assert get_graha_drishti("Saturn", 0.0, 270.0) == 60.0, "Saturn 10th aspect (270°) must be 60.0 Virūpas"

    # 6. Rahu and Ketu cast 0.0 Virūpas at all angles
    test_angles = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
    for node in ["Rahu", "Ketu"]:
        for angle in test_angles:
            assert get_graha_drishti(node, 0.0, angle) == 0.0, f"{node} must cast 0.0 Virūpas at {angle}°"


def test_whole_sign_cusp_verification_shivapuri():
    """
    Verifies that on Native Shivapuri (Lagna: Leo 9° 36'), whole-sign sensitive cusps
    anchor correctly to the rising sign:
    - House 1 cusp is at 129.5988° (Leo)
    - House 4 cusp is at 219.5988° (Scorpio)
    - House 7 cusp is at 309.5988° (Aquarius)
    - House 10 cusp is at 39.5988° (Taurus)
    """
    baseline = ChartBaseline(
        name="Shivapuri",
        year=1983, month=11, day=10, hour=22, minute=20, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0,
        nakshatra_system="ERNST_DHRUVA"
    )

    asc_coord = baseline.coordinates["Lagna"]
    assert asc_coord["sign"] == "Leo"
    assert asc_coord["sign_index"] == 4
    sens_deg = baseline.astronomical_anchors["sensitive_cusp_degree"]
    assert round(sens_deg, 4) == 9.5988

    aspects = calculate_aspect_matrices(baseline)
    cusp_longitudes = aspects["cusp_drishti"]["cusp_longitudes"]

    # Verify sensitive cusps for 1, 4, 7, 10
    assert pytest.approx(cusp_longitudes[1], abs=0.0001) == 129.5988
    assert pytest.approx(cusp_longitudes[4], abs=0.0001) == 219.5988
    assert pytest.approx(cusp_longitudes[7], abs=0.0001) == 309.5988
    assert pytest.approx(cusp_longitudes[10], abs=0.0001) == 39.5988

    # Verify signs of the 4 angles
    assert int(cusp_longitudes[1] // 30) == 4   # Leo
    assert int(cusp_longitudes[4] // 30) == 7   # Scorpio
    assert int(cusp_longitudes[7] // 30) == 10  # Aquarius
    assert int(cusp_longitudes[10] // 30) == 1  # Taurus


def test_rasi_drishti_rules():
    """
    Verifies Rāśi Dṛṣṭi modality rules:
    - Aries (Moveable) aspects Leo, Scorpio, Aquarius (NOT Taurus).
    - Taurus (Fixed) aspects Cancer, Libra, Capricorn (NOT Aries).
    - Gemini (Dual) aspects Virgo, Sagittarius, Pisces (NOT Gemini).
    """
    # 1. Moveable / Cardinal sign (Aries)
    aries_aspects = get_rasi_drishti("Aries")
    assert "Leo" in aries_aspects
    assert "Scorpio" in aries_aspects
    assert "Aquarius" in aries_aspects
    assert "Taurus" not in aries_aspects  # Adjacent fixed sign excluded
    assert len(aries_aspects) == 3

    # 2. Fixed sign (Taurus)
    taurus_aspects = get_rasi_drishti("Taurus")
    assert "Cancer" in taurus_aspects
    assert "Libra" in taurus_aspects
    assert "Capricorn" in taurus_aspects
    assert "Aries" not in taurus_aspects  # Adjacent moveable sign excluded
    assert len(taurus_aspects) == 3

    # 3. Dual sign (Gemini)
    gemini_aspects = get_rasi_drishti("Gemini")
    assert "Virgo" in gemini_aspects
    assert "Sagittarius" in gemini_aspects
    assert "Pisces" in gemini_aspects
    assert "Gemini" not in gemini_aspects  # Cannot aspect itself
    assert len(gemini_aspects) == 3


def test_calculate_aspect_matrices_dual_indexing_and_breakdown():
    """
    Verifies calculate_aspect_matrices for:
    1. Graha Drishti 11x11 planet-to-planet dual indexing (outgoing and incoming).
    2. Graha Drishti 7x12 planet-to-cusp dual indexing (by_planet and by_house).
    3. Rāśi Drishti planet_to_planet and house_to_planets structures.
    4. Benefic / Malefic Breakdown (+ / - Net Virūpas) for planets and cusps.
    """
    baseline = ChartBaseline(
        name="Angelina Jolie",
        year=1975, month=6, day=4, hour=9, minute=9, second=0,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )

    aspects = calculate_aspect_matrices(baseline)

    # 1. Graha Drishti Planet-to-Planet (11x11)
    gd = aspects["graha_drishti"]
    outgoing = gd["outgoing"]
    incoming = gd["incoming"]

    assert len(outgoing) == len(ALL_BODIES)
    assert len(incoming) == len(ALL_BODIES)

    for b1 in ALL_BODIES:
        assert len(outgoing[b1]) == len(ALL_BODIES)
        assert len(incoming[b1]) == len(ALL_BODIES)
        # Self-aspect is 0
        assert outgoing[b1][b1] == 0.0
        assert incoming[b1][b1] == 0.0

        for b2 in ALL_BODIES:
            # Dual indexing symmetry: outgoing[b1][b2] == incoming[b2][b1]
            assert outgoing[b1][b2] == incoming[b2][b1]

        # Non-casting bodies cast 0.0
        if b1 in NON_CASTING_BODIES:
            for b2 in ALL_BODIES:
                assert outgoing[b1][b2] == 0.0

    # 2. Graha Drishti Planet-to-Cusp (7x12)
    cd = aspects["cusp_drishti"]
    by_planet = cd["by_planet"]
    by_house = cd["by_house"]

    assert len(by_planet) == len(PHYSICAL_PLANETS)
    assert len(by_house) == 12

    for p in PHYSICAL_PLANETS:
        assert len(by_planet[p]) == 12
        for h in range(1, 13):
            # Dual indexing symmetry: by_planet[p][h] == by_house[h][p]
            assert by_planet[p][h] == by_house[h][p]
            assert 0.0 <= by_planet[p][h] <= 60.0

    for h in range(1, 13):
        assert len(by_house[h]) == len(PHYSICAL_PLANETS)

    # 3. Rāśi Drishti
    rd = aspects["rasi_drishti"]
    assert "planet_to_planet" in rd
    assert "house_to_planets" in rd
    assert "sign_to_signs" in rd

    for b in ALL_BODIES:
        assert b in rd["planet_to_planet"]
        assert isinstance(rd["planet_to_planet"][b], list)

    for h in range(1, 13):
        assert h in rd["house_to_planets"]
        assert isinstance(rd["house_to_planets"][h], list)
        for p in rd["house_to_planets"][h]:
            assert p in PLANETS_ORDER

    # 4. Benefic / Malefic Totals
    bmt = aspects["benefic_malefic_totals"]
    assert "planets" in bmt
    assert "cusps" in bmt
    assert "classification" in bmt

    classification = bmt["classification"]
    assert classification["Jupiter"] is True
    assert classification["Venus"] is True
    assert classification["Sun"] is False
    assert classification["Mars"] is False
    assert classification["Saturn"] is False

    for b in ALL_BODIES:
        entry = bmt["planets"][b]
        assert "benefic_virupas" in entry
        assert "malefic_virupas" in entry
        assert "net_virupas" in entry
        expected_net = round(entry["benefic_virupas"] - entry["malefic_virupas"], 4)
        assert pytest.approx(entry["net_virupas"], abs=0.0001) == expected_net

    for h in range(1, 13):
        entry = bmt["cusps"][h]
        assert "benefic_virupas" in entry
        assert "malefic_virupas" in entry
        assert "net_virupas" in entry
        expected_net = round(entry["benefic_virupas"] - entry["malefic_virupas"], 4)
        assert pytest.approx(entry["net_virupas"], abs=0.0001) == expected_net

    # 5. Backwards Compatibility Aliases
    assert aspects["planet_to_planet"] is outgoing
    assert aspects["planet_to_cusp"] is by_planet


def test_calculate_varga_aspects_adapter():
    """
    Verifies that calculate_varga_aspects cleanly consumes:
    1. A ChartBaseline instance with varga name.
    2. A varga dictionary directly (e.g. baseline.vargas["D1"]).
    3. Produces identical results across both calling styles.
    """
    baseline = ChartBaseline(
        name="Shivapuri",
        year=1983, month=11, day=10, hour=22, minute=20, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0,
        nakshatra_system="ERNST_DHRUVA"
    )

    # Calling style 1: baseline object + varga
    res1 = calculate_varga_aspects(baseline, "D1")

    # Calling style 2: direct varga dict
    res2 = calculate_varga_aspects(baseline.vargas["D1"])

    assert "planets" in res1
    assert "cusps" in res1
    assert "totals" in res1
    assert "yutis" in res1

    # Verify identity between both calling conventions
    assert res1["totals"]["planets"]["Sun"] == res2["totals"]["planets"]["Sun"]
    assert res1["planets"]["Sun"]["Moon"] == res2["planets"]["Sun"]["Moon"]


def test_mercury_malefic_conjunction_rule():
    """
    Verifies that Mercury becomes a functional malefic when conjoined with natural malefics
    (Mars, Saturn, Rahu, Ketu) per BPHS Ch. 3 and Phaladeepika Ch. 2.27.
    - Kailash: Mercury in Scorpio (free from combustion and no malefics in Scorpio) -> Benefic (True)
    - Native Shivapuri: Mercury in Libra with Saturn (natural malefic) -> Malefic (False)
    """
    kailash = ChartBaseline(
        name="Kailash",
        year=1987, month=11, day=19, hour=16, minute=0, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0
    )
    kailash_aspects = calculate_aspect_matrices(kailash)
    assert kailash_aspects["benefic_malefic_totals"]["classification"]["Mercury"] is True

    shivapuri = ChartBaseline(
        name="Shivapuri",
        year=1983, month=11, day=10, hour=22, minute=20, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0,
        nakshatra_system="ERNST_DHRUVA"
    )
    shiv_aspects = calculate_aspect_matrices(shivapuri)
    # Saturn in Libra conjoins Mercury in Libra -> Mercury is Malefic
    assert shiv_aspects["benefic_malefic_totals"]["classification"]["Mercury"] is False


def test_house_lord_protection_rule():
    """
    Verifies the House Lord Protection Rule per Phaladeepika Ch. 15.1-3:
    A planet casting Graha Drishti on its own whole-sign house is ALWAYS protective (benefic),
    even if that planet is a natural malefic (such as Mars or Saturn).
    
    In Native Shivapuri:
    - Lagna is Leo. House 9 is Aries, ruled by Mars (a natural malefic).
    - Mars in Virgo casts its 8th special aspect (60.0 Virupas) onto House 9 (Aries).
    - Under the protection rule, Mars's 60.0 Virupas are added to benefic_virupas, NOT malefic_virupas.
    """
    shivapuri = ChartBaseline(
        name="Shivapuri",
        year=1983, month=11, day=10, hour=22, minute=20, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0,
        nakshatra_system="ERNST_DHRUVA"
    )
    aspects = calculate_aspect_matrices(shivapuri)
    h9_cusp = aspects["cusp_drishti"]["by_house"][9]
    h9_totals = aspects["benefic_malefic_totals"]["cusps"][9]

    # Mars casts full 60.0 Virupas on House 9
    assert h9_cusp["Mars"] == 60.0

    # Benefics: Jupiter (57.5631) + Venus (55.9469) + Mars (60.0, protective lord) = 173.51
    assert pytest.approx(h9_totals["benefic_virupas"], abs=0.01) == 173.51
    # Verify Mars is NOT counted in malefic virupas
    assert h9_totals["malefic_virupas"] < 60.0

