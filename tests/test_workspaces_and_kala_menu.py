import pytest
import urllib.request
from playwright.sync_api import Page, expect

FLASK_URL = "http://127.0.0.1:5001"
CHART_ID = "angelina-jolie"

def is_server_running(url=FLASK_URL):
    try:
        urllib.request.urlopen(url)
        return True
    except Exception:
        return False

@pytest.fixture(scope="module", autouse=True)
def check_server():
    if not is_server_running():
        pytest.skip("Flask server is not running on port 5001")

def init_page(page: Page):
    page.goto(FLASK_URL)
    page.wait_for_timeout(800)
    page.evaluate(f"loadChart('{CHART_ID}')")
    page.wait_for_timeout(1200)

def test_planetary_info_widget_renders(page: Page):
    init_page(page)
    page.evaluate("assignWidget('planetary-info', document.getElementById('cell2'))")
    page.wait_for_timeout(400)
    
    rows = page.locator(".planetary-info-table tbody tr")
    assert rows.count() == 10, f"Expected 10 rows (Lagna + 9 planets), found {rows.count()}"
    
    table_text = page.locator(".planetary-info-table").inner_text()
    assert "Lagna" in table_text
    assert "Sun" in table_text
    assert "Mercury" in table_text
    assert "Moolatrikona" in table_text or "Own House" in table_text
    assert "Jan" in table_text  # Tara abbreviation
    assert "Retro [R]" in table_text
    assert "Cb [C]" in table_text  # Mercury is combust for Angelina Jolie

def test_workspace_core_predictive(page: Page):
    init_page(page)
    page.evaluate("changeWorkspace('core-predictive')")
    page.wait_for_timeout(500)
    
    # Verify 3-pane layout elements exist
    expect(page.locator("#col1 #cell1")).to_be_visible()
    expect(page.locator("#col2 #cell2")).to_be_visible()
    expect(page.locator("#cell3")).to_be_visible()
    expect(page.locator("#cell4")).to_be_visible()
    
    # cell2 has planetary info
    expect(page.locator("#cell2 .planetary-info-table")).to_be_visible()
    # cell3 has D9 chart
    d9_select = page.locator("#cell3 .varga-select")
    assert d9_select.input_value() == "D9"
    # cell4 has dashas timeline
    expect(page.locator("#cell4 .dasa-timeline-table")).to_be_visible()

def test_workspace_big_four(page: Page):
    init_page(page)
    page.evaluate("changeWorkspace('big-four')")
    page.wait_for_timeout(500)
    
    # Verify 4-quadrant layout
    expect(page.locator("#c1")).to_be_visible()
    expect(page.locator("#c2")).to_be_visible()
    expect(page.locator("#c3")).to_be_visible()
    expect(page.locator("#c4")).to_be_visible()
    
    assert page.locator("#c1 .varga-select").input_value() == "D1"
    assert page.locator("#c2 .varga-select").input_value() == "D9"
    assert page.locator("#c3 .varga-select").input_value() == "D10"
    assert page.locator("#c4 .varga-select").input_value() == "D3"

def test_kala_menu_modal(page: Page):
    init_page(page)
    page.evaluate("openKalaMenu()")
    page.wait_for_timeout(300)
    
    modal = page.locator("#kalaMenuModal")
    expect(modal).to_be_visible()
    
    # Verify 4 columns exist
    cols = page.locator("#kalaMenuModal .kala-column")
    assert cols.count() == 4
    
    # Close modal
    page.evaluate("closeKalaMenu()")
    page.wait_for_timeout(200)
    expect(modal).not_to_be_visible()

def test_shodasa_vargas_16_in_1_modal(page: Page):
    init_page(page)
    page.evaluate("openShodasaVargasModal()")
    page.wait_for_timeout(400)
    
    modal = page.locator("#shodasaVargasModal")
    expect(modal).to_be_visible()
    
    # Verify 16 divisional chart cards
    cards = page.locator(".shodasa-varga-card")
    assert cards.count() == 16
    
    # Switch style to north
    page.locator(".shodasa-btn-north").click()
    page.wait_for_timeout(200)
    expect(cards.first.locator("svg")).to_be_visible()
    
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
    expect(modal).not_to_be_visible()
