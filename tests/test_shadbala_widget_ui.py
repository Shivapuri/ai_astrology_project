import pytest
import urllib.request
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
def page():
    """Launch headless browser, load chart, and assign the shadbala-table widget."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page()
        pg.goto(FLASK_URL)
        pg.wait_for_timeout(1500)

        # Load Angelina Jolie chart
        pg.evaluate(f"loadChart('{CHART_ID}')")
        pg.wait_for_timeout(2000)

        # Assign 'shadbala-table' widget to cell1
        pg.evaluate("assignWidget('shadbala-table', document.getElementById('cell1'))")
        pg.wait_for_timeout(500)

        yield pg
        browser.close()

def test_shadbala_widget_rendered(page):
    table = page.locator(".shadbala-breakdown-grid")
    assert table.count() >= 1, "Shad Bala Breakdown table should be rendered"

def test_shadbala_widget_headers(page):
    headers = page.locator(".shadbala-breakdown-grid th").all_text_contents()
    expected = ["Strength Component", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    assert headers[:8] == expected, f"Unexpected header columns: {headers}"

def test_shadbala_widget_row_count(page):
    rows = page.locator(".shadbala-breakdown-grid tbody tr")
    assert rows.count() >= 25, f"Expected at least 25 breakdown rows, found {rows.count()}"

def test_shadbala_widget_has_totals_and_ranks(page):
    text = page.locator(".shadbala-breakdown-grid").inner_text()
    assert "Shad Bala Total" in text
    assert "Shad Bala in Rupas" in text
    assert "Relative Rank" in text
    assert "Sthana Bala" in text
    assert "Kaala Bala" in text
    assert "Dig Bala" in text
    assert "Ayana Bala" in text
    assert "Cheshta Bala" in text
