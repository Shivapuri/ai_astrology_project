import re
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
    
    # Check if split containers exist in the new grid layout
    expect(page.locator("#grid-container")).to_be_visible()
    expect(page.locator(".grid-cell").first).to_be_visible()

def test_hotkey_chart_switching(page: Page):
    page.goto("http://127.0.0.1:5001/")
    
    # Let layout load
    page.wait_for_timeout(1000)
    
    # Initially South is active in the first chart widget
    expect(page.locator(".widget-chart .view-south").first).to_have_class("view-south chart-view active")
    expect(page.locator(".widget-chart .btn-south").first).to_have_class("hotkey-btn active btn-south")
    
    # Click North hotkey pill
    page.locator(".widget-chart .btn-north").first.click()
    expect(page.locator(".widget-chart .view-north").first).to_have_class("view-north chart-view active")
    expect(page.locator(".widget-chart .btn-north").first).to_have_class("hotkey-btn btn-north active")

def test_varga_dropdown(page: Page):
    page.goto("http://127.0.0.1:5001/")
    page.wait_for_timeout(1000)
    
    # Select D9
    page.locator(".widget-chart .varga-select").first.select_option("D9")
    
    # Verify the select value is D9
    expect(page.locator(".widget-chart .varga-select").first).to_have_value("D9")

def test_planet_selection_clear(page: Page):
    page.goto("http://127.0.0.1:5001/")
    page.wait_for_timeout(1000)
    
    # Wait for the SVG to load
    page.locator("svg").first.wait_for(state="visible")
    
    # Click Sun interactive element (we'll just evaluate a click on the first two planets)
    # Since they are generated dynamically, we can query selector for '.interactive'
    interactive_elements = page.locator('.interactive[data-type="graha"]').all()
    if len(interactive_elements) >= 2:
        interactive_elements[0].click()
        page.wait_for_timeout(200)
        
        # Verify first is highlighted
        expect(interactive_elements[0]).to_have_class(re.compile(r"highlight-source"))
        
        interactive_elements[1].click()
        page.wait_for_timeout(200)
        
        # Verify first is NO LONGER highlighted
        expect(interactive_elements[0]).not_to_have_class(re.compile(r"highlight-source"))
        # Verify second IS highlighted
        expect(interactive_elements[1]).to_have_class(re.compile(r"highlight-source"))
