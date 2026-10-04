"""
tests/test_stage2a_interactions.py
Stage 2A Verification: Interaction & Relationship Matrices (Graha Dṛṣṭi & Pañcadhā Maitrī).

Verifies that:
1. Relationships and Aspects engines consume ChartBaseline directly without calling swisseph.
2. Natural, Temporary, and Compound (Pañcadhā) friendships compute accurately for the 7 physical grahas + nodes.
3. Varga dignities decompose across all 16 divisional charts (D1 through D60).
4. Aspect matrices generate valid 0-60 Virūpa continuous values matching Parāśarī rules.
5. Angelina Jolie and Native Shivapuri baseline charts execute with zero collisions or regressions.
"""

import sys
import pytest
from jyotish.baseline import (
    ChartBaseline,
    ALL_BODIES,
    VARGAS_LIST,
    SIGN_LORDS,
    VIMSHOTTARI_SEQUENCE,
    ZODIAC_SIGNS
)
from jyotish.relationships.relationships import (
    calculate_chart_dignities,
    get_natural_relationship,
    get_temporary_relationship,
    get_compound_relationship,
    get_dignity,
    SIGN_LORDS as REL_SIGN_LORDS,
    VIMSHOTTARI_SEQUENCE as REL_VIMSHOTTARI
)
from jyotish.aspects.aspects import (
    calculate_aspect_matrices,
    get_graha_drishti,
    ZODIAC_SIGNS as ASP_ZODIAC_SIGNS
)


PHYSICAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def test_stage2a_clean_import_hygiene():
    """Verifies single source of truth: no duplicate constant definitions, no swisseph calls."""
    # 1. Constants are identical single-source imports
    assert REL_SIGN_LORDS == SIGN_LORDS
    assert REL_VIMSHOTTARI == VIMSHOTTARI_SEQUENCE
    assert ASP_ZODIAC_SIGNS == ZODIAC_SIGNS

    # 2. Neither relationships nor aspects imports swisseph directly
    import jyotish.relationships.relationships as rel_mod
    import jyotish.aspects.aspects as asp_mod
    assert "swisseph" not in sys.modules or not hasattr(rel_mod, "swe")
    assert not hasattr(asp_mod, "swe")


def test_stage2a_angelina_jolie_relationships():
    """
    Verifies D1 Temporary (Tātkālika) and Compound (Pañcadhā) relationships
    on Angelina Jolie's certified benchmark chart.
    """
    baseline = ChartBaseline(
        name="Angelina Jolie",
        year=1975, month=6, day=4, hour=9, minute=9, second=0,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )

    dignity_data = calculate_chart_dignities(baseline)
    temp_rel = dignity_data["temporary_relationships"]
    comp_rel = dignity_data["compound_relationships"]

    # All 7 physical planets must be present
    for p1 in PHYSICAL_PLANETS:
        assert p1 in temp_rel
        assert p1 in comp_rel
        for p2 in PHYSICAL_PLANETS:
            assert temp_rel[p1][p2] in ["Friend", "Enemy"]
            assert comp_rel[p1][p2] in ["Great Friend", "Friend", "Neutral", "Enemy", "Great Enemy"]

    # Sun & Mercury are conjunct in Gemini (distance 0 -> house 1 -> Temporary Enemy)
    assert temp_rel["Sun"]["Mercury"] == "Enemy"
    # Sun natural to Mercury is Neutral. Neutral + Enemy = Enemy.
    assert comp_rel["Sun"]["Mercury"] == "Enemy"

    # Mars & Jupiter are conjunct in Aries (distance 0 -> house 1 -> Temporary Enemy)
    assert temp_rel["Mars"]["Jupiter"] == "Enemy"
    # Mars natural to Jupiter is Friend. Friend + Enemy = Neutral.
    assert comp_rel["Mars"]["Jupiter"] == "Neutral"

    # Sun in Gemini (sign 2), Mars in Aries (sign 0): distance from Sun to Mars = (0 - 2) % 12 = 10 (11th house) -> Friend
    assert temp_rel["Sun"]["Mars"] == "Friend"
    # Sun natural to Mars is Friend. Friend + Friend = Great Friend.
    assert comp_rel["Sun"]["Mars"] == "Great Friend"

    # Venus & Saturn are conjunct in Cancer (distance 0 -> Enemy)
    assert temp_rel["Venus"]["Saturn"] == "Enemy"
    # Venus natural to Saturn is Friend. Friend + Enemy = Neutral.
    assert comp_rel["Venus"]["Saturn"] == "Neutral"
    # Saturn natural to Venus is Friend. Friend + Enemy = Neutral.
    assert comp_rel["Saturn"]["Venus"] == "Neutral"

    # Rāhu and Ketu proxy evaluation in natural, temporary, and compound relationships
    nat_rel = dignity_data["natural_relationships"]
    assert "Rahu" in nat_rel
    assert "Ketu" in nat_rel
    assert nat_rel["Rahu"]["Mercury"] == "Friend"   # Saturn proxy views Mercury as Friend
    assert nat_rel["Ketu"]["Sun"] == "Friend"       # Mars proxy views Sun as Friend

    assert "Rahu" in comp_rel
    assert "Ketu" in comp_rel
    # Rahu uses Saturn proxy: Saturn natural to Mercury is Friend; Rahu in Scorpio (7), Mercury in Gemini (2)
    # Distance (2 - 7) % 12 = 7 (8th house -> Enemy) -> Friend + Enemy = Neutral
    assert comp_rel["Rahu"]["Mercury"] == "Neutral"


