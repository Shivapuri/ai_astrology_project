"""
tests/test_stage1_baseline.py
Verifies that Stage 1 ChartBaseline executes deterministically,
resolves cross-border wall leakage, and contains ZERO Shadbala or scoring logic.
"""

import json
import pytest
from jyotish.baseline import ChartBaseline, ALL_BODIES, VARGAS_LIST, PLANETS_ORDER, TARA_GRAHAS, calculate_shastiamsa_details


def test_chart_baseline_pure_astronomy():
    chart = ChartBaseline(
        name="Angelina Jolie",
        year=1975, month=6, day=4, hour=9, minute=9, second=0,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )

    # 1. Test Astronomical Coordinates
    coords = chart.coordinates
    assert abs(coords["Sun"]["longitude"] - 73.42) < 0.1
    assert abs(coords["Moon"]["longitude"] - 13.08) < 0.1
    assert coords["Lagna"]["sign"] == "Cancer"
    assert "MC" in coords

    # 2. Test Sensitive Cusp Degree
    assert abs(chart.astronomical_anchors["sensitive_cusp_degree"] - (coords["Lagna"]["longitude"] % 30.0)) < 0.0001

    # 3. Test Display-Only Isolation of Campanus Cusps
    display_cusps = chart.astronomical_anchors["campanus_display_cusps"]
    assert len(display_cusps) == 12
    for h in range(1, 13):
        assert display_cusps[h]["is_display_only"] is True
        assert "absolute_longitude" in display_cusps[h]
        assert "sign" in display_cusps[h]
        assert "degree_0_to_30" in display_cusps[h]

    # 4. Test Cross-Border Conjunction Detection with Boundary Attenuation
    conj = chart.conjunctions
    assert isinstance(conj, list)
    for c in conj:
        assert "effective_potency" in c
        assert "cross_border" in c
        if c["cross_border"]:
            assert c["boundary_factor"] == 0.75
        else:
            assert c["boundary_factor"] == 1.0

    # 5. Verify NO Shadbala, Dignity, or House Scoring exists on ChartBaseline
    assert not hasattr(chart, "shadbala")
    assert not hasattr(chart, "dignity")
    assert not hasattr(chart, "sign_base_scores")
    assert not hasattr(chart, "house_scores")


def test_3d_coordinates_and_baladi():
    """Verifies true 3D equatorial coordinates (RA, Declination) and Baladi age states."""
    chart = ChartBaseline(
        name="Coords3DTest",
        year=1995, month=5, day=15, hour=14, minute=30, second=0,
        latitude=28.6139, longitude=77.2090, timezone_offset=5.5
    )
    coords = chart.coordinates
    for b in ALL_BODIES:
        entry = coords[b]
        assert "right_ascension" in entry
        assert "declination" in entry
        assert 0.0 <= entry["right_ascension"] < 360.0
        assert -90.0 <= entry["declination"] <= 90.0
        assert "baladi_avastha" in entry
        baladi = entry["baladi_avastha"]
        assert baladi["segment"] in [1, 2, 3, 4, 5]
        assert baladi["efficiency_factor"] in [0.0, 0.10, 0.25, 0.50, 1.00]


def test_upagrahas_and_temporal_lords():
    """Verifies Gulika, Mandi, and Yamakantaka upagrahas, whole sign house placement, and temporal lords."""
    chart = ChartBaseline(
        name="UpagrahaTest",
        year=1995, month=5, day=15, hour=14, minute=30, second=0,
        latitude=28.6139, longitude=77.2090, timezone_offset=5.5
    )
    upag = chart.upagrahas
    assert "Gulika" in upag
    assert "Mandi" in upag
    assert "Yamakantaka" in upag
    for name, u in upag.items():
        assert 0.0 <= u["longitude"] < 360.0
        assert 0 <= u["sign_index"] < 12
        assert "degree_0_to_30" in u
        assert "epoch_jd" in u
        assert "whole_sign_house" in u
        assert 1 <= u["whole_sign_house"] <= 12

    # Verify January birth date preceding equinox lookup
    chart_jan = ChartBaseline(
        name="JanTest",
        year=1995, month=1, day=15, hour=12, minute=0, second=0,
        latitude=51.5074, longitude=-0.1278, timezone_offset=0.0
    )
    lords = chart_jan.astronomical_anchors["temporal_lords"]
    assert "Vara" in lords
    assert "Hora" in lords
    assert "Masa" in lords
    assert "Varsha" in lords


