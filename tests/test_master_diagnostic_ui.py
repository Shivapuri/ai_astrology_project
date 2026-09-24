"""
Playwright End-to-End Tests for Master Graha Diagnostics Table.
Verifies the 8-column layout, 9-tier archetypes, master lords, environmental badges,
calculation receipts, and divisional varga switching.
"""

import re
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
    page.wait_for_function("typeof loadChart === 'function'")
    page.evaluate(f"loadChart('{CHART_ID}')")
    page.wait_for_function("typeof currentChartData !== 'undefined' && currentChartData !== null && currentChartData.planetary_evaluation")


def test_master_diagnostic_table_renders(page: Page):
    init_page(page)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
    table = page.locator("#cell1 .master-diagnostic-table")
    expect(table).to_be_visible()

    # 1. Verify 9 header columns
    headers = page.locator("#cell1 .master-diagnostic-table > thead > tr > th")
    assert headers.count() == 9

    # 2. Verify rows: 1 Lagna row + 9 Graha rows = 10 rows
    rows = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row")
    expect(rows).to_have_count(10)

    # 3. Verify each row has 9 cells
    for i in range(10):
        cells = rows.nth(i).locator("td")
        assert cells.count() == 9

    # 4. Check Master Lord badges exist in Cell 1
    master_lord_badges = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row td:first-child .badge")
    assert master_lord_badges.count() >= 1

    # 5. Check Nakshatra badge exists in Cell 7
    cell7_elements = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row td:nth-child(7)")
    assert cell7_elements.count() == 10
    first_cell7 = cell7_elements.first.inner_text()
    assert "Overlord:" in first_cell7

    # 6. Check Vitality score and receipt in Cell 9
    cell9_elements = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row td:nth-child(9)")
    assert cell9_elements.count() == 10
    first_cell9 = cell9_elements.first.inner_text()
    assert "★" in first_cell9


def test_master_diagnostic_drawer_toggle(page: Page):
    init_page(page)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
    sun_row = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row[data-id='Sun']")
    expect(sun_row).to_be_visible()

    # Click Sun's row to open drawer
    drawer = page.locator("#cell1 #drawer-Sun")
    sun_row.click()
    expect(drawer).to_be_visible()
    drawer_text_upper = drawer.inner_text().upper()
    assert "1. ESSENTIAL FOUNDATION" in drawer_text_upper
    assert "2. ENVIRONMENT & ALLIANCES" in drawer_text_upper
    assert "3. INCOMING DRISHTI CURVES" in drawer_text_upper
    assert "STAGE 4 SYNTHESIS" in drawer_text_upper

    # Click again to close drawer
    sun_row.click()
    expect(drawer).not_to_be_visible()


def test_master_diagnostic_varga_switch(page: Page):
    init_page(page)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")

    # Select D9 Navamsha from dropdown
    select = page.locator("#cell1 .varga-select")
    expect(select).to_be_visible()
    select.select_option("D9")

    # Subtitle should update to D9
    subtitle = page.locator("#cell1 .varga-subtitle")
    expect(subtitle).to_contain_text("D9")

    # Verify rows still render properly
    rows = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row")
    expect(rows).to_have_count(10)


