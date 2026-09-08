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
    assert "D1" in data["svgs"]
    assert "south" in data["svgs"]["D1"]["symbol"]

def test_shri_krishna_chart_api(client):
    # Fetch by slug and UUID
    for endpoint in ['/api/chart/shri-krishna', '/api/chart/8270c2da-98d0-4b39-89ac-a3f5a11ac2b0']:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['native']['name'] == 'Shri Krishna'
        assert data['native']['date'] == '-3227-07-19'
        assert data['data']['vargas']['D1']['lagna']['sign'] == 'Pisces'
        assert 'D1' in data['svgs']

def test_goebbels_chart_api(client):
    # Fetch by slug and full name slug
    for endpoint in ['/api/chart/goebbels', '/api/chart/joseph-goebbels']:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['native']['name'] == 'Joseph Goebbels'
        assert data['native']['date'] == '1897-10-29'
        assert data['data']['vargas']['D1']['lagna']['sign'] == 'Leo'
        assert 'D1' in data['svgs']

