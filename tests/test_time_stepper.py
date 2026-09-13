import pytest
import os
import json
from jyotish import generate_jyotish
from jyotish import native_manager
import app

def test_generate_kala_chart_subsecond_precision():
    # Calling generate_kala_chart with second=0 vs second=30
    chart_0 = generate_jyotish.generate_kala_chart(
        name="Test Native",
        year=1990,
        month=5,
        day=15,
        hour=12,
        minute=0,
        second=0,
        latitude=51.5,
        longitude=-0.12,
        timezone_offset=0.0
    )
    chart_30 = generate_jyotish.generate_kala_chart(
        name="Test Native",
        year=1990,
        month=5,
        day=15,
        hour=12,
        minute=0,
        second=30,
        latitude=51.5,
        longitude=-0.12,
        timezone_offset=0.0
    )

    # In 30 seconds of time, Earth rotates 7.5 arcminutes (0.125 degrees)
    asc_0 = chart_0["vargas"]["D1"]["lagna"]["longitude"]
    asc_30 = chart_30["vargas"]["D1"]["lagna"]["longitude"]
    diff = (asc_30 - asc_0) % 360.0
    assert 0.05 <= diff <= 0.20, f"Expected non-zero ascendant shift in 30s, got {diff:.4f}"
    assert chart_30["subject_info"]["birth_datetime"].endswith(":30")

def test_compute_chart_data_offsets_and_rollover():
    native = {
        "id": "test-native-1",
        "name": "Midnight Native",
        "date": "01/01/2000",
        "time": "00:05:00",
        "lat": 51.5074,
        "lon": -0.1278,
        "tz": "+00:00"
    }

    # Step back 10 minutes (-600 seconds) -> should roll to 31/12/1999 23:55:00
    res_back = app.compute_chart_data(native, offset_seconds=-600)
    info_back = res_back["preview_info"]
    assert info_back["is_preview"] is True
    assert info_back["preview_time"] == "23:55:00"
    assert info_back["preview_date"] == "31/12/1999"
    assert info_back["offset_seconds"] == -600

    # Step forward 1 hour (+3600 seconds) -> should be 01/01/2000 01:05:00
    res_fwd = app.compute_chart_data(native, offset_seconds=3600)
    info_fwd = res_fwd["preview_info"]
    assert info_fwd["is_preview"] is True
    assert info_fwd["preview_time"] == "01:05:00"
    assert info_fwd["preview_date"] == "01/01/2000"
    assert info_fwd["offset_seconds"] == 3600

def test_api_chart_preview_route():
    client = app.app.test_client()
    natives = native_manager.load_natives("database/Charts.jsonl")
    assert len(natives) > 0, "Charts.jsonl should have at least one native"
    first_native = natives[0]
    native_id = first_native["id"]

    # Request with 60 seconds offset
    res = client.get(f"/api/chart/{native_id}?offset_seconds=60")
    assert res.status_code == 200
    json_data = res.get_json()

    assert json_data["is_preview"] is True
    assert json_data["preview_offset_seconds"] == 60
    assert "data" in json_data
    assert "svgs" in json_data
    assert "D1" in json_data["svgs"]
    assert "D9" in json_data["svgs"]