def test_stage2a_angelina_jolie_varga_dignities():
    """
    Verifies that planetary dignities decompose across all 16 divisional charts
    and match classical Parāśarī rules.
    """
    baseline = ChartBaseline(
        name="Angelina Jolie",
        year=1975, month=6, day=4, hour=9, minute=9, second=0,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )

    dignity_data = calculate_chart_dignities(baseline)
    varga_dig = dignity_data["varga_dignities"]

    # All 16 vargas must be evaluated
    assert len(varga_dig) == 16
    for v in VARGAS_LIST:
        assert v in varga_dig
        for p in PHYSICAL_PLANETS:
            entry = varga_dig[v][p]
            assert "sign" in entry
            assert "sign_lord" in entry
            assert "natural_relationship" in entry
            assert "temporary_relationship" in entry
            assert "compound_relationship" in entry
            assert "dignity" in entry
            assert entry["dignity"] in [
                "Exalted", "Moolatrikona", "Own Sign",
                "Great Friend's Sign", "Friend's Sign", "Neutral's Sign",
                "Enemy's Sign", "Great Enemy's Sign", "Debilitated"
            ]

    # Specific D1 Dignities
    d1 = varga_dig["D1"]
    assert d1["Sun"]["dignity"] == "Enemy's Sign"        # Sun in Gemini (ruled by Mercury, compound Enemy)
    assert d1["Mars"]["dignity"] == "Moolatrikona"       # Mars in Aries (<= 12°)
    assert d1["Mercury"]["dignity"] == "Own Sign"        # Mercury in Gemini (> 20° is own sign)

    # Specific D9 Navāṃśa Dignities
    d9 = varga_dig["D9"]
    assert d9["Venus"]["sign"] == "Pisces"
    assert d9["Venus"]["dignity"] == "Exalted"           # Venus exalted in Pisces
    assert d9["Mars"]["sign"] == "Cancer"
    assert d9["Mars"]["dignity"] == "Debilitated"        # Mars debilitated in Cancer
    assert d9["Moon"]["sign"] == "Cancer"
    assert d9["Moon"]["dignity"] == "Own Sign"           # Moon in own sign Cancer


def test_stage2a_debilitation_modes():
    """Verifies that kala_degree and whole_sign debilitation modes function correctly in orchestrator."""
    # Kailash chart where Moon is at ~5.7° Scorpio (past the 3° deep debilitation boundary)
    baseline = ChartBaseline(
        name="Kailash",
        year=1987, month=11, day=19, hour=16, minute=0, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0
    )

    kala_dig = calculate_chart_dignities(baseline, debilitation_mode="kala_degree")
    whole_dig = calculate_chart_dignities(baseline, debilitation_mode="whole_sign")

    # In kala_degree mode, Moon past 3° falls back to host relationship (Mars)
    assert kala_dig["varga_dignities"]["D1"]["Moon"]["dignity"] == "Friend's Sign"
    # In whole_sign mode, Moon anywhere in Scorpio is Debilitated
    assert whole_dig["varga_dignities"]["D1"]["Moon"]["dignity"] == "Debilitated"


