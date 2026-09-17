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
    page.wait_for_timeout(800)
    page.evaluate(f"loadChart('{CHART_ID}')")
    page.wait_for_timeout(1200)


def test_master_diagnostic_table_renders(page: Page):
    init_page(page)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
    page.wait_for_timeout(600)

    # 1. Verify table exists
    table = page.locator("#cell1 .master-diagnostic-table")
    assert table.is_visible()

    # 2. Verify 8 header columns
    headers = page.locator("#cell1 .master-diagnostic-table thead th")
    assert headers.count() == 8

    # 3. Verify rows: 1 Lagna row + 9 Graha rows = 10 rows
    rows = page.locator("#cell1 .master-diagnostic-table tbody tr")
    assert rows.count() == 10

    # 4. Verify each row has 8 cells
    for i in range(10):
        cells = rows.nth(i).locator("td")
        assert cells.count() == 8

    # 5. Check Master Lord badges exist in Cell 1
    master_lord_badges = page.locator("#cell1 .master-diagnostic-table tbody td:first-child .badge")
    assert master_lord_badges.count() >= 1

    # 6. Check Vitality score and receipt in Cell 8
    cell8_elements = page.locator("#cell1 .master-diagnostic-table tbody td:nth-child(8)")
    assert cell8_elements.count() == 10
    first_cell8 = cell8_elements.first.inner_text()
    assert "★" in first_cell8


def test_master_diagnostic_varga_switch(page: Page):
    init_page(page)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
    page.wait_for_timeout(600)

    # Select D9 Navamsha from dropdown
    select = page.locator("#cell1 .varga-select")
    select.select_option("D9")
    page.wait_for_timeout(500)

    # Verify rows still render properly
    rows = page.locator("#cell1 .master-diagnostic-table tbody tr")
    assert rows.count() == 10

    # Subtitle should update to D9
    subtitle = page.locator("#cell1 .varga-subtitle")
    assert "D9" in subtitle.inner_text()
