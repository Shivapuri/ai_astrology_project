"""
Playwright End-to-End Tests for Animated Transit Bi-Wheel & Chart Switching.
Verifies bidirectional chart switching (S, N, C, B, T), hotkey transitions,
aspect orb selection, trigger drawer interactivity, and circular chart aspect toggles.
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
    page.goto(FLASK_URL, wait_until="domcontentloaded")
    page.wait_for_function("typeof loadChart === 'function'")
    page.evaluate(f"loadChart('{CHART_ID}')")
    page.wait_for_function("typeof currentChartData !== 'undefined' && currentChartData !== null")


def test_transit_switching_bidirectional(page: Page):
    init_page(page)

    # 1. Switch cell1 to Transit via T button
    btn_t = page.locator("#cell1 .btn-transit")
    expect(btn_t).to_be_visible()
    btn_t.click()
    page.wait_for_timeout(800)

    cell1 = page.locator("#cell1")
    expect(cell1).to_have_attribute("data-widget", "transit-chart")

    # Verify buttons N, S, C, B, T exist inside transit toolbar
    expect(page.locator("#cell1 .btn-north")).to_be_visible()
    expect(page.locator("#cell1 .btn-south")).to_be_visible()
    expect(page.locator("#cell1 .btn-circular")).to_be_visible()
    expect(page.locator("#cell1 .btn-biwheel")).to_be_visible()

    # 2. Switch back to North Indian chart via N button
    page.locator("#cell1 .btn-north").click()
    page.wait_for_timeout(800)
    expect(cell1).to_have_attribute("data-widget", "chart")
    expect(page.locator("#cell1 .view-north")).to_have_class("view-north chart-view active")

    # 3. Switch to South Indian chart via S button
    page.locator("#cell1 .btn-south").click()
    page.wait_for_timeout(800)
    expect(page.locator("#cell1 .view-south")).to_have_class("view-south chart-view active")


def test_transit_hotkeys(page: Page):
    init_page(page)

    # Click cell1 to ensure it is the active cell
    page.locator("#cell1").click()

    # Press 't' to switch to Transit Bi-Wheel
    page.keyboard.press("t")
    page.wait_for_timeout(800)
    expect(page.locator("#cell1")).to_have_attribute("data-widget", "transit-chart")

    # Press 'c' to switch back to Circular Chart
    page.keyboard.press("c")
    page.wait_for_timeout(800)
    expect(page.locator("#cell1")).to_have_attribute("data-widget", "chart")
    expect(page.locator("#cell1 .view-circular")).to_have_class("view-circular chart-view active")

    # Press 't' again to toggle back to Transit Bi-Wheel
    page.keyboard.press("t")
    page.wait_for_timeout(800)
    expect(page.locator("#cell1")).to_have_attribute("data-widget", "transit-chart")

    # Press 'n' to switch back to North Indian chart
    page.keyboard.press("n")
    page.wait_for_timeout(800)
    expect(page.locator("#cell1")).to_have_attribute("data-widget", "chart")
    expect(page.locator("#cell1 .view-north")).to_have_class("view-north chart-view active")


def test_circular_chart_aspects_toggle(page: Page):
    init_page(page)

    page.locator("#cell1 .btn-circular").click()
    page.wait_for_timeout(800)

    aspect_btn = page.locator("#cell1 .btn-toggle-aspects")
    expect(aspect_btn).to_be_visible()

    # Toggle aspects ON
    aspect_btn.click()
    page.wait_for_timeout(300)
    expect(aspect_btn).to_contain_text("Aspects: ON")


def test_transit_orb_and_triggers_drawer(page: Page):
    init_page(page)

    page.locator("#cell1 .btn-transit").click()
    page.wait_for_timeout(800)

    # Change orb to 10.0°
    orb_sel = page.locator("#cell1 .transit-orb-select")
    orb_sel.select_option("10.0")
    page.wait_for_timeout(1000)

    count_badge = page.locator("#cell1 .transit-aspect-count")
    count_val = int(count_badge.inner_text())
    assert count_val > 1

    # Open drawer
    page.locator("#cell1 .btn-transit-toggle-table").click()
    page.wait_for_timeout(400)
    drawer = page.locator("#cell1 .transit-aspects-drawer")
    expect(drawer).to_be_visible()

    # Verify rows rendered
    rows = page.locator("#cell1 .transit-aspect-row")
    expect(rows).to_have_count(count_val)


def test_floating_window_chart_nav(page: Page):
    init_page(page)

    page.evaluate("openFloatingTransit()")
    page.wait_for_timeout(800)

    # Click Natal Chart in floating nav
    page.locator("#nav-btn-chart").click()
    page.wait_for_timeout(800)

    title = page.locator("#widgetMaximizeModalTitle")
    expect(title).to_contain_text("Natal Chart")
    expect(page.locator("#widgetMaximizeContainer .widget-chart")).to_be_visible()


def test_transit_stepper_and_date_adaptation(page: Page):
    init_page(page)

    # 1. Switch cell1 to Transit
    page.locator("#cell1 .btn-transit").click()
    page.wait_for_timeout(800)

    # Get initial date
    date_input = page.locator("#cell1 .transit-date-input")
    init_date_str = date_input.input_value()
    assert len(init_date_str) == 10

    # 2. Step forward 1 day
    page.locator("#cell1 .btn-transit-step-fwd").click()
    page.wait_for_timeout(800)

    stepped_date_str = date_input.input_value()
    assert stepped_date_str != init_date_str

    # Verify live badge updated
    badge_text = page.locator("#cell1 .transit-date-display-text").inner_text()
    assert len(badge_text) > 10

    # Verify SVG center hub contains the new stepped date
    hub_text = page.locator("#cell1 .transit-svg-container svg").text_content()
    assert "GOCHARA" in hub_text

    # 3. Fast Forward (5 days)
    page.locator("#cell1 .btn-transit-step-fast-fwd").click()
    page.wait_for_timeout(800)
    ff_date_str = date_input.input_value()
    assert ff_date_str != stepped_date_str

    # 4. Change interval to 30d and step forward
    page.select_option("#cell1 .transit-interval-select", "30d")
    page.locator("#cell1 .btn-transit-step-fwd").click()
    page.wait_for_timeout(800)
    month_date_str = date_input.input_value()
    assert month_date_str != ff_date_str

    # 5. Direct date input change to 2020-01-01
    date_input.fill("2020-01-01")
    date_input.dispatch_event("change")
    page.wait_for_timeout(800)

    current_date = date_input.input_value()
    assert current_date == "2020-01-01"
    hub_text_2020 = page.locator("#cell1 .transit-svg-container svg").text_content()
    assert "01/01/2020" in hub_text_2020

    # 6. Play / Pause animation test
    play_btn = page.locator("#cell1 .btn-transit-play-pause")
    play_btn.click()
    page.wait_for_timeout(1200)

    # Date should have advanced during playback
    played_date = date_input.input_value()
    assert played_date != "2020-01-01"

    # Pause
    play_btn.click()
    page.wait_for_timeout(400)
    paused_date = date_input.input_value()
    page.wait_for_timeout(600)
    still_paused_date = date_input.input_value()
    assert paused_date == still_paused_date
