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
    page.goto(FLASK_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(800)
    page.evaluate(f"loadChart('{CHART_ID}')")
    page.wait_for_timeout(1200)

def test_houses_of_life_widget_renders(page: Page):
    init_page(page)
    page.evaluate("assignWidget('houses-of-life', document.querySelector('.grid-cell'))")
    page.wait_for_timeout(600)

    # Verify 12 rows rendered in matrix
    assert page.locator(".hol-house-row").count() == 12

    # Verify Horizon Ribbon elements
    assert page.locator(".hol-asc-anchor").inner_text() != "--"
    assert page.locator(".hol-top-flourishing").inner_text() != "--"
    assert page.locator(".hol-bars-grid > div").count() == 12

def test_houses_of_life_row_click_receipt(page: Page):
    init_page(page)
    page.evaluate("assignWidget('houses-of-life', document.querySelector('.grid-cell'))")
    page.wait_for_timeout(600)

    # Click House 8 row
    page.locator(".hol-house-row[data-house='8']").click()
    page.wait_for_timeout(400)

    # Verify receipt header card shows House 8
    badge = page.locator(".hol-selected-house-badge").first
    assert "H8" in badge.inner_text()
    title = page.locator(".hol-receipt-title").first
    assert "House 8" in title.inner_text()

    # Verify active tab in compact mode shifted to receipt
    tab_badge = page.locator(".hol-tab-house-badge").first
    assert "H8" in tab_badge.inner_text()

def test_houses_of_life_tab_switching(page: Page):
    init_page(page)
    page.evaluate("assignWidget('houses-of-life', document.querySelector('.grid-cell'))")
    page.wait_for_timeout(600)

    # Switch to 7-Graha Ledger
    page.locator(".hol-tab-btn[data-view='planets']").click()
    page.wait_for_timeout(400)
    assert page.locator(".hol-planets-table tbody tr").count() == 7

    # Switch to Concordance
    page.locator(".hol-tab-btn[data-view='concordance']").click()
    page.wait_for_timeout(400)
    assert page.locator(".hol-concordance-table tbody tr").count() == 12

    # Switch back to 12-House Matrix
    page.locator(".hol-tab-btn[data-view='matrix']").click()
    page.wait_for_timeout(400)
    assert page.locator(".hol-house-row").count() == 12

def test_houses_of_life_receipt_prev_next(page: Page):
    init_page(page)
    page.evaluate("assignWidget('houses-of-life', document.querySelector('.grid-cell'))")
    page.wait_for_timeout(600)

    # Select House 1
    page.locator(".hol-house-row[data-house='1']").click()
    page.wait_for_timeout(300)

    # Click Next button
    page.locator(".hol-receipt-next-btn").first.click()
    page.wait_for_timeout(300)
    assert "H2" in page.locator(".hol-selected-house-badge").first.inner_text()

    # Click Prev button
    page.locator(".hol-receipt-prev-btn").first.click()
    page.wait_for_timeout(300)
    assert "H1" in page.locator(".hol-selected-house-badge").first.inner_text()

def test_houses_of_life_right_click_menu_and_popup(page: Page):
    init_page(page)
    cell = page.locator(".grid-cell").first
    cell.click(button="right")
    page.wait_for_timeout(400)

    # Verify right-click Kala menu opens
    assert page.locator("#kalaMenuModal").is_visible()

    # Click Houses of Life in Column 3 (Tables)
    hol_item = page.locator(".kala-item:has-text('Houses of Life')")
    assert hol_item.count() > 0
    hol_item.click()
    page.wait_for_timeout(400)

    # Verify widget is rendered in cell
    assert page.locator(".widget-houses-of-life").count() > 0

    # Right click again and launch floating popup
    cell.click(button="right")
    page.wait_for_timeout(400)
    popup_btn = page.locator(".btn-kala-popup:has-text('Houses of Life Cockpit')")
    assert popup_btn.count() > 0
    popup_btn.click()
    page.wait_for_timeout(400)

    # Verify floating modal opened
    assert page.locator("#widgetMaximizeModal").is_visible()

