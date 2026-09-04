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

def test_client_change_updates_chart(page: Page):
    page.goto("http://127.0.0.1:5001/")
    page.wait_for_timeout(1000)
    
    # Ensure the first client is loaded and SVG is visible
    page.locator("svg").first.wait_for(state="visible")
    
    # Grab the HTML content of the first chart widget's South SVG
    chart_widget = page.locator('.grid-cell[data-widget="chart"]').first
    initial_svg_html = chart_widget.locator('.svg-south').inner_html()
    
    # Check options in select
    select_locator = page.locator("#nativeSelect")
    options_count = select_locator.locator("option").count()
    
    if options_count >= 3:
        # Select the next client (index 2)
        second_option_value = select_locator.locator("option").nth(2).get_attribute("value")
        select_locator.select_option(second_option_value)
        
        # Click Load
        page.locator("button", has_text="Load").click()
        
        # Wait for loading indicator to show then hide (or just wait a bit)
        page.wait_for_timeout(1500)
        
        # Grab the HTML content again
        new_svg_html = chart_widget.locator('.svg-south').inner_html()
        
        # The chart should have updated, so the SVGs should be different
        assert initial_svg_html != new_svg_html, "Chart SVG did not update after loading a new client!"

def test_16_shodashavargas_options(page: Page):
    page.goto("http://127.0.0.1:5001/")
    page.wait_for_timeout(1000)
    
    expected_vargas = [
        "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
        "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"
    ]
    
    # Check chart dropdown
    chart_select = page.locator(".widget-chart .varga-select").first
    chart_options = [opt.get_attribute("value") for opt in chart_select.locator("option").all()]
    assert chart_options == expected_vargas, f"Chart varga options mismatch: {chart_options}"
    
    # Check qualitative avasthas dropdown
    avastha_select = page.locator('.grid-cell[data-widget="avasthas-calc"] .varga-select').first
    avastha_options = [opt.get_attribute("value") for opt in avastha_select.locator("option").all()]
    assert avastha_options == expected_vargas, f"Avastha varga options mismatch: {avastha_options}"

def test_dignities_table_click_switches_chart(page: Page):
    page.goto("http://127.0.0.1:5001/")
    page.wait_for_timeout(1000)
    page.locator("svg").first.wait_for(state="visible")
    
    # Find row 9 in Dignities table and click it
    rows = page.locator("#vargaDignitiesTable tbody tr").all()
    clicked = False
    for r in rows:
        val = r.locator("td").first.inner_text().strip()
        if val == "9":
            r.click()
            clicked = True
            break
    assert clicked, "Row 9 not found in Dignities table"
    page.wait_for_timeout(500)
    
    # Check chart select value is D9
    expect(page.locator(".widget-chart .varga-select").first).to_have_value("D9")

def test_avasthas_calc_independent_varga_switch(page: Page):
    page.goto("http://127.0.0.1:5001/")
    page.wait_for_timeout(1000)
    page.locator("svg").first.wait_for(state="visible")
    
    chart_select = page.locator(".widget-chart .varga-select").first
    chart_select.select_option("D1")
    expect(chart_select).to_have_value("D1")
    
    # Switch avastha select to D10
    avastha_cell = page.locator('.grid-cell[data-widget="avasthas-calc"]').first
    avastha_select = avastha_cell.locator(".varga-select")
    avastha_select.select_option("D10")
    page.wait_for_timeout(500)
    
    # Verify title updated to D10
    expect(avastha_cell.locator(".avastha-calc-title")).to_have_text("D10 - Qualitative Avasthas")
    
    # Verify chart select remained D1 (independent multi-varga grid)
    expect(chart_select).to_have_value("D1")


def test_table_widget_maximize_modal(page: Page):
    page.goto("http://127.0.0.1:5001/")
    page.wait_for_timeout(1000)
    page.locator("svg").first.wait_for(state="visible")

    # Find Dignities widget and click maximize button
    dignities_cell = page.locator('.grid-cell[data-widget="dignities"]').first
    max_btn = dignities_cell.locator(".btn-widget-maximize")
    expect(max_btn).to_be_visible()
    max_btn.click()

    modal = page.locator("#widgetMaximizeModal")
    expect(modal).to_be_visible()
    expect(page.locator("#widgetMaximizeModalTitle")).to_contain_text("Dignities in Vargas")
    expect(page.locator("#widgetMaximizeContainer table")).to_be_visible()

    # Close with Escape key
    page.keyboard.press("Escape")
    expect(modal).not_to_be_visible()