def test_pancanga_and_corrected_santana_tithi():
    """Verifies Pancanga metrics, Santana Tithi Krishna Chidra filter, and 3-tier Bija/Ksetra status."""
    chart = ChartBaseline(
        name="PancangaTest",
        year=1975, month=6, day=4, hour=9, minute=9, second=0,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )
    p = chart.pancanga
    assert 1 <= p["tithi"]["number"] <= 30
    assert p["tithi"]["paksha"] in ["Shukla", "Krishna"]
    assert 1 <= p["karana"]["number"] <= 60
    assert 1 <= p["nitya_yoga"]["number"] <= 27
    assert p["vara"] in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    sphutas = chart.special_sphutas
    moon_lon = chart.coordinates["Moon"]["longitude"]
    sun_lon = chart.coordinates["Sun"]["longitude"]
    expected_santana_arc = (5.0 * (moon_lon - sun_lon)) % 360.0
    expected_santana_tithi = int(expected_santana_arc // 12.0) + 1

    assert abs(sphutas["santana_tithi"]["arc_degrees"] - round(expected_santana_arc, 4)) < 0.0001
    assert sphutas["santana_tithi"]["tithi_number"] == expected_santana_tithi
    assert "paksha" in sphutas["santana_tithi"]
    assert "is_afflicted" in sphutas["santana_tithi"]

    # 3-tier Bija / Ksetra checks
    bija = sphutas["bija_sphuta_male"]
    assert "status" in bija
    assert "tier" in bija
    assert bija["tier"] in ["Strong", "Moderate", "Deficient"]
    assert "is_virile" in bija

    ksetra = sphutas["ksetra_sphuta_female"]
    assert "status" in ksetra
    assert "tier" in ksetra
    assert ksetra["tier"] in ["Strong", "Moderate", "Deficient"]
    assert "is_fertile" in ksetra


def test_candra_kriyadi_and_navatara():
    """Verifies Moon's Candra Kriyadi (with Sanskrit names, translations, benefic flags) and Navatara."""
    chart = ChartBaseline(
        name="KriyadiTest",
        year=1975, month=6, day=4, hour=9, minute=9, second=0,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )
    nak = chart.nakshatras
    moon_entry = nak["grahas"]["Moon"]
    assert "candra_kriyadi" in moon_entry
    kriyadi = moon_entry["candra_kriyadi"]
    assert 1 <= kriyadi["kriya"] <= 60
    assert 1 <= kriyadi["avastha"] <= 12
    assert 1 <= kriyadi["vela"] <= 36

    # Verify canonical names, translations, and nature
    assert "kriya_name" in kriyadi
    assert "kriya_translation" in kriyadi
    assert "kriya_nature" in kriyadi
    assert isinstance(kriyadi["kriya_is_benefic"], bool)
    assert "avastha_name" in kriyadi
    assert "vela_name" in kriyadi

    # Verify Navatara on all bodies
    for b in ALL_BODIES:
        entry = nak["grahas"][b]
        assert "tara" in entry
        assert "tara_number" in entry
        assert 1 <= entry["tara_number"] <= 9
        assert "lord_sublord" in entry
        assert "sidereal_ra" in entry
        assert "sidereal_longitude" in entry


def test_divisional_vargas_mc_and_lagna_d60_d30():
    """Verifies that Lagna and MC have D60 and D30 specs, and even-sign numbering is distinct."""
    chart = ChartBaseline(
        name="VargaSpecTest",
        year=1995, month=5, day=15, hour=14, minute=30, second=0,
        latitude=28.6139, longitude=77.2090, timezone_offset=5.5
    )
    vargas = chart.vargas
    assert len(vargas) == 16

    for v_name in VARGAS_LIST:
        v = vargas[v_name]
        assert "lagna" in v
        assert "mc" in v, f"MC missing in varga {v_name}"
        assert 0.0 <= v["mc"]["longitude"] < 360.0
        assert "cusps" in v
        assert len(v["cusps"]) == 12
        assert "bhavas" in v

    # 1. D60 specs on Lagna, MC, and Grahas
    d60 = vargas["D60"]
    assert "shastiamsa" in d60["lagna"]
    assert "shastiamsa" in d60["mc"]
    assert "shastiamsa" in d60["grahas"]["Sun"]
    sh_lagna = d60["lagna"]["shastiamsa"]
    assert "slice_number" in sh_lagna
    assert "deity_number" in sh_lagna
    assert 1 <= sh_lagna["slice_number"] <= 60
    assert 1 <= sh_lagna["deity_number"] <= 60

    # 2. D30 Parashari Trimsamsa on Lagna, MC, and Grahas
    d30 = vargas["D30"]
    assert "parashari_trimsamsa" in d30["lagna"]
    assert "parashari_trimsamsa" in d30["mc"]
    assert "parashari_trimsamsa" in d30["grahas"]["Sun"]

    # 3. Test even-sign reversal in D60
    # Taurus (even sign, index 1) at 0.25°:
    sh_even = calculate_shastiamsa_details(30.25)
    assert sh_even["slice_number"] == 1
    assert sh_even["deity_number"] == 60
    assert sh_even["deity"] == "Chandrarekha"


def test_cross_border_graha_yuddha_and_coordinates_flag():
    """Verifies Graha Yuddha collision <= 1.0° and coordinates planetary war flags."""
    chart = ChartBaseline()
    wars = chart.planetary_wars
    assert isinstance(wars, list)
    for w in wars:
        assert w["planet1"] in TARA_GRAHAS
        assert w["planet2"] in TARA_GRAHAS
        assert w["separation_degrees"] <= 1.0
        assert "winner" in w
        assert "loser" in w
        assert "cross_border" in w

    # Verify that Tara Grahas in coordinates possess war status attributes
    coords = chart.coordinates
    for p in TARA_GRAHAS:
        assert "is_in_planetary_war" in coords[p]
        assert "is_war_winner" in coords[p]
        assert "is_war_loser" in coords[p]
        assert "war_opponent" in coords[p]


def test_to_dict_serialization():
    """Verifies that to_dict exports completely clean primitive types serializable via json.dumps."""
    chart = ChartBaseline(
        name="SerializationTest",
        year=1995, month=5, day=15, hour=14, minute=30, second=0,
        latitude=28.6139, longitude=77.2090, timezone_offset=5.5
    )
    data = chart.to_dict()
    assert isinstance(data, dict)
    json_str = json.dumps(data)
    assert len(json_str) > 1000
    roundtrip = json.loads(json_str)
    assert roundtrip["name"] == "SerializationTest"
    assert "Gulika" in roundtrip["upagrahas"]
    assert "whole_sign_house" in roundtrip["upagrahas"]["Gulika"]
    assert "santana_tithi" in roundtrip["special_sphutas"]


def test_cross_border_conjunction_attenuation():
    """Verifies cross-border wall leakage resolution with 0.75 attenuation factor."""
    chart = ChartBaseline(
        name="CrossBorderTest",
        year=2000, month=6, day=20, hour=12, minute=0, second=0,
        latitude=0.0, longitude=0.0, timezone_offset=0.0
    )

    conjunctions = chart.conjunctions
    cross_border_conjs = [c for c in conjunctions if c["cross_border"]]

    assert len(cross_border_conjs) > 0, "Expected at least one cross-border conjunction"

    for c in cross_border_conjs:
        assert c["same_sign"] is False
        assert c["cross_border"] is True
        assert c["boundary_factor"] == 0.75
        assert c["sign1"] != c["sign2"]
        proximity_ratio = max(0.0, 1.0 - (c["separation_degrees"] / 10.0))
        assert abs(c["effective_potency"] - round(proximity_ratio * 0.75, 4)) < 0.0001


def test_separation_and_shortest_distance_matrices():
    """Verifies that 11x11 matrices cover all bodies including MC without KeyError."""
    chart = ChartBaseline(
        name="MatrixTest",
        year=1990, month=1, day=1, hour=12, minute=0, second=0,
        latitude=51.5074, longitude=-0.1278, timezone_offset=0.0
    )

    sep_matrix = chart.separation_matrix
    dist_matrix = chart.shortest_distance_matrix

    assert len(sep_matrix) == len(ALL_BODIES)
    assert len(dist_matrix) == len(ALL_BODIES)

    for b1 in ALL_BODIES:
        assert b1 in sep_matrix
        assert b1 in dist_matrix
        assert len(sep_matrix[b1]) == len(ALL_BODIES)
        assert len(dist_matrix[b1]) == len(ALL_BODIES)

        assert sep_matrix[b1][b1] == 0.0
        assert dist_matrix[b1][b1] == 0.0

        for b2 in ALL_BODIES:
            d = dist_matrix[b1][b2]
            assert 0.0 <= d <= 180.0
            assert abs(dist_matrix[b1][b2] - dist_matrix[b2][b1]) < 0.0001


def test_combustion_and_lunar_phase():
    """Verifies Surya Siddhanta combustion and lunar phase calculations."""
    chart = ChartBaseline(
        name="PhaseTest",
        year=1975, month=6, day=4, hour=9, minute=9, second=0,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )

    comb = chart.combustion_status
    assert comb["Sun"]["is_combust"] is False
    assert comb["Rahu"]["is_combust"] is False
    assert comb["Ketu"]["is_combust"] is False

    for p in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        assert "is_combust" in comb[p]
        assert "separation" in comb[p]
        assert "sun_distance" in comb[p]
        assert "orb_limit" in comb[p]
        assert "combustion_orb" in comb[p]
        assert "severity" in comb[p]

    lp = chart.lunar_phase
    assert "elongation_degrees" in lp
    assert "is_waxing" in lp
    assert "paksha" in lp
    assert isinstance(lp["is_waxing"], bool)
    assert 0.0 <= lp["illumination_pct"] <= 100.0


def test_refinements_and_shivapuri_case():
    """
    Verifies the 5 classical and mathematical refinements:
    1. Sidereal Nitya Yoga (Shivapuri has Yoga #10 Ganda, not tropical #13 Vyaghata).
    2. Phaladeepika Ch. 25 Upagrahas: Kala and Ardhaprahara along with Mandi, Gulika, and Yamakantaka.
    3. Phaladeepika Ch. 17 Core Sphutas: Trisphuta (with D9 Navamsa), Catusphuta, and Pancasphuta.
    4. True Node dynamic retrograde status (reflects direct stations).
    5. D30 primary coordinates map to Parashari unequal bounds with continuous harmonic auxiliary fields.
    """
    chart = ChartBaseline(
        name="Shivapuri",
        year=1983, month=11, day=10,
        hour=22, minute=20, second=0,
        latitude=52.20296, longitude=8.0448, timezone_offset=1.0,
        nakshatra_system="ERNST_DHRUVA"
    )

    # 1. Sidereal Nitya Yoga
    ny = chart.pancanga["nitya_yoga"]
    assert ny["number"] == 10, f"Expected Yoga #10 (Ganda), got {ny['number']}"
    assert ny["name"] == "Ganda"
    assert abs(ny["arc_degrees"] - 127.9623) < 0.01

    # 2. Complete Upagrahas (5 classical points)
    up = chart.upagrahas
    assert len(up) == 5
    for name in ["Gulika", "Mandi", "Yamakantaka", "Kala", "Ardhaprahara"]:
        assert name in up
        assert "sign" in up[name]
        assert "whole_sign_house" in up[name]
        assert 1 <= up[name]["whole_sign_house"] <= 12

    # 3. Phaladeepika Ch. 17 Sphutas
    sph = chart.special_sphutas
    assert "trisphuta" in sph
    assert "catusphuta" in sph
    assert "pancasphuta" in sph
    assert sph["trisphuta"]["sign"] == "Sagittarius"
    assert sph["trisphuta"]["d9_sign"] == "Gemini"
    assert sph["catusphuta"]["sign"] == "Cancer"
    assert sph["pancasphuta"]["sign"] == "Libra"

    # 4. True Node dynamic speed
    # On 1983-11-10 22:20 UTC, the True Node was in a direct station (speed > 0)
    rahu = chart.coordinates["Rahu"]
    assert rahu["speed"] > 0
    assert rahu["is_retrograde"] is False
    ketu = chart.coordinates["Ketu"]
    assert ketu["is_retrograde"] is False

    # 5. D30 primary Parashari mapping
    v30 = chart.vargas["D30"]
    # Lagna is at 129.5988° (Leo 9.5988° -> odd sign 5°-10° bound -> Saturn in Aquarius)
    assert v30["lagna"]["sign"] == "Aquarius"
    assert v30["lagna"]["sign_index"] == 10
    assert v30["lagna"]["continuous_sign"] == "Capricorn"
    assert "continuous_harmonic_longitude" in v30["lagna"]

    # Grahas in D30
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        g = v30["grahas"][p]
        assert "sign" in g
        assert "sign_index" in g
        assert "continuous_sign" in g
        assert "continuous_harmonic_longitude" in g
        assert "parashari_trimsamsa" in g


def test_baseline_modular_split():
    """
    Verifies the 3-file modular architecture:
    1. baseline_tables contains immutable reference catalogs.
    2. baseline_math provides pure stateless mathematical functions.
    3. baseline seamlessly re-exports both while orchestrating ChartBaseline.
    """
    # 1. Test baseline_tables imports & catalog lengths
    import jyotish.baseline_tables as tables
    assert len(tables.SHASTIAMSA_DEITIES) == 60
    assert len(tables.CHANDRA_KRIYAS_DATA) == 60
    assert len(tables.CHANDRA_AVASTHAS_DATA) == 12
    assert len(tables.CHANDRA_VELAS_DATA) == 36
    assert len(tables.NAKSHATRAS) == 27
    assert len(tables.NITYA_YOGAS) == 27
    assert len(tables.ZODIAC_SIGNS) == 12

    # 2. Test baseline_math standalone algorithms
    import jyotish.baseline_math as b_math
    # Sub-lord calculation
    sub = b_math.calculate_sub_lord(0.5, "Ketu")
    assert sub in tables.VIMSHOTTARI_SEQUENCE

    # D9 Navamsa calculation: 0° Aries -> 0° Aries
    nav_lon = b_math.calculate_varga_longitude(0.0, "D9")
    assert nav_lon == 0.0

    # Unequal Trimsamsa: 2° Aries (odd sign, 0-5°) -> Mars in Aries
    t_info = b_math.calculate_unequal_trimsamsa(2.0)
    assert t_info["ruler"] == "Mars"
    assert t_info["sign"] == "Aries"

    # Shastiamsa: 0.25° Aries (odd sign, 1st half-degree) -> Ghora
    sh_info = b_math.calculate_shastiamsa_details(0.25)
    assert sh_info["deity"] == "Ghora"
    assert sh_info["deity_number"] == 1

    # Baladi state: 3° Aries (odd sign, 0-6°) -> Bala
    baladi = b_math.calculate_baladi_state("Aries", 3.0)
    assert baladi["state"] == "Bala (Infant)"

    # Spherical trigonometry: 0° Ecliptic -> (0° RA, 0° Dec)
    ra, dec = b_math.get_eq_from_ecl(0.0)
    assert abs(ra) < 1e-5
    assert abs(dec) < 1e-5

    # 3. Test baseline re-exports
    import jyotish.baseline as b_main
    assert hasattr(b_main, "ChartBaseline")
    assert hasattr(b_main, "calculate_varga_longitude")
    assert hasattr(b_main, "ZODIAC_SIGNS")
    assert hasattr(b_main, "NITYA_YOGAS")
    assert hasattr(b_main, "CHANDRA_KRIYAS_DATA")
    assert hasattr(b_main, "get_eq_from_ecl")


