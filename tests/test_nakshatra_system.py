"""
Tests for Nakshatra Calculation Engine Toggle (ERNST_DHRUVA vs VIC_CHITRA)
and Master Graha Diagnostics Nakshatra payload integration.
"""

import pytest
from app import app
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.nakshatra_metadata import (
    NAKSHATRA_SYSTEM_DHRUVA,
    NAKSHATRA_SYSTEM_VIC,
    get_nakshatra_metadata,
    NAKSHATRA_METADATA
)

# Angelina Jolie birth data
ANGELINA_DATA = {
    "name": "Angelina Jolie",
    "year": 1975,
    "month": 6,
    "day": 4,
    "hour": 9,
    "minute": 9,
    "lat": 34.0522,
    "lon": -118.2437,
    "tz": -7.0
}


def test_nakshatra_metadata_table_completeness():
    """Verify that all 27 nakshatras have complete metadata with canonical devatas."""
    assert len(NAKSHATRA_METADATA) == 27
    for name, meta in NAKSHATRA_METADATA.items():
        assert meta["name"] == name
        assert meta["deity"]
        assert meta["ruler"] in ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        assert meta["nature"]
        assert meta["core_drive"]

    # Check key specific deities
    assert NAKSHATRA_METADATA["Chitra"]["deity"] == "Tvashtar"
    assert NAKSHATRA_METADATA["Rohini"]["deity"] == "Prajapati"
    assert NAKSHATRA_METADATA["Pushya"]["deity"] == "Brihaspati"
    assert NAKSHATRA_METADATA["Mula"]["deity"] == "Nirriti"


def test_ernst_dhruva_default_chart():
    """Verify default ERNST_DHRUVA system calculation in generate_kala_chart."""
    chart_dhruva = generate_kala_chart(
        name=ANGELINA_DATA["name"],
        year=ANGELINA_DATA["year"],
        month=ANGELINA_DATA["month"],
        day=ANGELINA_DATA["day"],
        hour=ANGELINA_DATA["hour"],
        minute=ANGELINA_DATA["minute"],
        latitude=ANGELINA_DATA["lat"],
        longitude=ANGELINA_DATA["lon"],
        timezone_offset=ANGELINA_DATA["tz"],
        nakshatra_system=NAKSHATRA_SYSTEM_DHRUVA
    )

    assert chart_dhruva["nakshatras"]["system"] == "ERNST_DHRUVA"
    assert chart_dhruva["nakshatras"]["zodiac"] == "Sidereal Equatorial"
    assert chart_dhruva["calculation_settings"]["nakshatra_system"] == "ERNST_DHRUVA"
    assert "Dhruva Galactic Center" in chart_dhruva["calculation_settings"]["ayanamsa_name"]

    # Verify Vimshottari at_birth has nakshatra_system recorded
    at_birth = chart_dhruva["vimshottari_dasha"]["at_birth"]
    assert at_birth["nakshatra_system"] == "ERNST_DHRUVA"
    assert isinstance(at_birth["moon_position_used"], float)
    assert 0.0 <= at_birth["moon_position_used"] < 360.0

    # Verify planetary evaluation has nakshatra payload for each graha
    pe_planets = chart_dhruva["planetary_evaluation"]["planets"]
    for graha in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        assert "nakshatra" in pe_planets[graha]
        n_data = pe_planets[graha]["nakshatra"]
        assert "name" in n_data
        assert "deity" in n_data
        assert "ruler" in n_data
        assert "nature" in n_data
        assert "core_drive" in n_data


def test_vic_chitra_chart_mode():
    """Verify VIC_CHITRA system calculation (Tropical Rasis + Lahiri Ecliptic Sidereal Nakshatras)."""
    chart_vic = generate_kala_chart(
        name=ANGELINA_DATA["name"],
        year=ANGELINA_DATA["year"],
        month=ANGELINA_DATA["month"],
        day=ANGELINA_DATA["day"],
        hour=ANGELINA_DATA["hour"],
        minute=ANGELINA_DATA["minute"],
        latitude=ANGELINA_DATA["lat"],
        longitude=ANGELINA_DATA["lon"],
        timezone_offset=ANGELINA_DATA["tz"],
        nakshatra_system=NAKSHATRA_SYSTEM_VIC
    )

    assert chart_vic["nakshatras"]["system"] == "VIC_CHITRA"
    assert "Lahiri" in chart_vic["nakshatras"]["zodiac"]
    assert chart_vic["calculation_settings"]["nakshatra_system"] == "VIC_CHITRA"
    assert "Lahiri / Chitra Paksha" in chart_vic["calculation_settings"]["ayanamsa_name"]

    # Tropical Rasi signs remain IDENTICAL (Integrated Approach)
    chart_dhruva = generate_kala_chart(
        name=ANGELINA_DATA["name"],
        year=ANGELINA_DATA["year"],
        month=ANGELINA_DATA["month"],
        day=ANGELINA_DATA["day"],
        hour=ANGELINA_DATA["hour"],
        minute=ANGELINA_DATA["minute"],
        latitude=ANGELINA_DATA["lat"],
        longitude=ANGELINA_DATA["lon"],
        timezone_offset=ANGELINA_DATA["tz"],
        nakshatra_system=NAKSHATRA_SYSTEM_DHRUVA
    )
    for graha in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        assert chart_vic["vargas"]["D1"]["grahas"][graha]["sign"] == chart_dhruva["vargas"]["D1"]["grahas"][graha]["sign"]

    # Sidereal Nakshatra positions differ between Equatorial RA vs Ecliptic Lahiri
    dhruva_moon_pos = chart_dhruva["nakshatras"]["grahas"]["Moon"]["sidereal_ra"]
    vic_moon_pos = chart_vic["nakshatras"]["grahas"]["Moon"]["sidereal_longitude"]
    # There is an astronomical difference between Equatorial RA and Ecliptic Longitude
    assert abs(dhruva_moon_pos - vic_moon_pos) > 0.001

    at_birth = chart_vic["vimshottari_dasha"]["at_birth"]
    assert at_birth["nakshatra_system"] == "VIC_CHITRA"
    assert isinstance(at_birth["moon_position_used"], float)
    assert 0.0 <= at_birth["moon_position_used"] < 360.0


def test_api_nakshatra_system_switch():
    """Verify that Flask /api/chart/<native_id> accepts ?nakshatra_system=VIC_CHITRA."""
    client = app.test_client()
    chart_id = "angelina-jolie"

    # 1. Default (or explicit ERNST_DHRUVA)
    res_dhruva = client.get(f"/api/chart/{chart_id}?nakshatra_system=ERNST_DHRUVA")
    assert res_dhruva.status_code == 200
    data_dhruva = res_dhruva.get_json()["data"]
    assert data_dhruva["nakshatras"]["system"] == "ERNST_DHRUVA"

    # 2. Vic DiCara mode
    res_vic = client.get(f"/api/chart/{chart_id}?nakshatra_system=VIC_CHITRA")
    assert res_vic.status_code == 200
    data_vic = res_vic.get_json()["data"]
    assert data_vic["nakshatras"]["system"] == "VIC_CHITRA"
    assert "Lahiri" in data_vic["calculation_settings"]["ayanamsa_name"]

    # 3. Planetary evaluation contains nakshatra objects in both
    for p in ["Sun", "Moon", "Jupiter"]:
        assert "nakshatra" in data_vic["planetary_evaluation"]["planets"][p]
        assert "deity" in data_vic["planetary_evaluation"]["planets"][p]["nakshatra"]
