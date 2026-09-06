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

def test_floating_bhava_chalita_window(page: Page):
    init_page(page)
    # Open Bhava Chalita Cusps floating table
    page.evaluate("openBhavaCuspsModal()")
    page.wait_for_timeout(300)
    
    modal = page.locator("#widgetMaximizeModal")
    card = page.locator("#widgetMaximizeCard")
    expect(modal).to_be_visible()
    expect(card).to_be_visible()
    
    # 1. Verify No Blur on the background overlay
    computed_blur = modal.evaluate("el => window.getComputedStyle(el).backdropFilter || window.getComputedStyle(el).webkitBackdropFilter")
    assert computed_blur == "none" or computed_blur == "" or "blur" not in computed_blur, f"Overlay should not blur background, found: {computed_blur}"
    
    # 2. Verify Table content (12 Campanus cusps)
    expect(page.locator("#widgetMaximizeModalTitle")).to_contain_text("Bhava Chalita")
    rows = page.locator("#widgetMaximizeContainer table tbody tr")
    assert rows.count() == 12, f"Expected 12 house rows, found {rows.count()}"
    
    # Verify columns: Bhava, Sign, Lord, Cusp, Longitude, Occupants
    header_text = page.locator("#widgetMaximizeContainer table thead").inner_text()
    assert "Bhava" in header_text
    assert "Sign" in header_text
    assert "Lord" in header_text
    assert "Cusp" in header_text
    assert "Occupants" in header_text
    
    # 3. Test Dragging: Drag header by 60px down and 80px right
    header = page.locator("#widgetMaximizeHeader")
    initial_pos = card.bounding_box()
    assert initial_pos is not None
    
    header_box = header.bounding_box()
    assert header_box is not None
    start_x = header_box["x"] + header_box["width"] / 2
    start_y = header_box["y"] + header_box["height"] / 2
    
    page.mouse.move(start_x, start_y)
    page.mouse.down()
    page.mouse.move(start_x + 80, start_y + 60, steps=5)
    page.mouse.up()
    page.wait_for_timeout(200)
    
    new_pos = card.bounding_box()
    assert new_pos is not None
    assert new_pos["x"] > initial_pos["x"], "Card should have moved to the right"
    assert new_pos["y"] > initial_pos["y"], "Card should have moved downwards"
    
    # 4. Test Quick Tab Navigation: Switch to Planetary Info and back
    page.locator("#nav-btn-planet").click()
    page.wait_for_timeout(200)
    expect(page.locator("#widgetMaximizeModalTitle")).to_contain_text("Planetary Information")
    expect(page.locator("#widgetMaximizeContainer .planetary-info-table")).to_be_visible()
    
    # Switch back to Bhava Chalita
    page.locator("#nav-btn-bhava").click()
    page.wait_for_timeout(200)
    expect(page.locator("#widgetMaximizeModalTitle")).to_contain_text("Bhava Chalita")
    
    # 5. Test Minimize / Collapse toggle
    collapse_btn = page.locator("#widgetMaximizeCollapseBtn")
    collapse_btn.click()
    page.wait_for_timeout(150)
    assert "collapsed" in (card.get_attribute("class") or "")
    
    # Expand again
    collapse_btn.click()
    page.wait_for_timeout(150)
    assert "collapsed" not in (card.get_attribute("class") or "")
    
    # 6. Test Close with Escape key
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
    expect(modal).not_to_be_visible()

