import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Astra" in response.data or b"Charts" in response.data

def test_countries_api(client):
    response = client.get('/api/countries')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    # the response is typically a list mapping country code to name

def test_chart_api(client):
    # Fetch a known ID or the default ID 589fabff-bf49-405a-9372-6d9566bf6955
    response = client.get('/api/chart/589fabff-bf49-405a-9372-6d9566bf6955')
    if response.status_code == 404 or b"error" in response.data:
        pytest.skip("Default chart ID not found, skipping this test.")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "data" in data
    assert "svgs" in data
    assert "vargas" in data["data"]
    assert "yogas" in data["data"]
    assert "summary" in data["data"]["yogas"]
    assert "D1" in data["svgs"]
    assert "south" in data["svgs"]["D1"]["symbol"]

def test_chart_api_notation_and_modes(client):
    response = client.get('/api/chart/adolf-hitler?mode=english&d10_mode=direct&nakshatra_system=VIC_CHITRA')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "english" in data["svgs"]["D1"]
    assert "Su" in data["svgs"]["D1"]["english"]["south"]
    assert "Su" in data["svgs"]["D1"]["south"]
    # Nakshatra system VIC_CHITRA
    assert data["data"]["calculation_settings"]["nakshatra_system"] == "VIC_CHITRA"
    assert data["data"]["nakshatras"]["system"] == "VIC_CHITRA"
    # D10 mode direct
    assert data["data"]["calculation_settings"]["d10_mode"] == "direct"

def test_shri_krishna_chart_api(client):
    # Fetch by slug and UUID
    for endpoint in ['/api/chart/shri-krishna', '/api/chart/8270c2da-98d0-4b39-89ac-a3f5a11ac2b0']:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Shri Krishna' in data['native']['name']
        assert data['native']['date'] in ['28/08/-3255', '-3255-08-28']
        assert data['data']['vargas']['D1']['lagna']['sign'] == 'Taurus'
        assert 'D1' in data['svgs']

def test_goebbels_chart_api(client):
    # Fetch by slug and full name slug
    for endpoint in ['/api/chart/goebbels', '/api/chart/joseph-goebbels']:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['native']['name'] == 'Joseph Goebbels'
        assert data['native']['date'] in ['29/10/1897', '1897-10-29']
        assert data['data']['vargas']['D1']['lagna']['sign'] == 'Leo'
        assert 'D1' in data['svgs']

def test_mahaprabhuji_chart_api(client):
    for endpoint in ['/api/chart/mahaprabhuji', '/api/chart/deep-narayan-mahaprabhuji']:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['native']['name'] == 'Bhagwan Sri Deep Narayan Mahaprabhuji'
        assert data['native']['date'] in ['07/11/1828', '1828-11-07']
        assert data['data']['vargas']['D1']['lagna']['sign'] == 'Libra'
        assert 'D1' in data['svgs']

def test_date_standardization_helpers():
    from jyotish.native_manager import parse_date_to_parts, to_standard_date
    
    # 1. Standard DD/MM/YYYY
    assert parse_date_to_parts("10/11/1983") == (1983, 11, 10)
    assert to_standard_date("10/11/1983") == "10/11/1983"
    
    # 2. ISO YYYY-MM-DD
    assert parse_date_to_parts("1983-11-10") == (1983, 11, 10)
    assert to_standard_date("1983-11-10") == "10/11/1983"
    
    # 3. Dots DD.MM.YYYY
    assert parse_date_to_parts("14.06.1946") == (1946, 6, 14)
    assert to_standard_date("14.06.1946") == "14/06/1946"
    
    # 4. Slashes YYYY/MM/DD
    assert parse_date_to_parts("2018/01/08") == (2018, 1, 8)
    assert to_standard_date("2018/01/08") == "08/01/2018"
    
    # 5. Astronomical BCE dates
    assert parse_date_to_parts("-3255-08-28") == (-3255, 8, 28)
    assert to_standard_date("-3255-08-28") == "28/08/-3255"
    assert parse_date_to_parts("28/08/-3255") == (-3255, 8, 28)
    assert to_standard_date("28/08/-3255") == "28/08/-3255"

