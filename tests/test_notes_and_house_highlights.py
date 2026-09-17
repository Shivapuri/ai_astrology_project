import pytest
import json
from jyotish.draw_chart import generate_south_indian, generate_north_indian, generate_bhava_chalita_north
import app as flask_app
from jyotish import native_manager

def test_svg_house_attributes_south_indian():
    items = [
        {"type": "planet", "name": "Lagna", "sign": "Aries", "degree": 10, "minute": 20, "is_retrograde": False},
        {"type": "planet", "name": "Sun", "sign": "Leo", "degree": 15, "minute": 30, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    svg_str = generate_south_indian(items, varga_name="D1")
    
    # Assert all 12 houses are present on sign-cell-bg rects
    for h in range(1, 13):
        assert f'data-house="{h}"' in svg_str
    # Specifically for Aries (Lagna), it must be house 1
    assert 'data-id="Aries" data-house="1"' in svg_str
    # Leo is 5th sign from Aries, so it must be house 5
    assert 'data-id="Leo" data-house="5"' in svg_str

def test_svg_house_attributes_north_indian():
    items = [
        {"type": "planet", "name": "Lagna", "sign": "Taurus", "degree": 5, "minute": 10, "is_retrograde": False},
        {"type": "planet", "name": "Sun", "sign": "Taurus", "degree": 10, "minute": 20, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Taurus"}
    ]
    svg_str = generate_north_indian(items, varga_name="D1")
    
    # Assert all 12 houses are present on sign-cell-bg polygons
    for h in range(1, 13):
        assert f'data-house="{h}"' in svg_str
    assert 'data-id="Taurus" data-house="1"' in svg_str

def test_svg_house_attributes_bhava_chalita():
    # Mock 12 bhavas
    bhavas = []
    for i in range(12):
        bhavas.append({
            "cusp": i * 30.0 + 15.0,
            "planets": ["Sun"] if i == 0 else []
        })
    svg_str = generate_bhava_chalita_north(bhavas)
    for h in range(1, 13):
        assert f'data-house="{h}"' in svg_str

def test_notes_api_endpoints():
    client = flask_app.app.test_client()
    natives = native_manager.load_natives(flask_app.CHARTS_FILE)
    assert len(natives) > 0
    test_native = natives[0]
    native_id = test_native["id"]

    # 1. GET notes
    res = client.get(f'/api/native/{native_id}/notes')
    assert res.status_code == 200
    data = res.get_json()
    assert "general" in data
    assert "houses" in data

    # 2. POST notes
    test_payload = {
        "general": "Integration test general note",
        "houses": {
            "1": "Ascendant Tanu note",
            "10": "Karma career note"
        }
    }
    res_post = client.post(f'/api/native/{native_id}/notes', json=test_payload)
    assert res_post.status_code == 200
    res_data = res_post.get_json()
    assert res_data.get("success") is True
    assert res_data["notes"]["general"] == "Integration test general note"
    assert res_data["notes"]["houses"]["1"] == "Ascendant Tanu note"

    # 3. Verify persistence with GET
    res_verify = client.get(f'/api/native/{native_id}/notes')
    assert res_verify.status_code == 200
    v_data = res_verify.get_json()
    assert v_data["general"] == "Integration test general note"
    assert v_data["houses"]["1"] == "Ascendant Tanu note"
    assert v_data["houses"]["10"] == "Karma career note"

    # 4. 404 for invalid native
    res_404 = client.get('/api/native/non-existent-id/notes')
    assert res_404.status_code == 404

def test_frontend_house_highlights_and_notes(page):
    import urllib.request
    try:
        urllib.request.urlopen("http://127.0.0.1:5001/api/natives", timeout=2)
    except Exception:
        pytest.skip("Flask server not running on 5001")

    # Navigate to app
    page.goto("http://127.0.0.1:5001", wait_until="domcontentloaded")
    page.wait_for_selector(".grid-cell[data-widget='chart']", timeout=10000)

    # 1. Test Kendra toggle
    kendra_btn = page.locator(".grid-cell[data-widget='chart'] .btn-highlight-kendra").first
    assert kendra_btn.is_visible()
    kendra_btn.click()
    page.wait_for_timeout(300)

    # Assert kendra button has active class and cells 1, 4, 7, 10 have house-kendra
    assert "active" in (kendra_btn.get_attribute("class") or "")
    h1_cell = page.locator(".grid-cell[data-widget='chart'] .sign-cell-bg[data-house='1']").first
    assert "house-kendra" in (h1_cell.get_attribute("class") or "")

    # Clear button should now be visible
    clear_btn = page.locator(".grid-cell[data-widget='chart'] .btn-highlight-clear").first
    assert clear_btn.is_visible()
    clear_btn.click()
    page.wait_for_timeout(300)
    assert "house-kendra" not in (h1_cell.get_attribute("class") or "")

    # 2. Test Open Notes button
    notes_btn = page.locator(".grid-cell[data-widget='chart'] .btn-open-notes").first
    assert notes_btn.is_visible()
    notes_btn.click()
    page.wait_for_timeout(500)

    # Verify notes widget container is rendered
    notes_widget = page.locator(".widget-notes").first
    assert notes_widget.is_visible()

    # Verify General note card and 12 house cards exist
    assert page.locator(".notes-card.general-card").first.is_visible()
    assert page.locator(".notes-card.house-card[data-house='1']").first.is_visible()
    assert page.locator(".notes-card.house-card[data-house='12']").first.is_visible()

    # 3. Test Filter pills in notes widget
    filter_kendra = page.locator(".notes-filter-btn[data-filter='kendra']").first
    filter_kendra.click()
    page.wait_for_timeout(300)
    # H1 and H4 should be visible, H2 (not kendra) should be hidden
    assert page.locator(".notes-card.house-card[data-house='1']").first.is_visible()
    assert not page.locator(".notes-card.house-card[data-house='2']").first.is_visible()

    filter_all = page.locator(".notes-filter-btn[data-filter='all']").first
    filter_all.click()
    page.wait_for_timeout(300)
    assert page.locator(".notes-card.house-card[data-house='2']").first.is_visible()

