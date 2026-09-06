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

def test_vimshottari_widget_renders(page: Page):
    init_page(page)
    page.evaluate("assignWidget('dashas-timeline', document.getElementById('cell2'))")
    page.wait_for_timeout(500)
    assert page.locator(".dasa-timeline-table tbody tr").count() >= 9
    assert page.locator(".dasa-timeline-table tbody tr.md-row").count() == 9

def test_ashtakavarga_widget_renders(page: Page):
    init_page(page)
    page.evaluate("assignWidget('ashtakavarga', document.getElementById('cell3'))")
    page.wait_for_timeout(500)
    assert page.locator(".ashtakavarga-table tbody tr").count() >= 7
    assert "337" in page.locator(".sav-tot").inner_text()

def test_vimshopaka_widget_renders(page: Page):
    init_page(page)
    page.evaluate("assignWidget('vimshopaka', document.getElementById('cell4'))")
    page.wait_for_timeout(500)
    assert page.locator(".vimshopaka-table tbody tr").count() >= 4
    text = page.locator(".vimshopaka-table").inner_text()
    assert "Shadvarga" in text
    assert "Shodashavarga" in text

def test_ashtakavarga_view_mode_switching(page: Page):
    init_page(page)
    page.evaluate("assignWidget('ashtakavarga', document.getElementById('cell3'))")
    page.wait_for_timeout(300)
    select = page.locator("#cell3 .av-view-select")
    select.select_option("trikona")
    page.wait_for_timeout(300)
    assert page.locator("#cell3 .ashtakavarga-table tbody tr").count() >= 7

    select.select_option("ekadhipatya")
    page.wait_for_timeout(300)
    assert page.locator("#cell3 .ashtakavarga-table tbody tr").count() >= 7

def test_nakshatras_widget_phase3_fields(page: Page):
    init_page(page)
    page.evaluate("assignWidget('nakshatras', document.getElementById('cell2'))")
    page.wait_for_timeout(500)
    assert page.locator(".nakshatras-table tbody tr").count() >= 7
    text = page.locator(".nakshatras-table").inner_text()
    assert "%" in text  # relative speed percentage pill

def test_yoga_judgment_widget_renders(page: Page):
    init_page(page)
    page.evaluate("assignWidget('yoga-judgment', document.getElementById('cell2'))")
    page.wait_for_timeout(500)
    assert page.locator(".yoga-judgment-table tbody tr").count() >= 12
    text = page.locator(".yoga-judgment-table").inner_text()
    assert "Ishta and Kashta" in text
    assert "Subha and Asubha" in text
    assert "Subha and Asubha Dig Bala" in text
    assert "IxSxSD" in text
    assert "KxAxAD" in text

def test_floating_yoga_judgment_modal(page: Page):
    init_page(page)
    page.evaluate("openFloatingYogaJudgment()")
    page.wait_for_timeout(500)
    modal = page.locator("#widgetMaximizeModal")
    assert modal.is_visible()
    title = page.locator("#widgetMaximizeModalTitle").inner_text()
    assert "Yoga Judgment" in title
    assert page.locator("#widgetMaximizeContainer .yoga-judgment-table tbody tr").count() >= 12
    # Close modal
    page.evaluate("document.getElementById('widgetMaximizeModal').style.display = 'none'")

def test_hover_tooltips_on_tables(page: Page):
    init_page(page)
    page.evaluate("assignWidget('yoga-judgment', document.getElementById('cell2'))")
    page.wait_for_timeout(500)
    # Hover over the first numeric cell in Yoga Judgment
    first_cell = page.locator(".yoga-judgment-table tbody tr td.tooltip-target").first
    first_cell.hover()
    page.wait_for_timeout(300)
    tooltip = page.locator("#global-tooltip")
    assert tooltip.is_visible()
    tip_text = tooltip.inner_text()
    assert len(tip_text) > 10

def test_click_house_empty_field_in_charts(page: Page):
    init_page(page)
    # Assign Context & Technical Info widget to cell2
    page.evaluate("assignWidget('info', document.getElementById('cell2'))")
    page.wait_for_timeout(500)
    
    # 1. Click empty field (polygon) of House 4 in North Indian chart
    page.evaluate("setGlobalChartStyle('north')")
    page.evaluate("assignWidget('chart', document.getElementById('cell1'))")
    page.wait_for_timeout(500)
    h4_poly = page.locator("#cell1 polygon.house-cell[data-id='4']").first
    assert h4_poly.count() > 0
    h4_poly.dispatch_event("click")
    page.wait_for_timeout(400)
    info_text = page.locator("#cell2 #context-info-content").inner_text()
    assert "House 4" in info_text
    assert "Sukha Bhāva" in info_text or "Kṣetra" in info_text
        
    # 2. Click empty field (rect) of House in South Indian chart
    page.evaluate("setGlobalChartStyle('south')")
    page.evaluate("assignWidget('chart', document.getElementById('cell1'))")
    page.wait_for_timeout(500)
    south_house_cell = page.locator("#cell1 rect.house-cell").first
    assert south_house_cell.count() > 0
    h_id = south_house_cell.get_attribute("data-id")
    south_house_cell.dispatch_event("click")
    page.wait_for_timeout(400)
    info_text = page.locator("#cell2 #context-info-content").inner_text()
    assert f"House {h_id}" in info_text
        
    # 3. Click an independent house cusp number
    cusp_el = page.locator("#cell1 g.interactive[data-type='house']").first
    assert cusp_el.count() > 0
    cusp_id = cusp_el.get_attribute("data-id")
    cusp_el.dispatch_event("click")
    page.wait_for_timeout(400)
    info_text = page.locator("#cell2 #context-info-content").inner_text()
    assert f"House {cusp_id}" in info_text

