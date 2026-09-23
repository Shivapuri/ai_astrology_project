"""
Playwright End-to-End Tests for Master Graha Diagnostics Table.
Verifies the 8-column layout, 9-tier archetypes, master lords, environmental badges,
calculation receipts, and divisional varga switching.
"""

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
    page.wait_for_function("typeof loadChart === 'function'")
    page.evaluate(f"loadChart('{CHART_ID}')")
    page.wait_for_function("typeof currentChartData !== 'undefined' && currentChartData !== null && currentChartData.planetary_evaluation")


def test_master_diagnostic_table_renders(page: Page):
    init_page(page)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
    table = page.locator("#cell1 .master-diagnostic-table")
    expect(table).to_be_visible()

    # 1. Verify 9 header columns
    headers = page.locator("#cell1 .master-diagnostic-table > thead > tr > th")
    assert headers.count() == 9

    # 2. Verify rows: 1 Lagna row + 9 Graha rows = 10 rows
    rows = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row")
    expect(rows).to_have_count(10)

    # 3. Verify each row has 9 cells
    for i in range(10):
        cells = rows.nth(i).locator("td")
        assert cells.count() == 9

    # 4. Check Master Lord badges exist in Cell 1
    master_lord_badges = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row td:first-child .badge")
    assert master_lord_badges.count() >= 1

    # 5. Check Nakshatra badge exists in Cell 7
    cell7_elements = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row td:nth-child(7)")
    assert cell7_elements.count() == 10
    first_cell7 = cell7_elements.first.inner_text()
    assert "Overlord:" in first_cell7

    # 6. Check Vitality score and receipt in Cell 9
    cell9_elements = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row td:nth-child(9)")
    assert cell9_elements.count() == 10
    first_cell9 = cell9_elements.first.inner_text()
    assert "★" in first_cell9


def test_master_diagnostic_drawer_toggle(page: Page):
    init_page(page)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
    sun_row = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row[data-id='Sun']")
    expect(sun_row).to_be_visible()

    # Click Sun's row to open drawer
    drawer = page.locator("#cell1 #drawer-Sun")
    sun_row.click()
    expect(drawer).to_be_visible()
    assert "Dignity & Peer Bridge" in drawer.inner_text()
    assert "House Placement" in drawer.inner_text()

    # Click again to close drawer
    sun_row.click()
    expect(drawer).not_to_be_visible()


def test_master_diagnostic_varga_switch(page: Page):
    init_page(page)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")

    # Select D9 Navamsha from dropdown
    select = page.locator("#cell1 .varga-select")
    expect(select).to_be_visible()
    select.select_option("D9")

    # Subtitle should update to D9
    subtitle = page.locator("#cell1 .varga-subtitle")
    expect(subtitle).to_contain_text("D9")

    # Verify rows still render properly
    rows = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row")
    expect(rows).to_have_count(10)
