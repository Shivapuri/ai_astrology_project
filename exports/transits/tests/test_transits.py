import pytest
from jyotish import native_manager
from jyotish import generate_jyotish
from jyotish.transits.transits import calculate_transits, get_transit_aspects
from jyotish.draw_chart import generate_transit_biwheel, parse_varga_data
from app import app, CHARTS_FILE

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_transit_calculation():
    all_natives = native_manager.load_natives(CHARTS_FILE)
    assert len(all_natives) > 0
    native = all_natives[0]

    natal = generate_jyotish.generate_kala_chart(
        name=native['name'],
        year=1990, month=1, day=1, hour=12, minute=0,
        latitude=float(native['lat']), longitude=float(native['lon']),
        timezone_offset=0.0
    )

    # Test Ernst Dhruva
    res_dhruva = calculate_transits(
        natal_chart=natal,
        transit_year=2026, transit_month=10, transit_day=1,
        transit_hour=12, transit_minute=0,
        nakshatra_system="ERNST_DHRUVA"
    )
    assert "transit_planets" in res_dhruva
    assert len(res_dhruva["transit_planets"]) == 9
    assert "Jupiter" in res_dhruva["transit_planets"]
    assert "house_from_lagna" in res_dhruva["transit_planets"]["Jupiter"]
    assert "house_from_moon" in res_dhruva["transit_planets"]["Jupiter"]

    # Test Vic Chitra
    res_chitra = calculate_transits(
        natal_chart=natal,
        transit_year=2026, transit_month=10, transit_day=1,
        transit_hour=12, transit_minute=0,
        nakshatra_system="VIC_CHITRA"
    )
    assert "transit_planets" in res_chitra

def test_transit_biwheel_svg():
    all_natives = native_manager.load_natives(CHARTS_FILE)
    native = all_natives[0]

    natal = generate_jyotish.generate_kala_chart(
        name=native['name'],
        year=1990, month=1, day=1, hour=12, minute=0,
        latitude=float(native['lat']), longitude=float(native['lon']),
        timezone_offset=0.0
    )

    transit_res = calculate_transits(
        natal_chart=natal,
        transit_year=2026, transit_month=10, transit_day=1,
        transit_hour=12, transit_minute=0
    )

    natal_d1_items = parse_varga_data(natal["vargas"]["D1"])
    transit_d1_items = parse_varga_data(transit_res["transit_chart"]["vargas"]["D1"])

    svg = generate_transit_biwheel(
        inner_items=natal_d1_items,
        outer_items=transit_d1_items,
        active_aspects=transit_res["active_aspects"]
    )
    assert "<svg" in svg
    assert "Natal · Transit" in svg
    assert "transit-aspect-lines" in svg
    assert "outer-planets-group" in svg

    # Redesigned Adius-style layout: unshaded canvas, expanded inner hub (r=56), flat house ring (r=72)
    assert '<circle class="interactive-center-circle" cx="0" cy="0" r="56"' in svg
    assert '<circle cx="0" cy="0" r="72"' in svg
    assert 'class="house-bg house-kendra"' not in svg
    assert '<path class="house-bg"' in svg
    assert 'fill="none"' in svg
    assert '<g class="inner-planet-ticks">' in svg
    assert 'class="angle-ac-badge"' in svg
    assert 'stroke-dasharray="1,2.5"' in svg

def test_transit_api_endpoint(client):
    all_natives = native_manager.load_natives(CHARTS_FILE)
    native = all_natives[0]
    nid = native['id']

    resp = client.get(f'/api/chart/{nid}/transit?transit_date=01/10/2026&transit_time=12:00:00')
    assert resp.status_code == 200
    data = resp.get_json()
    assert "svg" in data
    assert "transit_planets" in data
    assert "active_aspects" in data
    assert "transit_time_info" in data


def test_transit_custom_orbs_and_motion(client):
    all_natives = native_manager.load_natives(CHARTS_FILE)
    native = all_natives[0]
    nid = native['id']

    # Narrow Navamsha orb (3.3333°)
    resp_narrow = client.get(f'/api/chart/{nid}/transit?transit_date=2026-10-15&transit_time=12:00:00&orb=3.3333')
    assert resp_narrow.status_code == 200
    data_narrow = resp_narrow.get_json()
    assert data_narrow["orb"] == 3.3333

    # Wide Parashari orb (10.0°) should return equal or more active aspects
    resp_wide = client.get(f'/api/chart/{nid}/transit?transit_date=2026-10-15&transit_time=12:00:00&orb=10.0')
    assert resp_wide.status_code == 200
    data_wide = resp_wide.get_json()
    assert data_wide["orb"] == 10.0
    assert len(data_wide["active_aspects"]) >= len(data_narrow["active_aspects"])

    # Check motion status fields on aspects
    for asp in data_wide["active_aspects"]:
        assert "motion_status" in asp
        assert asp["motion_status"] in ("Applying", "Separating")
        assert "is_applying" in asp

