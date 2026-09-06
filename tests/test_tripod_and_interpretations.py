import json
import pytest
import urllib.request
from playwright.sync_api import Page, expect

from jyotish import draw_chart, generate_jyotish

FLASK_URL = "http://127.0.0.1:5001"
CHART_ID = "angelina-jolie"

def is_server_running(url=FLASK_URL):
    try:
        urllib.request.urlopen(url)
        return True
    except Exception:
        return False

@pytest.fixture(scope="module")
def aj_data():
    return generate_jyotish.generate_kala_chart(
        name="Angelina Jolie",
        year=1975,
        month=6,
        day=4,
        hour=9,
        minute=9,
        latitude=34.0522,
        longitude=-118.2437,
        timezone_offset=-7.0,
        name_sound_value=0
    )

def test_south_indian_roots(aj_data):
    items = draw_chart.parse_varga_data(aj_data["vargas"]["D1"])
    
    # Lagna
    svg_lagna = draw_chart.generate_south_indian(items, mode="symbol", varga_name="D1", root_planet="Lagna")
    assert "Asc" in svg_lagna
    assert "South Indian" in svg_lagna

    # Chandra Lagna
    svg_moon = draw_chart.generate_south_indian(items, mode="symbol", varga_name="D1", root_planet="Moon")
    assert "CL" in svg_moon
    assert "Chandra Lagna" in svg_moon
    assert "H1" in svg_moon

    # Surya Lagna
    svg_sun = draw_chart.generate_south_indian(items, mode="symbol", varga_name="D1", root_planet="Sun")
    assert "SL" in svg_sun
    assert "Surya Lagna" in svg_sun
    assert "H1" in svg_sun

def test_north_indian_roots(aj_data):
    items = draw_chart.parse_varga_data(aj_data["vargas"]["D1"])
    
    # Moon in Cancer for Angelina Jolie -> Chandra Lagna should anchor Cancer (Sign 4) at top diamond
    svg_moon = draw_chart.generate_north_indian(items, mode="symbol", varga_name="D1", root_planet="Moon")
    assert "Chandra Lagna" in svg_moon
    assert 'data-type="sign" data-id="Cancer"' in svg_moon

    # Sun in Taurus for Angelina Jolie -> Surya Lagna should anchor Taurus (Sign 2) at top diamond
    svg_sun = draw_chart.generate_north_indian(items, mode="symbol", varga_name="D1", root_planet="Sun")
    assert "Surya Lagna" in svg_sun
    assert 'data-type="sign" data-id="Taurus"' in svg_sun

def test_circular_roots(aj_data):
    items = draw_chart.parse_varga_data(aj_data["vargas"]["D1"])
    ayanamsha = aj_data["astronomy"]["equatorial_ayanamsa_value"]

    svg_moon = draw_chart.generate_circular_chart(items, mode="symbol", varga_name="D1", ayanamsha=ayanamsha, root_planet="Moon")
    assert "Chandra Lagna" in svg_moon

    svg_sun = draw_chart.generate_circular_chart(items, mode="symbol", varga_name="D1", ayanamsha=ayanamsha, root_planet="Sun")
    assert "Surya Lagna" in svg_sun

def test_api_calculate_roots_and_modifiers():
    from app import app
    client = app.test_client()
    
    response = client.get("/api/chart/angelina-jolie")
    assert response.status_code == 200
    res = response.get_json()

    # Verify roots in svgs
    assert "svgs" in res
    assert "D1" in res["svgs"]
    assert "roots" in res["svgs"]["D1"]
    assert "Lagna" in res["svgs"]["D1"]["roots"]
    assert "Moon" in res["svgs"]["D1"]["roots"]
    assert "Sun" in res["svgs"]["D1"]["roots"]

    # Verify varga_lajjitadi_net_modifiers in data
    assert "data" in res
    assert "varga_lajjitadi_net_modifiers" in res["data"]
    mods = res["data"]["varga_lajjitadi_net_modifiers"]
    assert "D1" in mods
    assert "D3" in mods
    assert "D60" in mods
    assert "Mercury" in mods["D1"]
    assert "Mercury" in mods["D3"]

# ----------------- UI / Playwright Tests -----------------

def init_page(page: Page):
    page.goto(FLASK_URL)
    page.wait_for_timeout(800)
    page.evaluate(f"loadChart('{CHART_ID}')")
    page.wait_for_timeout(1200)

def test_tripod_of_life_workspace(page: Page):
    if not is_server_running():
        pytest.skip("Flask server is not running on port 5001")
    init_page(page)

    page.evaluate("changeWorkspace('tripod-of-life')")
    page.wait_for_timeout(800)

    # Verify 3 chart cells at the top exist
    cell_lagna = page.locator("#c1")
    cell_moon = page.locator("#c2")
    cell_sun = page.locator("#c3")

    expect(cell_lagna).to_be_visible()
    expect(cell_moon).to_be_visible()
    expect(cell_sun).to_be_visible()

    # Verify bottom cell has planetary info table
    expect(page.locator("#c4 .planetary-info-table")).to_be_visible()

    # Verify root pill buttons are active according to cell dataset
    assert page.locator("#c1 .btn-root-lagna").is_visible()
    assert page.locator("#c2 .btn-root-moon").is_visible()
    assert page.locator("#c3 .btn-root-sun").is_visible()

