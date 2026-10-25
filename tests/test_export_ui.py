"""
Playwright End-to-End Tests for Export Dropdown Menu and AI Text Exporter Modal.
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
    page.wait_for_function("typeof currentChartData !== 'undefined' && currentChartData !== null && currentChartData.planetary_evaluation")


def test_export_dropdown_and_modal(page: Page):
    init_page(page)

    # 1. Verify Export Dropdown exists in top toolbar
    export_btn = page.locator("#btnExportMenu")
    expect(export_btn).to_be_visible()
    assert "Export" in export_btn.text_content()

    # 2. Check dropdown items
    dropdown_menu = page.locator(".export-dropdown-menu")
    export_btn.hover()
    expect(dropdown_menu).to_be_visible()

    pdf_option = page.locator(".export-dropdown-menu #btnExportPdf")
    text_option = page.locator(".export-dropdown-menu #btnExportText")
    expect(pdf_option).to_be_visible()
    expect(text_option).to_be_visible()
    assert "PDF" in pdf_option.text_content()
    assert "Text" in text_option.text_content()

    # 3. Open Export Text Modal
    text_option.click()
    modal = page.locator("#exportTextModal")
    expect(modal).to_be_visible()

    # Wait for the text export preview to generate
    page.wait_for_function("document.getElementById('exportTextPreview') && document.getElementById('exportTextPreview').value.length > 100")
    preview = page.locator("#exportTextPreview")
    val = preview.input_value()

    # 4. Verify Content in Textarea
    assert "Astrological Master Dossier: Angelina Jolie" in val
    assert "Tropical Signs (Sāyana)" in val
    assert "Campanus 3D House System" in val
    assert "Master Graha Diagnostics (D1 Root Chart)" in val
    assert "Lagna (Ascendant)" in val
    assert "Sun" in val
    assert "Moon" in val
    assert "Campanus 3D Bhava Chalita Cusps" in val
    assert "Vimśottarī Daśā Timeline" in val

    # 5. Check Token Stats Readout
    stats = page.locator("#exportTextStats")
    expect(stats).to_be_visible()
    stats_text = stats.text_content()
    assert "words" in stats_text
    assert "tokens" in stats_text

    # 6. Test Preset Switch to Diagnostics Only
    radio_diag = page.locator("#radio-text-diag")
    radio_diag.click()
    page.wait_for_timeout(400)
    val_diag = preview.input_value()
    assert "Master Graha Diagnostics (D1 Root Chart)" in val_diag
    assert "AI Interpretation Directive" not in val_diag

    # 7. Close modal
    close_btn = page.locator("#exportTextModal .modal-close-btn")
    close_btn.click()
    expect(modal).not_to_be_visible()