def test_transit_pure_speed_and_station_calculus():
    """Verify Hemisphere A pure calculus: zero HTML/colors, strict types."""
    all_natives = native_manager.load_natives(CHARTS_FILE)
    native = all_natives[0]
    natal = generate_jyotish.generate_kala_chart(
        name=native['name'],
        year=1990, month=1, day=1, hour=12, minute=0,
        latitude=float(native['lat']), longitude=float(native['lon']),
        timezone_offset=0.0
    )

    transit_res = calculate_transits(
        natal_chart=natal,
        transit_year=2026, transit_month=10, transit_day=26,
        transit_hour=12, transit_minute=0
    )

    planets = transit_res["transit_planets"]
    for p_name, p_data in planets.items():
        assert isinstance(p_data["daily_speed"], float)
        assert isinstance(p_data["speed_ratio"], float)
        assert isinstance(p_data["is_stationary"], bool)
        assert p_data["station_type"] in (None, "SR", "SD")
        assert isinstance(p_data["motion_state"], str)
        assert isinstance(p_data["gati_sanskrit"], str)

        # Zero HTML or hex leakage
        for k, v in p_data.items():
            if isinstance(v, str):
                assert "<" not in v and ">" not in v
                assert "#" not in v

    # Verify enriched aspects
    for asp in transit_res["active_aspects"]:
        assert isinstance(asp["aspecting_is_stationary"], bool)
        assert asp["aspecting_station_type"] in (None, "SR", "SD")
        assert isinstance(asp["aspecting_speed_ratio"], float)
        assert isinstance(asp["intensity_weight"], float)
        assert asp["intensity_weight"] >= 0.0

def test_milestone_scanner_detection():
    """Verify coarse-to-fine milestone scanner detects stations, exact hits, and ingresses."""
    from jyotish.transits.milestone_scanner import scan_transit_milestones
    all_natives = native_manager.load_natives(CHARTS_FILE)
    native = all_natives[0]
    natal = generate_jyotish.generate_kala_chart(
        name=native['name'],
        year=1990, month=1, day=1, hour=12, minute=0,
        latitude=float(native['lat']), longitude=float(native['lon']),
        timezone_offset=0.0
    )

    res = scan_transit_milestones(
        natal_chart=natal,
        start_year=2026, start_month=10, start_day=26,
        days_back=60, days_forward=120
    )

    assert "milestones" in res
    assert "upcoming_stations" in res
    assert len(res["milestones"]) > 0

    categories = {m["category"] for m in res["milestones"]}
    # Should detect at least EXACT_ASPECT and stations
    assert "EXACT_ASPECT" in categories

    for m in res["milestones"]:
        assert m["tier"] in (1, 2, 3)
        assert m["category"] in ("NATAL_STATION", "EXACT_ASPECT", "SKY_STATION", "SIGN_INGRESS")
        assert "timestamp_utc" in m
        assert "jump_date" in m
        assert "jump_time" in m
        assert "description" in m
        if m["category"] == "EXACT_ASPECT":
            assert m["orb_at_event"] == 0.0
            assert m["pass_number"] is not None
            assert m["total_passes"] is not None
            assert m["pass_number"] <= m["total_passes"]

    # Test upcoming stations structure
    for st in res["upcoming_stations"]:
        assert st["station_type"] in ("SR", "SD")
        assert "longitude" in st
        assert "jump_date" in st
        assert "tooltip" in st

def test_transit_biwheel_svg_upgrades():
    """Verify applying vs separating lines, SR/SD badges, and station pins in SVG."""
    all_natives = native_manager.load_natives(CHARTS_FILE)
    native = all_natives[0]
    natal = generate_jyotish.generate_kala_chart(
        name=native['name'],
        year=1990, month=1, day=1, hour=12, minute=0,
        latitude=float(native['lat']), longitude=float(native['lon']),
        timezone_offset=0.0
    )

    transit_res = calculate_transits(
        natal_chart=natal,
        transit_year=2026, transit_month=10, transit_day=26,
        transit_hour=12, transit_minute=0
    )

    natal_d1_items = parse_varga_data(natal["vargas"]["D1"])
    transit_d1_items = parse_varga_data(transit_res["transit_chart"]["vargas"]["D1"])
    for it in transit_d1_items:
        p_nm = it.get("name")
        if p_nm in transit_res["transit_planets"]:
            it.update(transit_res["transit_planets"][p_nm])

    upcoming_sample = [{
        "planet": "Saturn",
        "station_type": "SD",
        "longitude": 7.5,
        "sign": "Aries",
        "degree": 7,
        "minute": 30,
        "jump_date": "2026-12-10",
        "jump_time": "12:00:00",
        "tooltip": "Upcoming Saturn SD at 7°30' Aries"
    }]

    svg = generate_transit_biwheel(
        inner_items=natal_d1_items,
        outer_items=transit_d1_items,
        active_aspects=transit_res["active_aspects"],
        upcoming_stations=upcoming_sample
    )

    # Check station pins
    assert "upcoming-stations-layer" in svg
    assert "station-pin" in svg
    assert 'data-jump-date="2026-12-10"' in svg

    # Check applying/separating aspect lines
    if transit_res["active_aspects"]:
        assert "transit-aspect-lines-layer" in svg
        assert 'data-applying=' in svg

def test_transit_milestones_api_endpoint(client):
    """Verify /api/chart/<native_id>/transit/milestones endpoint."""
    all_natives = native_manager.load_natives(CHARTS_FILE)
    native = all_natives[0]
    nid = native['id']

    resp = client.get(f'/api/chart/{nid}/transit/milestones?transit_date=2026-10-26&days_back=60&days_forward=120')
    assert resp.status_code == 200
    data = resp.get_json()
    assert "milestones" in data
    assert "upcoming_stations" in data
    assert "scan_meta" in data
    assert len(data["milestones"]) > 0
