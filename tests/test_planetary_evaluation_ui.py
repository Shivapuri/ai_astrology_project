"""
Playwright End-to-End and Visual Verification Tests for
Vic DiCara's Planetary Evaluation & Positive-to-Negative Scale Widget & Floating Modal.
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

def test_planetary_evaluation_widget_renders(page: Page):
    init_page(page)
    # Assign widget to cell2
    page.evaluate("assignWidget('planetary-evaluation', document.getElementById('cell2'))")
    page.wait_for_timeout(600)
    
    # Verify Master Lords cards rendered
    master_cards = page.locator("#cell2 .eval-master-card")
    assert master_cards.count() >= 3
    
    # Verify table rows rendered
    rows = page.locator("#cell2 .planetary-eval-table tbody tr:not(.eval-calc-drawer-row)")
    assert rows.count() >= 7
    
    # Check scale badges exist
    badges = page.locator("#cell2 .eval-scale-badge")
    assert badges.count() >= 7

def test_planetary_evaluation_math_drawer_toggle(page: Page):
    init_page(page)
    page.evaluate("assignWidget('planetary-evaluation', document.getElementById('cell2'))")
    page.wait_for_timeout(500)
    
    # Click math button on first planet row
    math_btn = page.locator("#cell2 .btn-toggle-row-drawer").first
    math_btn.click()
    page.wait_for_timeout(300)
    
    # Verify drawer is now displayed
    drawer = page.locator("#cell2 .eval-calc-drawer-row").first
    assert drawer.is_visible()
    assert "📐" in drawer.inner_text()
    assert "Base" in drawer.inner_text()

def test_planetary_evaluation_floating_modal(page: Page):
    init_page(page)
    # Open floating modal
    page.evaluate("openFloatingPlanetaryEvaluation()")
    page.wait_for_timeout(600)
    
    modal = page.locator("#widgetMaximizeModal")
    assert modal.is_visible()
    
    title = page.locator("#widgetMaximizeModalTitle")
    assert "Planetary Evaluation" in title.inner_text()
    
    # Verify nav pill is active
    nav_btn = page.locator("#nav-btn-evaluation")
    assert "active" in nav_btn.get_attribute("class")
    
    # Close modal with Esc
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    assert not modal.is_visible()