def test_native_crud_api(client):
    # 1. Add new native with standard DD/MM/YYYY date
    payload = {
        "name": "Unit Test Native",
        "date": "25/12/1990",
        "time": "14:30:00",
        "lat": 28.6139,
        "lon": 77.2090,
        "tz": "+05:30",
        "place": "New Delhi",
        "country": "IN",
        "name_sound_value": 3,
        "notes": "Test native for API verification"
    }
    res_add = client.post('/api/add_native', json=payload)
    assert res_add.status_code == 200
    added = json.loads(res_add.data)
    assert added["name"] == "Unit Test Native"
    assert added["date"] == "25/12/1990"
    native_id = added["id"]
    
    try:
        # 2. Get native by ID
        res_get = client.get(f'/api/native/{native_id}')
        assert res_get.status_code == 200
        fetched = json.loads(res_get.data)
        assert fetched["name"] == "Unit Test Native"
        assert fetched["date"] == "25/12/1990"
        
        # 3. Update native with new DD/MM/YYYY date and details
        update_payload = {
            "name": "Unit Test Native Updated",
            "date": "26/12/1990",
            "time": "15:00:00",
            "lat": 28.7,
            "lon": 77.3,
            "notes": "Updated notes"
        }
        res_update = client.post(f'/api/update_native/{native_id}', json=update_payload)
        assert res_update.status_code == 200
        updated = json.loads(res_update.data)
        assert updated["name"] == "Unit Test Native Updated"
        assert updated["date"] == "26/12/1990"
        assert updated["notes"] == "Updated notes"
        
        # 4. Generate chart for the updated native
        res_chart = client.get(f'/api/chart/{native_id}')
        assert res_chart.status_code == 200
        chart_data = json.loads(res_chart.data)
        assert chart_data["native"]["name"] == "Unit Test Native Updated"
        assert chart_data["native"]["date"] == "26/12/1990"
        assert "D1" in chart_data["data"]["vargas"]
        
    finally:
        # 5. Clean up: Delete native
        res_del = client.post(f'/api/delete_native/{native_id}')
        assert res_del.status_code == 200
        del_data = json.loads(res_del.data)
        assert del_data.get("success") is True
        
        # Confirm deleted
        res_check = client.get(f'/api/native/{native_id}')
        assert res_check.status_code == 404


def test_biwheel_endpoints(client):
    # Test Angelina Jolie chart has biwheel SVGs
    res = client.get('/api/chart/angelina-jolie')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert "svgs" in data
    assert "D1" in data["svgs"]
    assert "biwheel" in data["svgs"]["D1"]
    assert "biwheel" in data["svgs"]["D1"]["symbol"]
    assert "biwheel" in data["svgs"]["D9"]["symbol"]
    assert '<svg' in data["svgs"]["D1"]["symbol"]["biwheel"]

    # Test dynamic biwheel endpoint
    res_bi = client.get('/api/chart/angelina-jolie/biwheel?inner=D1&outer=D9')
    assert res_bi.status_code == 200
    bi_data = json.loads(res_bi.data)
    assert "svg" in bi_data
    assert bi_data["inner"] == "D1"
    assert bi_data["outer"] == "D9"
    assert '<svg' in bi_data["svg"]
    assert 'Bi-Wheel' in bi_data["svg"]


def test_natives_list_and_dropdown_exclusivity(client):
    # 1. Verify /api/natives returns all natives
    res = client.get('/api/natives')
    assert res.status_code == 200
    natives = json.loads(res.data)
    names = [n['name'] for n in natives]
    assert "Adolf Hitler" in names
    assert "Heinrich Himmler" in names
    assert "Jeffrey Dahmer" in names

    # 2. Verify top dropdown on index page does NOT include Criminals by default
    res_idx = client.get('/')
    assert res_idx.status_code == 200
    html = res_idx.data.decode('utf-8')
    select_section = html.split('id="nativeSelect"')[1].split('</select>')[0]
    assert "Adolf Hitler" not in select_section
    assert "Heinrich Himmler" not in select_section
    assert "Jeffrey Dahmer" not in select_section

    # 3. Verify Open Chart modal components exist in HTML
    assert 'id="openChartModal"' in html
    assert 'id="btnOpenChartModal"' in html
    assert 'id="openChartSearchInput"' in html


