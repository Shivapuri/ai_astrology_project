"""
tests/test_vargas.py
Rigorous verification test suite for Divisional Charts (Ṣoḍaśavarga)
Remediation & Planetary Rulership Engine.
"""

import pytest
from jyotish.baseline_tables import (
    SHASTIAMSA_MALEFIC_ODD,
    VARGAS_LIST,
    ZODIAC_SIGNS,
    PLANETS_ORDER
)
from jyotish.baseline_math import (
    calculate_varga_longitude,
    calculate_shastiamsa_details,
    calculate_unequal_trimsamsa,
    get_varga_ruler_info
)
from jyotish.baseline import ChartBaseline
from jyotish.pipeline import ChartPipeline
from jyotish.generate_jyotish import generate_kala_chart


# =============================================================================
# 1. D60 MALEFIC AUDIT (PHALADEEPIKA CH. 3 TEXT 5)
# =============================================================================
def test_d60_malefic_set_and_slice_classification():
    """
    Verifies that slice 39 (Poornachandra / Full Moon) is malefic (Ashubha/malefic),
    while slice 41 (Kulanasa / Lineage Destroyer) is non-malefic (Shubha/benefic),
    strictly conforming to Mantreswara's Phaladeepika Ch. 3 Text 5.
    """
    # Check set catalog
    assert 39 in SHASTIAMSA_MALEFIC_ODD, "Slice 39 (Poornachandra) MUST be in malefic set per Phaladeepika"
    assert 41 not in SHASTIAMSA_MALEFIC_ODD, "Slice 41 (Kulanasa) must NOT be in malefic set per Phaladeepika"

    # Odd sign test: Aries (0°–30°):
    # Slice 39 spans 19.0° to 19.5° (part_idx 38 -> slice 39)
    lon_slice_39 = 19.25
    details_39 = calculate_shastiamsa_details(lon_slice_39)
    assert details_39["slice_number"] == 39
    assert details_39["deity"] == "Poornachandra"
    assert details_39["is_benefic"] is False
    assert details_39["is_malefic"] is True
    assert details_39["nature"] == "Ashubha / Malefic"

    # Slice 41 spans 20.0° to 20.5° (part_idx 40 -> slice 41)
    lon_slice_41 = 20.25
    details_41 = calculate_shastiamsa_details(lon_slice_41)
    assert details_41["slice_number"] == 41
    assert details_41["deity"] == "Kulanasa"
    assert details_41["is_malefic"] is False
    assert details_41["is_benefic"] is True
    assert details_41["nature"] == "Shubha / Benefic"


