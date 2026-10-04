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