def test_hitler_himmler_dahmer_chart_api(client):
    targets = [
        ('adolf-hitler', 'Libra', 'Adolf Hitler'),
        ('heinrich-himmler', 'Aquarius', 'Heinrich Himmler'),
        ('jeffrey-dahmer', 'Libra', 'Jeffrey Dahmer')
    ]
    for cid, expected_lagna, expected_name in targets:
        res = client.get(f'/api/chart/{cid}')
        assert res.status_code == 200
        data = json.loads(res.data)
        assert data['native']['name'] == expected_name
        assert data['data']['vargas']['D1']['lagna']['sign'] == expected_lagna
        assert 'D1' in data['svgs']
        assert 'D9' in data['svgs']
        assert 'D10' in data['svgs']


def test_toggle_dropdown_api(client):
    # Toggle Hitler in_dropdown from false to true and back
    res1 = client.post('/api/native/adolf-hitler/toggle_dropdown')
    assert res1.status_code == 200
    data1 = json.loads(res1.data)
    assert data1['id'] == 'adolf-hitler'
    assert data1['in_dropdown'] is True

    # Toggle back to false
    res2 = client.post('/api/native/adolf-hitler/toggle_dropdown')
    assert res2.status_code == 200
    data2 = json.loads(res2.data)
    assert data2['id'] == 'adolf-hitler'
    assert data2['in_dropdown'] is False


def test_lazy_chart_svg_api(client):
    # 1. South Indian JSON response
    res = client.get('/api/chart/adolf-hitler/svg?varga=D1&mode=symbol&style=south')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['varga'] == 'D1'
    assert data['mode'] == 'symbol'
    assert data['style'] == 'south'
    assert '<svg' in data['svg']

    # 2. Raw SVG response with Accept header
    res_raw = client.get('/api/chart/adolf-hitler/svg?varga=D1&mode=symbol&style=south', headers={'Accept': 'image/svg+xml'})
    assert res_raw.status_code == 200
    assert res_raw.mimetype == 'image/svg+xml'
    assert b'<svg' in res_raw.data

    # 3. North Indian JSON response
    res_north = client.get('/api/chart/adolf-hitler/svg?varga=D9&mode=symbol&style=north')
    assert res_north.status_code == 200
    data_north = json.loads(res_north.data)
    assert data_north['varga'] == 'D9'
    assert '<svg' in data_north['svg']

    # 4. Circular Chart JSON response with Moon root
    res_circ = client.get('/api/chart/adolf-hitler/svg?varga=D1&mode=symbol&root=Moon&style=circular')
    assert res_circ.status_code == 200
    data_circ = json.loads(res_circ.data)
    assert data_circ['root'] == 'Moon'
    assert '<svg' in data_circ['svg']

    # 5. Bi-Wheel Chart JSON response
    res_bi = client.get('/api/chart/adolf-hitler/svg?varga=D1&outer=D10&mode=symbol&style=biwheel')
    assert res_bi.status_code == 200
    data_bi = json.loads(res_bi.data)
    assert '<svg' in data_bi['svg']

    # 6. All styles combined JSON response
    res_all = client.get('/api/chart/adolf-hitler/svg?varga=D1&mode=symbol&root=Lagna&style=all')
    assert res_all.status_code == 200
    data_all = json.loads(res_all.data)
    assert 'svgs' in data_all
    assert 'south' in data_all['svgs']
    assert 'north' in data_all['svgs']
    assert 'circular' in data_all['svgs']
    assert 'biwheel' in data_all['svgs']

    # 7. Error handling
    assert client.get('/api/chart/nonexistent-id/svg').status_code == 404
    assert client.get('/api/chart/adolf-hitler/svg?varga=D99').status_code == 404