# =============================================================================
# 2. D2 PARĀŚARĪ HORĀ & SYMBOL REPRESENTATION
# =============================================================================
def test_d2_parashari_hora_calculations():
    """
    Verifies classical Parāśarī Horā (D2):
    - 5° Aries (odd sign, 1st half) -> Sun (Leo, ☉)
    - 20° Aries (odd sign, 2nd half) -> Moon (Cancer, ☽)
    - 5° Taurus (even sign, 1st half) -> Moon (Cancer, ☽)
    - 20° Taurus (even sign, 2nd half) -> Sun (Leo, ☉)
    - Confirm no planet under 'parashari' mode ever receives any sign other than Cancer or Leo.
    """
    # 5° Aries (odd sign, 0°–15°)
    lon_5_aries = 5.0
    d2_5_aries = calculate_varga_longitude(lon_5_aries, "D2", d2_mode="parashari")
    sign_idx_5_aries = int(d2_5_aries // 30) % 12
    assert ZODIAC_SIGNS[sign_idx_5_aries] == "Leo"
    info_5_aries = get_varga_ruler_info("D2", 0, 5.0, d2_mode="parashari")
    assert info_5_aries["ruler"] == "Sun"
    assert info_5_aries["symbol"] == "☉"
    assert info_5_aries["display_symbol"] == "☉"
    assert "Solar" in info_5_aries["hora_polarity"]

    # 20° Aries (odd sign, 15°–30°)
    lon_20_aries = 20.0
    d2_20_aries = calculate_varga_longitude(lon_20_aries, "D2", d2_mode="parashari")
    sign_idx_20_aries = int(d2_20_aries // 30) % 12
    assert ZODIAC_SIGNS[sign_idx_20_aries] == "Cancer"
    info_20_aries = get_varga_ruler_info("D2", 0, 20.0, d2_mode="parashari")
    assert info_20_aries["ruler"] == "Moon"
    assert info_20_aries["symbol"] == "☽"
    assert info_20_aries["display_symbol"] == "☽"
    assert "Lunar" in info_20_aries["hora_polarity"]

    # 5° Taurus (even sign, 0°–15°)
    lon_5_taurus = 35.0
    d2_5_taurus = calculate_varga_longitude(lon_5_taurus, "D2", d2_mode="parashari")
    sign_idx_5_taurus = int(d2_5_taurus // 30) % 12
    assert ZODIAC_SIGNS[sign_idx_5_taurus] == "Cancer"
    info_5_taurus = get_varga_ruler_info("D2", 1, 5.0, d2_mode="parashari")
    assert info_5_taurus["ruler"] == "Moon"
    assert info_5_taurus["symbol"] == "☽"
    assert info_5_taurus["display_symbol"] == "☽"
    assert "Lunar" in info_5_taurus["hora_polarity"]

    # 20° Taurus (even sign, 15°–30°)
    lon_20_taurus = 50.0
    d2_20_taurus = calculate_varga_longitude(lon_20_taurus, "D2", d2_mode="parashari")
    sign_idx_20_taurus = int(d2_20_taurus // 30) % 12
    assert ZODIAC_SIGNS[sign_idx_20_taurus] == "Leo"
    info_20_taurus = get_varga_ruler_info("D2", 1, 20.0, d2_mode="parashari")
    assert info_20_taurus["ruler"] == "Sun"
    assert info_20_taurus["symbol"] == "☉"
    assert info_20_taurus["display_symbol"] == "☉"
    assert "Solar" in info_20_taurus["hora_polarity"]

    # Thorough sweep: verify that across all 360 degrees, Parashari D2 ONLY produces Cancer or Leo
    for deg in range(0, 360):
        d2_deg = calculate_varga_longitude(float(deg) + 0.5, "D2", d2_mode="parashari")
        s_name = ZODIAC_SIGNS[int(d2_deg // 30) % 12]
        assert s_name in ("Cancer", "Leo"), f"Degree {deg} produced non-bipolar sign {s_name} in D2"


def test_d2_cyclical_legacy_mode():
    """Verifies that cyclical / parivritti mode remains supported for backward compatibility."""
    lon_5_aries = 5.0
    d2_cyc = calculate_varga_longitude(lon_5_aries, "D2", d2_mode="cyclical")
    assert int(d2_cyc // 30) % 12 == 0  # Aries


def test_d2_binary_chambers_structure():
    """
    Verifies that D2 produces 2 binary chambers (Solar / Pingala and Lunar / Ida)
    instead of 12 whole sign houses with 10 empty signs.
    """
    chart = generate_kala_chart(
        name="HoraChamberTest",
        year=1995, month=5, day=15, hour=14, minute=30,
        latitude=51.5074, longitude=-0.1278, timezone_offset=1.0,
        d2_mode="parashari"
    )
    d2 = chart["vargas"]["D2"]
    assert d2.get("is_binary_varga") is True
    bhavas = d2.get("bhavas", [])
    assert len(bhavas) == 2, "D2 must have exactly 2 chambers"

    c1, c2 = bhavas[0], bhavas[1]
    assert c1["chamber"] == 1
    assert c1["ruler"] == "Sun"
    assert c1["symbol"] == "☉"
    assert "Solar" in c1["polarity"]

    assert c2["chamber"] == 2
    assert c2["ruler"] == "Moon"
    assert c2["symbol"] == "☽"
    assert "Lunar" in c2["polarity"]

    # Verify all 9 planets + Ascendant are accounted for
    all_occupants = c1["planets"] + c2["planets"]
    assert "Asc" in all_occupants
    for p in PLANETS_ORDER:
        assert p in all_occupants


# =============================================================================
# 3. D3 & D30 PLANETARY REPRESENTATION & TRIṀŚĀṀŚA INTEGRITY
# =============================================================================
def test_d3_planetary_representation():
    """
    Verifies that in D3 (Drekkāṇa), 15° Aries (second trine -> Leo)
    is ruled by Sun with symbol ☉ and category Drekkāṇa Trine 2.
    """
    r_info = get_varga_ruler_info("D3", 0, 15.0)
    assert r_info["ruler"] == "Sun"
    assert r_info["symbol"] == "☉"
    assert r_info["display_symbol"] == "☉"
    assert r_info["display_entity"] == "☉ Sun"
    assert r_info["varga_type"] == "planetary_triad"
    assert r_info["is_planetary_varga"] is True


def test_d30_trimsamsa_integrity():
    """
    Verifies that in standard mode, a planet at 15° Aries is placed in Sagittarius ruled by Jupiter (♃),
    and that no planet in classical Parashari D30 is ever assigned to Cancer or Leo.
    """
    # 15° Aries is in odd sign between 10° and 18° -> Sagittarius ruled by Jupiter
    lon_15_aries = 15.0
    t_info = calculate_unequal_trimsamsa(lon_15_aries)
    assert t_info["sign"] == "Sagittarius"
    assert t_info["ruler"] == "Jupiter"

    r_info = get_varga_ruler_info("D30", 0, 15.0)
    assert r_info["ruler"] == "Jupiter"
    assert r_info["symbol"] == "♃"
    assert r_info["display_symbol"] == "♃"
    assert r_info["display_entity"] == "♃ Jupiter"
    assert r_info["bound_ruler"] == "Jupiter"
    assert r_info["bound_symbol"] == "♃"
    assert r_info["varga_type"] == "planetary_bounds"
    assert r_info["is_planetary_varga"] is True

    # Sweep entire zodiac: confirm Cancer and Leo NEVER appear in classical D30
    for sign_i in range(12):
        for deg in [1.0, 7.0, 14.0, 22.0, 28.0]:
            lon = sign_i * 30.0 + deg
            res = calculate_unequal_trimsamsa(lon)
            assert res["sign"] not in ("Cancer", "Leo"), (
                f"Classical D30 assigned invalid sign {res['sign']} at longitude {lon}"
            )
            assert res["ruler"] in ("Mars", "Saturn", "Jupiter", "Mercury", "Venus")


def test_d30_pipeline_does_not_mutate_to_harmonic():
    """
    Verifies that ChartPipeline does NOT overwrite classical Parashari D30
    with continuous harmonic coordinates unless harmonic mode is explicitly requested.
    """
    # Standard generation (default trimsamsa_mode="parashari")
    chart = generate_kala_chart(
        name="TrimsamsaTest",
        year=1995, month=5, day=15, hour=14, minute=30,
        latitude=51.5074, longitude=-0.1278, timezone_offset=1.0,
        trimsamsa_mode="parashari"
    )
    d30_grahas = chart["vargas"]["D30"]["grahas"]
    for p_name, g_data in d30_grahas.items():
        assert g_data["sign"] not in ("Cancer", "Leo"), (
            f"Planet {p_name} in Parashari D30 received forbidden sign {g_data['sign']}"
        )
        assert "bound_ruler" in g_data
        assert "bound_symbol" in g_data
        assert g_data["is_planetary_varga"] is True

    # When harmonic mode is explicitly requested, it should use continuous harmonic coordinates
    chart_harmonic = generate_kala_chart(
        name="TrimsamsaHarmonicTest",
        year=1995, month=5, day=15, hour=14, minute=30,
        latitude=51.5074, longitude=-0.1278, timezone_offset=1.0,
        trimsamsa_mode="harmonic"
    )
    d30_harmonic_grahas = chart_harmonic["vargas"]["D30"]["grahas"]
    for p_name, g_data in d30_harmonic_grahas.items():
        assert "continuous_harmonic_longitude" in g_data
        assert abs(g_data["longitude"] - g_data["continuous_harmonic_longitude"]) < 0.001


# =============================================================================
# 4. WHOLE SIGN VARGA BHAVAS
# =============================================================================
def test_whole_sign_varga_bhavas():
    """
    Verifies that vargas['D9']['bhavas'] contains 12 non-overlapping 30° houses
    properly matching whole signs starting from the Navāṁśa Lagna.
    """
    chart = generate_kala_chart(
        name="BhavaTest",
        year=1995, month=5, day=15, hour=14, minute=30,
        latitude=51.5074, longitude=-0.1278, timezone_offset=1.0
    )
    d9 = chart["vargas"]["D9"]
    d9_lagna_sign = d9["lagna"]["sign"]
    d9_lagna_idx = ZODIAC_SIGNS.index(d9_lagna_sign)
    bhavas = d9["bhavas"]

    assert len(bhavas) == 12, "D9 must have exactly 12 bhavas"

    # House 1 must match the D9 Lagna sign
    assert bhavas[0]["house"] == 1
    assert bhavas[0]["sign"] == d9_lagna_sign
    assert bhavas[0]["sign_index"] == d9_lagna_idx
    assert "Asc" in bhavas[0]["planets"]

    # Verify all 12 houses are sequential, non-overlapping 30° whole-sign sectors
    for i in range(12):
        bh = bhavas[i]
        expected_sign_idx = (d9_lagna_idx + i) % 12
        expected_sign = ZODIAC_SIGNS[expected_sign_idx]
        assert bh["house"] == i + 1
        assert bh["sign"] == expected_sign
        assert bh["sign_index"] == expected_sign_idx
        assert round(bh["end"] - bh["start"], 4) == 30.0

        # Check planetary occupancy matches varga sign
        for p_name in bh["planets"]:
            if p_name != "Asc":
                assert d9["grahas"][p_name]["sign"] == expected_sign


# =============================================================================
# 5. ENRICHMENT OF RULERS & SYMBOLS ACROSS ALL VARGAS
# =============================================================================
def test_varga_ruler_and_symbol_enrichment():
    """
    Verifies that all 16 divisional charts have ruler, ruler_symbol,
    display_entity, display_symbol, and is_planetary_varga populated on all entities and Lagna.
    """
    chart = generate_kala_chart(
        name="EnrichmentTest",
        year=1995, month=5, day=15, hour=14, minute=30,
        latitude=51.5074, longitude=-0.1278, timezone_offset=1.0
    )
    vargas = chart["vargas"]

    for v_name in VARGAS_LIST:
        v_data = vargas[v_name]
        assert "lagna" in v_data
        lagna = v_data["lagna"]
        assert "ruler" in lagna and isinstance(lagna["ruler"], str)
        assert "ruler_symbol" in lagna and isinstance(lagna["ruler_symbol"], str)
        assert "display_entity" in lagna and isinstance(lagna["display_entity"], str)
        assert "display_symbol" in lagna and isinstance(lagna["display_symbol"], str)
        assert "is_planetary_varga" in lagna

        if v_name in ("D2", "D3", "D30"):
            assert lagna["is_planetary_varga"] is True
        else:
            assert lagna["is_planetary_varga"] is False

        if v_name == "D2":
            assert lagna["hora_lord"] in ("Sun", "Moon")
            assert lagna["hora_symbol"] in ("☉", "☽")
            assert "Solar" in lagna["hora_polarity"] or "Lunar" in lagna["hora_polarity"]
        elif v_name == "D30":
            assert "bound_ruler" in lagna
            assert "bound_symbol" in lagna

        for p_name in PLANETS_ORDER:
            g = v_data["grahas"][p_name]
            assert "ruler" in g
            assert "ruler_symbol" in g
            assert "display_entity" in g
            assert "display_symbol" in g
            assert "is_planetary_varga" in g
            if v_name == "D2":
                assert g["hora_lord"] in ("Sun", "Moon")
                assert g["hora_symbol"] in ("☉", "☽")
                assert "Solar" in g["hora_polarity"] or "Lunar" in g["hora_polarity"]
            elif v_name == "D30":
                assert "bound_ruler" in g
                assert "bound_symbol" in g