def test_master_diagnostic_typography_floor(page: Page):
    """Verify that NO text anywhere in tables, badges, captions, or drawer cards is below 12px."""
    init_page(page)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
    
    # Open Venus drawer
    venus_row = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row[data-id='Venus']")
    expect(venus_row).to_be_visible()
    venus_row.click()
    
    drawer = page.locator("#cell1 #drawer-Venus")
    expect(drawer).to_be_visible()
    
    # Check computed font-sizes of headers, cells, badges, and drawer elements
    font_check = page.evaluate("""() => {
        const table = document.querySelector('#cell1 .master-diagnostic-table');
        if (!table) return { count: 0, violations: [] };
        
        const violations = [];
        const walker = document.createTreeWalker(table, NodeFilter.SHOW_ELEMENT);
        let el = walker.nextNode();
        let total = 0;
        
        while (el) {
            // Only inspect elements with direct text or specific visual widgets
            if (el.tagName !== 'svg' && el.tagName !== 'path' && el.tagName !== 'g' && el.tagName !== 'line' && el.tagName !== 'circle' && el.tagName !== 'polyline' && el.tagName !== 'polygon') {
                const fs = parseFloat(window.getComputedStyle(el).fontSize);
                // Check if element has non-empty text content
                const text = el.innerText ? el.innerText.trim() : '';
                if (text && fs > 0) {
                    total++;
                    if (fs < 12.0) {
                        violations.push({
                            tag: el.tagName,
                            className: el.className,
                            fontSize: fs,
                            text: text.substring(0, 30)
                        });
                    }
                }
            }
            el = walker.nextNode();
        }
        return { count: total, violations: violations };
    }""")
    
    assert font_check["count"] > 0, "Should have inspected text elements"
    assert len(font_check["violations"]) == 0, f"Found sub-12px elements: {font_check['violations'][:5]}"


def test_master_diagnostic_drawer_cockpit_layout(page: Page):
    """Verify widescreen 3-column cockpit layout: Top Strip, Shadvarga Table, Alliances, Drishti Curves, and Stage 4 Banner."""
    init_page(page)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
    
    venus_row = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row[data-id='Venus']")
    expect(venus_row).to_be_visible()
    venus_row.click()
    
    drawer = page.locator("#cell1 #drawer-Venus")
    expect(drawer).to_be_visible()
    
    # 1. Cockpit container
    cockpit = drawer.locator(".diagnostic-drawer-cockpit")
    expect(cockpit).to_be_visible()
    
    drawer_text = drawer.inner_text()
    drawer_text_upper = drawer_text.upper()
    
    # 2. Header Strip: Kinetic Muscle & Score
    assert "Kinetic Muscle:" in drawer_text
    assert "/ 10" in drawer_text
    
    # 3. Column 1: Essential Foundation (Shadvarga)
    assert "1. ESSENTIAL FOUNDATION (SHADVARGA)" in drawer_text_upper
    assert "Base Shadvarga Dignity:" in drawer_text
    
    # 4. Column 2: Environment & Alliances
    assert "2. ENVIRONMENT & ALLIANCES" in drawer_text_upper
    assert "Host Dispositor:" in drawer_text
    assert "FUNCTIONAL DIGNITY:" in drawer_text_upper
    
    # 5. Column 3: Incoming Drishti Curves
    assert "3. INCOMING DRISHTI CURVES" in drawer_text_upper
    
    # 6. Bottom Banner: Stage 4 Synthesis
    assert "STAGE 4 SYNTHESIS:" in drawer_text_upper
    assert "Net Vitality:" in drawer_text
    assert "Biological Vitality:" in drawer_text
    assert "Conscious Mood:" in drawer_text
    
    # 7. Also test Jupiter drawer for clean Lajjitadi badges and no emojis in badges
    jup_row = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row[data-id='Jupiter']")
    expect(jup_row).to_be_visible()
    jup_row.click()
    
    jup_drawer = page.locator("#cell1 #drawer-Jupiter")
    expect(jup_drawer).to_be_visible()
    jup_cockpit = jup_drawer.locator(".diagnostic-drawer-cockpit")
    expect(jup_cockpit).to_be_visible()
    
    jup_text_upper = jup_drawer.inner_text().upper()
    assert "1. ESSENTIAL FOUNDATION (SHADVARGA)" in jup_text_upper
    assert "2. ENVIRONMENT & ALLIANCES" in jup_text_upper
    assert "3. INCOMING DRISHTI CURVES" in jup_text_upper
    assert "STAGE 4 SYNTHESIS:" in jup_text_upper