def test_stage2a_aspect_matrices_geometry_and_rules():
    """
    Verifies that calculate_aspect_matrices generates:
    1. An 11x11 planet_to_planet matrix covering ALL_BODIES.
    2. A 7x12 planet_to_cusp matrix covering 7 classical planets and 12 sensitive cusps.
    3. Exact Parāśarī special aspects (Mars 4/8, Jupiter 5/9, Saturn 3/10, all 7th).
    """
    baseline = ChartBaseline(
        name="Angelina Jolie",
        year=1975, month=6, day=4, hour=9, minute=9, second=0,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )

    aspects = calculate_aspect_matrices(baseline)
    p2p = aspects["planet_to_planet"]
    p2c = aspects["planet_to_cusp"]

    # 1. 11x11 Planet-to-Planet Matrix Validation
    assert len(p2p) == len(ALL_BODIES)
    for b1 in ALL_BODIES:
        assert len(p2p[b1]) == len(ALL_BODIES)
        # Self-aspect is 0.0
        assert p2p[b1][b1] == 0.0
        for b2 in ALL_BODIES:
            val = p2p[b1][b2]
            assert 0.0 <= val <= 60.0

        # Non-casting bodies (Rahu, Ketu, Lagna, MC) cast 0.0 to all
        if b1 in ["Rahu", "Ketu", "Lagna", "MC"]:
            for b2 in ALL_BODIES:
                assert p2p[b1][b2] == 0.0

    # 2. 7x12 Planet-to-Cusp Matrix Validation
    assert len(p2c) == len(PHYSICAL_PLANETS)
    for p in PHYSICAL_PLANETS:
        assert len(p2c[p]) == 12
        for h in range(1, 13):
            val = p2c[p][h]
            assert 0.0 <= val <= 60.0

    # 3. Direct Parāśarī special aspect peak tests using get_graha_drishti
    # 7th opposition: all planets cast full 60 Virūpas at 180°
    for p in PHYSICAL_PLANETS:
        assert get_graha_drishti(p, 0.0, 180.0) == 60.0

    # Mars 4th (90°) and 8th (210°) aspects = 60.0
    assert get_graha_drishti("Mars", 0.0, 90.0) == 60.0
    assert get_graha_drishti("Mars", 0.0, 210.0) == 60.0

    # Jupiter 5th (120°) and 9th (240°) aspects = 60.0
    assert get_graha_drishti("Jupiter", 0.0, 120.0) == 60.0
    assert get_graha_drishti("Jupiter", 0.0, 240.0) == 60.0

    # Saturn 3rd (60°) and 10th (270°) aspects = 60.0
    assert get_graha_drishti("Saturn", 0.0, 60.0) == 60.0
    assert get_graha_drishti("Saturn", 0.0, 270.0) == 60.0


def test_stage2a_shivapuri_case():
    """
    Verifies that Native Shivapuri chart executes Stage 2A with zero collisions or regressions.
    """
    baseline = ChartBaseline(
        name="Shivapuri",
        year=1983, month=11, day=10, hour=22, minute=20, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0,
        nakshatra_system="ERNST_DHRUVA"
    )

    dignities = calculate_chart_dignities(baseline)
    aspects = calculate_aspect_matrices(baseline)

    # 1. Dignity breakdown for Shivapuri's Lagna Lord (Sun in Scorpio)
    # Sun in Scorpio is ruled by Mars (in Virgo).
    # Sun to Mars distance: Virgo (sign 5) from Scorpio (sign 7) = (5 - 7) % 12 = 10 (11th house) -> Friend
    # Sun natural to Mars: Friend. Friend + Friend = Great Friend!
    sun_d1 = dignities["varga_dignities"]["D1"]["Sun"]
    assert sun_d1["sign"] == "Scorpio"
    assert sun_d1["sign_lord"] == "Mars"
    assert sun_d1["natural_relationship"] == "Friend"
    assert sun_d1["temporary_relationship"] == "Friend"
    assert sun_d1["compound_relationship"] == "Great Friend"
    assert sun_d1["dignity"] == "Great Friend's Sign"

    # 2. Aspect matrix sizes
    assert len(aspects["planet_to_planet"]) == 11
    assert len(aspects["planet_to_cusp"]) == 7
    for p in PHYSICAL_PLANETS:
        assert len(aspects["planet_to_cusp"][p]) == 12
