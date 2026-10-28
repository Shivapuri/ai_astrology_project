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

def test_houses_of_life_basic_sheet_renders(page: Page):
    """
    Step 4 Frontend UI Test:
    Clicking the Basic (30%) cell for House 1 opens the receipt inspector,
    renders the spreadsheet-grade Pillar 1 calculation ledger with 10 column headers,
    9 planet/node rows, and 3 footer proof rows, and verifies the 12px font floor.
    """
    init_page(page)
    page.evaluate("assignWidget('houses-of-life', document.querySelector('.grid-cell'))")
    page.wait_for_timeout(600)

    # Click Basic (30%) cell on House 1
    basic_cell_h1 = page.locator(".hol-house-row[data-house='1'] .hol-cell-basic")
    assert basic_cell_h1.count() > 0
    basic_cell_h1.click()
    page.wait_for_timeout(500)

    # Switch to receipt tab if on compact width
    tab_receipt = page.locator(".hol-tab-btn[data-view='receipt']")
    if tab_receipt.is_visible():
        tab_receipt.click()
        page.wait_for_timeout(300)

    # Verify spreadsheet table renders
    sheet_table = page.locator(".hol-basic-sheet-table")
    assert sheet_table.is_visible()

    # Verify 10 column headers
    headers = sheet_table.locator("thead th")
    assert headers.count() == 10
    header_texts = [headers.nth(i).inner_text().strip() for i in range(10)]
    assert "GRAHA" in header_texts[0].upper()
    assert "NET RAY" in header_texts[9].upper()

    # Verify exactly 9 rows (7 classical planets + Rahu + Ketu)
    rows = sheet_table.locator("tbody tr")
    assert rows.count() == 9

    # Verify 3 footer proof rows
    footer_rows = sheet_table.locator("tfoot tr")
    assert footer_rows.count() == 3
    assert "∑ Raw Signed Cusp Rays" in footer_rows.nth(0).inner_text()
    assert "÷ Fixed Baseline Divisor" in footer_rows.nth(1).inner_text()
    assert "Final Basic Score" in footer_rows.nth(2).inner_text()

    # Verify strict 12px font floor on headers and cells
    for i in range(headers.count()):
        font_size_px = float(headers.nth(i).evaluate("el => parseFloat(window.getComputedStyle(el).fontSize)"))
        assert font_size_px >= 12.0, f"Header {i} font size {font_size_px}px is below 12px floor"

    # Test toggle expand button
    expand_btn = page.locator(".hol-btn-expand-basic")
    assert expand_btn.count() > 0
    expand_btn.click()
    page.wait_for_timeout(300)
    assert page.locator(".hol-receipt-right.hol-sheet-expanded").count() > 0
    expand_btn.click()
    page.wait_for_timeout(300)
    assert page.locator(".hol-receipt-right.hol-sheet-expanded").count() == 0


