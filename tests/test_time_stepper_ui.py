import pytest
from playwright.sync_api import Page, expect
import urllib.request

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

def test_stepper_present_and_responsive(page: Page):
    page.goto("http://127.0.0.1:5001/")
    page.wait_for_timeout(1000)
    
    # Load chart
    page.evaluate("loadChart('589fabff-bf49-405a-9372-6d9566bf6955')")
    page.wait_for_timeout(1200)

    cell1 = page.locator("#cell1")
    stepper = cell1.locator(".chart-time-stepper")
    expect(stepper).to_be_visible()

    # Verify initial clock display
    clock = stepper.locator(".stepper-clock")
    expect(clock).to_contain_text("22:20:00")
    
    # Verify badge says Original
    badge = stepper.locator(".stepper-offset-badge")
    expect(badge).to_have_text("Original")
    
    # Reset and Save buttons should be hidden initially
    reset_btn = stepper.locator(".stepper-btn-reset")
    expect(reset_btn).to_be_hidden()
    
    save_btn = stepper.locator(".stepper-btn-save")
    expect(save_btn).to_be_hidden()

    # Click +1m
    btn_plus_1m = stepper.locator("button:has-text('+1m')")
    btn_plus_1m.click()
    page.wait_for_timeout(800)

    # Clock should advance to 22:21:00
    expect(clock).to_contain_text("22:21:00")
    expect(badge).to_have_text("+1m")
    expect(reset_btn).to_be_visible()
    expect(save_btn).to_be_visible()

    # Check top subtitle contains PREVIEW tag
    subtitle = page.locator("#chartSubtitle")
    expect(subtitle).to_contain_text("PREVIEW: +1m")

    # Click reset button
    reset_btn.click()
    page.wait_for_timeout(800)

    # Reverts to original
    expect(clock).to_contain_text("22:20:00")
    expect(badge).to_have_text("Original")
    expect(reset_btn).to_be_hidden()
    expect(save_btn).to_be_hidden()
    expect(subtitle).not_to_contain_text("PREVIEW")
