"""
Playwright End-to-End Regression Tests for Table Maximization (Full Screen).
Verifies that maximizing any table widget mounts the complete view with all data rows,
active controls, and no empty header-only tables.
"""

import urllib.request
import pytest
from playwright.sync_api import sync_playwright

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


@pytest.fixture(scope="module")
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(FLASK_URL)
        page.wait_for_timeout(1000)
        page.evaluate(f"loadChart('{CHART_ID}')")
        page.wait_for_timeout(1500)
        yield page
        browser.close()


def test_maximize_master_diagnostic(browser_page):
    page = browser_page
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
    page.wait_for_timeout(300)

    btn = page.locator("#cell1 .btn-widget-maximize")
    btn.click(force=True)
    page.wait_for_timeout(400)

    container = page.locator("#widgetMaximizeContainer")
    rows = container.locator("tbody tr.diagnostic-row")
    assert rows.count() == 10, f"Expected 10 diagnostic rows, got {rows.count()}"

    # Verify drawer opens on row click
    sun_row = container.locator("tr.diagnostic-row[data-id='Sun']")
    sun_row.click()
    page.wait_for_timeout(200)
    drawer = container.locator("#drawer-Sun")
    assert drawer.is_visible()

    # Close modal
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)


def test_maximize_planetary_info(browser_page):
    page = browser_page
    page.evaluate("assignWidget('planetary-info', document.getElementById('cell1'))")
    page.wait_for_timeout(300)

    btn = page.locator("#cell1 .btn-widget-maximize")
    btn.click(force=True)
    page.wait_for_timeout(400)

    container = page.locator("#widgetMaximizeContainer")
    rows = container.locator("tbody tr")
    assert rows.count() == 10, f"Expected 10 planetary info rows, got {rows.count()}"

    page.keyboard.press("Escape")
    page.wait_for_timeout(200)


def test_maximize_ashtakavarga(browser_page):
    page = browser_page
    page.evaluate("assignWidget('ashtakavarga', document.getElementById('cell1'))")
    page.wait_for_timeout(300)

    btn = page.locator("#cell1 .btn-widget-maximize")
    btn.click(force=True)
    page.wait_for_timeout(400)

    container = page.locator("#widgetMaximizeContainer")
    rows = container.locator("tbody tr")
    assert rows.count() == 8, f"Expected 8 ashtakavarga rows, got {rows.count()}"

    # Test view switch inside maximized window
    v_select = container.locator(".av-view-select")
    v_select.select_option("trikona")
    page.wait_for_timeout(200)
    assert container.locator("tbody tr").count() == 8

    page.keyboard.press("Escape")
    page.wait_for_timeout(200)


def test_maximize_aspects(browser_page):
    page = browser_page
    page.evaluate("assignWidget('aspects-planets', document.getElementById('cell1'))")
    page.wait_for_timeout(300)

    btn = page.locator("#cell1 .btn-widget-maximize")
    btn.click(force=True)
    page.wait_for_timeout(400)

    container = page.locator("#widgetMaximizeContainer")
    rows = container.locator("tbody tr")
    assert rows.count() >= 9, f"Expected at least 9 aspect rows, got {rows.count()}"

    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
