"""
tests/test_harmonic_overlay.py
Unit tests for Degree-Specific Harmonic Varga Overlay Engine (D9, D7, D10 projected onto D1).
"""

import pytest
from jyotish.report.interpretation_engine import compute_harmonic_overlays


def test_harmonic_degree_projection_d9():
    """
    Verify continuous harmonic longitude projection for D9:
    Formula: lambda_D9 = (lambda_D1 * 9) % 360.
    Natal Sun at 10.0° Aries (10.0° longitude) projects to 90.0° (0.0° Cancer).
    Natal Moon at 91.0° (1.0° Cancer).
    Angular separation = 1.0° <= 3°20' (3.3333°).
    Must trigger harmonic contact!
    """
    mock_vargas = {"D1": {"lagna": {"longitude": 0.0}, "grahas": {}}}
    d1_lons = {
        "Sun": 10.0,
        "Moon": 91.0
    }

    res = compute_harmonic_overlays(mock_vargas, d1_longitudes=d1_lons)
    contacts = res["contacts"]

    d9_sun_moon = [
        c for c in contacts
        if c["harmonic_chart"] == "D9" and c["harmonic_planet"] == "Sun" and c["natal_target"] == "Moon"
    ]
    assert len(d9_sun_moon) == 1
    assert d9_sun_moon[0]["harmonic_degree"] == 90.0
    assert d9_sun_moon[0]["natal_degree"] == 91.0
    assert d9_sun_moon[0]["orb_separation"] == 1.0


def test_harmonic_degree_projection_d7():
    """
    Verify continuous harmonic longitude projection for D7:
    Formula: lambda_D7 = (lambda_D1 * 7) % 360.
    Natal Venus at 20.0° (20.0° Aries).
    D7 projection = (20.0 * 7) % 360 = 140.0° (20.0° Leo).
    Natal Jupiter at 141.5° (21.5° Leo).
    Separation = 1.5° <= 3.3333°.
    Must trigger harmonic contact!
    """
    mock_vargas = {"D1": {"lagna": {"longitude": 0.0}, "grahas": {}}}
    d1_lons = {
        "Venus": 20.0,
        "Jupiter": 141.5
    }

    res = compute_harmonic_overlays(mock_vargas, d1_longitudes=d1_lons)
    contacts = res["contacts"]

    d7_venus_jup = [
        c for c in contacts
        if c["harmonic_chart"] == "D7" and c["harmonic_planet"] == "Venus" and c["natal_target"] == "Jupiter"
    ]
    assert len(d7_venus_jup) == 1
    assert d7_venus_jup[0]["harmonic_degree"] == 140.0
    assert d7_venus_jup[0]["orb_separation"] == 1.5


def test_harmonic_degree_projection_d10():
    """
    Verify continuous harmonic longitude projection for D10:
    Formula: lambda_D10 = (lambda_D1 * 10) % 360.
    Natal Mars at 15.0° (15.0° Aries).
    D10 projection = (15.0 * 10) % 360 = 150.0° (0.0° Virgo).
    Natal Saturn at 152.0° (2.0° Virgo).
    Separation = 2.0° <= 3.3333°.
    Must trigger harmonic contact!
    """
    mock_vargas = {"D1": {"lagna": {"longitude": 0.0}, "grahas": {}}}
    d1_lons = {
        "Mars": 15.0,
        "Saturn": 152.0
    }

    res = compute_harmonic_overlays(mock_vargas, d1_longitudes=d1_lons)
    contacts = res["contacts"]

    d10_mars_sat = [
        c for c in contacts
        if c["harmonic_chart"] == "D10" and c["harmonic_planet"] == "Mars" and c["natal_target"] == "Saturn"
    ]
    assert len(d10_mars_sat) == 1
    assert d10_mars_sat[0]["harmonic_degree"] == 150.0
    assert d10_mars_sat[0]["orb_separation"] == 2.0


def test_harmonic_orb_boundary():
    """
    Verify that contacts > 3°20' (3.3333°) are NOT flagged.
    Natal Sun at 10.0°, D9 projection = 90.0°.
    Natal Mars at 95.0°. Separation = 5.0° > 3.3333°.
    Should NOT trigger contact!
    """
    mock_vargas = {"D1": {"lagna": {"longitude": 0.0}, "grahas": {}}}
    d1_lons = {
        "Sun": 10.0,
        "Mars": 95.0
    }

    res = compute_harmonic_overlays(mock_vargas, d1_longitudes=d1_lons)
    contacts = res["contacts"]

    d9_sun_mars = [
        c for c in contacts
        if c["harmonic_chart"] == "D9" and c["harmonic_planet"] == "Sun" and c["natal_target"] == "Mars"
    ]
    assert len(d9_sun_mars) == 0
