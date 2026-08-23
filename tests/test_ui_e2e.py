import pytest
import urllib.request
from playwright.sync_api import Page, expect

def is_server_running(url="http://127.0.0.1:5001"):
    try:
        urllib.request.urlopen(url)
        return True
    except:
        return False

@pytest.fixture(scope="module", autouse=True)
def check_server():
    if not is_server_running():
        pytest.skip("Flask server is not running on port 5001")

def test_homepage_loads(page: Page):
    page.goto("http://127.0.0.1:5001/")
    expect(page).to_have_title("Ernst Wilhelm Kala Chart Software")
    
def test_dashboard_split_layout(page: Page):
    page.goto("http://127.0.0.1:5001/")
    
    # Check if split containers exist
    expect(page.locator("#chart-pane")).to_be_visible()
    expect(page.locator("#info-pane")).to_be_visible()

def test_hotkey_chart_switching(page: Page):
    page.goto("http://127.0.0.1:5001/")
    
    # Initially South is active
    expect(page.locator("#view-south")).to_have_class("chart-view active")
    expect(page.locator("#btn-south")).to_have_class("hotkey-btn active")
    
    # Click North hotkey pill
    page.locator("#btn-north").click()
    expect(page.locator("#view-north")).to_have_class("chart-view active")
    expect(page.locator("#btn-north")).to_have_class("hotkey-btn active")
    expect(page.locator("#view-south")).not_to_have_class("chart-view active")

def test_varga_dropdown(page: Page):
    page.goto("http://127.0.0.1:5001/")
    # Select D9
    page.locator("#vargaSelect1").select_option("D9")
    # Title in toolbar should update
    expect(page.locator("#toolbar-chart-title")).to_have_text("D9 - Navamsa")
