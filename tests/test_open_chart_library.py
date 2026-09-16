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

def test_open_chart_modal_toggle_and_search(page: Page):
    page.goto("http://127.0.0.1:5001/")
    page.wait_for_timeout(1000)

    # 1. Click Open button in toolbar
    btn_open = page.locator("#btnOpenChartModal")
    expect(btn_open).to_be_visible()
    btn_open.click()

    # 2. Check modal is displayed
    modal = page.locator("#openChartModal")
    expect(modal).to_be_visible()

    # 3. Filter by 'Criminals'
    pill_crim = page.locator(".open-chart-pill[data-cat='Criminals']")
    expect(pill_crim).to_be_visible()
    pill_crim.click()

    # Expect Adolf Hitler, Heinrich Himmler, Jeffrey Dahmer, Joseph Goebbels to be visible
    expect(page.locator("#openChartListContainer").get_by_text("Adolf Hitler")).to_be_visible()
    expect(page.locator("#openChartListContainer").get_by_text("Heinrich Himmler")).to_be_visible()
    expect(page.locator("#openChartListContainer").get_by_text("Jeffrey Dahmer")).to_be_visible()
    expect(page.locator("#openChartListContainer").get_by_text("Joseph Goebbels")).to_be_visible()

    # Non-criminals like Shivapuri should NOT be in the filtered list
    expect(page.locator("#openChartListContainer").get_by_text("Shivapuri")).not_to_be_visible()

    # 4. Search input live filtering
    search_input = page.locator("#openChartSearchInput")
    search_input.fill("dahmer")
    page.wait_for_timeout(300)

    expect(page.locator("#openChartListContainer").get_by_text("Jeffrey Dahmer")).to_be_visible()
    expect(page.locator("#openChartListContainer").get_by_text("Adolf Hitler")).not_to_be_visible()

    # 5. Open Jeffrey Dahmer chart
    page.locator("#openChartListContainer .btn-primary").click()
    page.wait_for_timeout(1000)

    # Modal should close and Jeffrey Dahmer chart should be loaded
    expect(modal).not_to_be_visible()
    expect(page.locator("#chartTitle")).to_contain_text("Jeffrey Dahmer")
    expect(page.locator("#chartSubtitle")).to_contain_text("Milwaukee, WI")

    # Dropdown should show Jeffrey Dahmer selected without cluttering permanent list
    native_select = page.locator("#nativeSelect")
    expect(native_select).to_have_value("jeffrey-dahmer")

def test_hotkey_ctrl_o_opens_modal(page: Page):
    page.goto("http://127.0.0.1:5001/")
    page.wait_for_timeout(1000)

    modal = page.locator("#openChartModal")
    expect(modal).not_to_be_visible()

    # Press Ctrl+O / Meta+O
    page.keyboard.press("Control+o")
    page.wait_for_timeout(400)
    expect(modal).to_be_visible()

    # Press Escape to close
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    expect(modal).not_to_be_visible()
