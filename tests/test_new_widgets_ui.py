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