def test_varga_lajjitadi_modifiers_ui(page: Page):
    if not is_server_running():
        pytest.skip("Flask server is not running on port 5001")
    init_page(page)

    page.evaluate("assignWidget('varga-lajjitadi-modifiers', document.getElementById('cell2'))")
    page.wait_for_timeout(500)

    # Check 16 rows for the 16 vargas
    rows = page.locator("#cell2 .varga-lajjitadi-table tbody tr")
    assert rows.count() == 16, f"Expected 16 varga rows, got {rows.count()}"

    # Verify table headers
    headers = page.locator("#cell2 .varga-lajjitadi-table thead th")
    assert headers.count() == 8  # Varga + 7 planets
    
    table_text = page.locator("#cell2 .varga-lajjitadi-table").inner_text()
    assert "D1" in table_text
    assert "D3" in table_text
    assert "D60" in table_text

def test_rashi_drishti_ui(page: Page):
    if not is_server_running():
        pytest.skip("Flask server is not running on port 5001")
    init_page(page)

    page.evaluate("assignWidget('rashi-drishti', document.getElementById('cell2'))")
    page.wait_for_timeout(500)

    # Check 12 rows for 12 signs
    rows = page.locator("#cell2 .rashi-drishti-table tbody tr")
    assert rows.count() == 12, f"Expected 12 sign rows, got {rows.count()}"

    table_text = page.locator("#cell2 .rashi-drishti-table").inner_text()
    assert "Aries" in table_text
    assert "Movable" in table_text
    assert "Leo, Scorpio, Aquarius" in table_text

def test_bhava_inspector_ui(page: Page):
    if not is_server_running():
        pytest.skip("Flask server is not running on port 5001")
    init_page(page)

    # Evaluate the 5-Fold Bhava Inspector for House 10
    html = page.evaluate("renderBhavaInspectorHtml(10, 'D1')")
    assert "House 10 • Karma Bhāva" in html
    assert "1. The Field (Kṣetra)" in html
    assert "2. The Lord (Bhāveśa)" in html
    assert "3. Natural Karakas (Naisargika)" in html
    assert "4. Ārūḍha Pada (Manifestation)" in html
    assert "5. Divisional Varga Link" in html
    assert "Open D10" in html

    # Test openVargaFromInspector
    page.evaluate("openVargaFromInspector('D10')")
    page.wait_for_timeout(300)
    chart_cell = page.locator(".grid-cell[data-widget='chart']").first
    assert chart_cell.locator(".varga-select").input_value() == "D10"

def test_switch_root_perspectives(page: Page):
    if not is_server_running():
        pytest.skip("Flask server is not running on port 5001")
    init_page(page)

    cell = page.locator('.grid-cell[data-widget="chart"]').first

    # 1. Switch to Moon and back to Lagna via Toolbar button
    cell.locator('.btn-root-moon').click()
    page.wait_for_timeout(300)
    assert cell.get_attribute('data-root-planet') == 'Moon'
    assert 'Chandra Lagna' in cell.inner_text()

    cell.locator('.btn-root-lagna').click()
    page.wait_for_timeout(300)
    assert cell.get_attribute('data-root-planet') == 'Lagna'
    assert 'Chandra Lagna' not in cell.inner_text()

    # 2. Switch to Surya via Kala menu and back via D1 Rasi / Ascendant
    page.evaluate("currentActiveCell = document.querySelector('.grid-cell[data-widget=\"chart\"]')")
    page.evaluate("assignKalaPerspective('surya')")
    page.wait_for_timeout(300)
    assert cell.get_attribute('data-root-planet') == 'Sun'
    assert 'Surya Lagna' in cell.inner_text()

    page.evaluate("assignKalaChart('D1')")
    page.wait_for_timeout(300)
    assert cell.get_attribute('data-root-planet') == 'Lagna'
    assert 'Surya Lagna' not in cell.inner_text()

    # 3. Switch back via explicit Ascendant item in Kala menu
    page.evaluate("assignKalaPerspective('chandra')")
    page.wait_for_timeout(300)
    assert cell.get_attribute('data-root-planet') == 'Moon'

    page.evaluate("assignKalaPerspective('lagna')")
    page.wait_for_timeout(300)
    assert cell.get_attribute('data-root-planet') == 'Lagna'
    assert 'Chandra Lagna' not in cell.inner_text()

    # 4. Switch back via context menu option
    page.evaluate("assignWidget('chart', currentActiveCell, { root_planet: 'Moon' })")
    page.wait_for_timeout(300)
    assert cell.get_attribute('data-root-planet') == 'Moon'

    page.evaluate("assignWidget('chart', currentActiveCell, { root_planet: 'Lagna' })")
    page.wait_for_timeout(300)
    assert cell.get_attribute('data-root-planet') == 'Lagna'
    assert 'Chandra Lagna' not in cell.inner_text()
