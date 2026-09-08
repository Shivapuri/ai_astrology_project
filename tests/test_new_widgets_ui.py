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

def test_click_house_cusp_numbers_in_charts(page: Page):
    init_page(page)
    # Assign Context & Technical Info widget to cell2
    page.evaluate("assignWidget('info', document.getElementById('cell2'))")
    page.wait_for_timeout(500)
    
    # 1. Click house cusp in North Indian chart
    page.evaluate("setGlobalChartStyle('north')")
    page.evaluate("assignWidget('chart', document.getElementById('cell1'))")
    page.wait_for_timeout(500)
    cusp_north = page.locator("#cell1 g.interactive[data-type='house']").first
    assert cusp_north.count() > 0
    c_id = cusp_north.get_attribute("data-id")
    cusp_north.click()
    page.wait_for_timeout(400)
    info_text = page.locator("#cell2 #context-info-content").inner_text()
    assert f"House {c_id}" in info_text
        
    # 2. Click house cusp in South Indian chart
    page.evaluate("setGlobalChartStyle('south')")
    page.evaluate("assignWidget('chart', document.getElementById('cell1'))")
    page.wait_for_timeout(500)
    cusp_south = page.locator("#cell1 g.interactive[data-type='house']").first
    assert cusp_south.count() > 0
    s_id = cusp_south.get_attribute("data-id")
    cusp_south.click()
    page.wait_for_timeout(400)
    info_text = page.locator("#cell2 #context-info-content").inner_text()
    assert f"House {s_id}" in info_text

def test_sign_attributes_widget_renders(page: Page):
    init_page(page)
    page.evaluate("assignWidget('sign-attributes', document.getElementById('cell2'))")
    page.wait_for_timeout(500)
    assert page.locator("#cell2 .sign-attr-matrix-table").count() == 1
    assert page.locator("#cell2 .sign-attr-matrix-table tbody tr").count() == 4
    # Check that Fire, Earth, Air, Water are present
    text = page.locator("#cell2 .sign-attr-matrix-table").inner_text()
    assert "Fire" in text
    assert "Earth" in text
    assert "Air" in text
    assert "Water" in text

def test_sign_attributes_tabs_switching(page: Page):
    init_page(page)
    page.evaluate("assignWidget('sign-attributes', document.getElementById('cell2'))")
    page.wait_for_timeout(500)

    # 1. Switch to Kalapurusha Anatomy tab
    anatomy_btn = page.locator("#cell2 .sign-attr-pill-btn", has_text="Kalapurusha Anatomy")
    anatomy_btn.click()
    page.wait_for_timeout(400)
    assert page.locator("#cell2 .sign-attr-anatomy-table tbody tr").count() == 12
    anat_text = page.locator("#cell2 .sign-attr-anatomy-table").inner_text()
    assert "Head, Brain" in anat_text
    assert "Feet, Toes" in anat_text

    # 2. Switch to Polarity & Rising tab
    polarity_btn = page.locator("#cell2 .sign-attr-pill-btn", has_text="Polarity & Rising")
    polarity_btn.click()
    page.wait_for_timeout(400)
    pol_text = page.locator("#cell2 .sign-attr-content").inner_text()
    assert "Active / Masculine / Day Signs" in pol_text
    assert "Passive / Feminine / Night Signs" in pol_text
    assert "Head-rising (Shirshodaya)" in pol_text

def test_south_indian_center_cycling(page: Page):
    init_page(page)
    page.evaluate("setGlobalChartStyle('south')")
    page.evaluate("assignWidget('chart', document.getElementById('cell1'))")
    page.wait_for_timeout(500)

    center = page.locator("#cell1 .svg-south .si-center-container")
    assert center.count() == 1
    assert center.get_attribute("data-view") == "title"

    # Click to cycle to matrix view
    center.click()
    page.wait_for_timeout(300)
    assert center.get_attribute("data-view") == "matrix"
    matrix_view = page.locator("#cell1 .svg-south .si-view-matrix")
    assert matrix_view.is_visible()

    # Click to cycle to anatomy view
    center.click()
    page.wait_for_timeout(300)
    assert center.get_attribute("data-view") == "anatomy"
    anatomy_view = page.locator("#cell1 .svg-south .si-view-anatomy")
    assert anatomy_view.is_visible()

    # Click to cycle back to title view
    center.click()
    page.wait_for_timeout(300)
    assert center.get_attribute("data-view") == "title"
    title_view = page.locator("#cell1 .svg-south .si-view-title")
    assert title_view.is_visible()

def test_floating_sign_attributes(page: Page):
    init_page(page)
    page.evaluate("openFloatingSignAttributes('D1')")
    page.wait_for_timeout(500)
    modal = page.locator("#widgetMaximizeModal")
    assert modal.is_visible()
    assert "Sign Attributes & Anatomy" in page.locator("#widgetMaximizeModalTitle").inner_text()
    assert page.locator("#floatingSignAttrContent .sign-attr-matrix-table").count() == 1
    # Close modal
    page.evaluate("document.getElementById('widgetMaximizeModal').style.display = 'none'")


