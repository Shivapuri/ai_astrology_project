"""
Edge-Case Tests for Master Graha Diagnostics (Backend Math & Frontend UI)
Run via: pytest tests/test_diagnostics_edge_cases.py -v
"""

import pytest
import json
import urllib.request
from playwright.sync_api import Page, expect
from jyotish.generate_jyotish import generate_kala_chart

FLASK_URL = "http://127.0.0.1:5001"

# ==========================================
# 1. BACKEND TESTS (Math & Nakshatra Data)
# ==========================================

@pytest.fixture(scope='module')
def test_chart():
    # Generate a standard baseline chart
    return generate_kala_chart(
        name='Test Edge Case Chart',
        year=1975, month=6, day=4,
        hour=9, minute=9,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )

def test_equation_parts_no_double_counting(test_chart):
    """
    Asserts that the Vitality Score perfectly matches the sum of equation_parts.
    Ensures old flat additives (+0.3 for retrograde, etc) have been fully removed.
    """
    planets_eval = test_chart["planetary_evaluation"]["planets"]

    for planet_name, eval_data in planets_eval.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue

        vitality_score = eval_data.get("vitality_score", 0.0)
        equation_parts = eval_data.get("equation_parts", {})

        # Verify the receipt exists
        assert equation_parts, f"equation_parts missing for {planet_name}"

        # Calculate the mathematical sum of the receipt
        calculated_sum = sum(equation_parts.values())

        # Assert the final score matches the explicitly declared math breakdown
        # (Using a small tolerance for floating-point rounding)
        assert abs(vitality_score - calculated_sum) < 0.01, \
            f"Double counting detected for {planet_name}! Final Score: {vitality_score}, Sum of Parts: {calculated_sum}"

def test_nakshatra_payload_presence_and_structure(test_chart):
    """
    Asserts the Nakshatra payload is correctly attached to the planetary evaluation
    and contains all the necessary analytical metadata.
    """
    planets_eval = test_chart["planetary_evaluation"]["planets"]

    # Check Moon as a baseline
    moon_eval = planets_eval["Moon"]
    assert "nakshatra" in moon_eval, "Nakshatra data completely missing from Moon evaluation."

    nak_data = moon_eval["nakshatra"]
    assert "name" in nak_data, "Nakshatra missing 'name'"
    assert "ruler" in nak_data, "Nakshatra missing 'ruler' (Overlord)"
    assert "deity" in nak_data, "Nakshatra missing 'deity'"
    assert "nature" in nak_data, "Nakshatra missing 'nature' (Mridu/Ugra/etc)"
    assert "core_drive" in nak_data, "Nakshatra missing 'core_drive'"


# ==========================================
# 2. FRONTEND UI TESTS (Playwright)
# ==========================================

def is_server_running(url=FLASK_URL):
    try:
        urllib.request.urlopen(url, timeout=1.0)
        return True
    except Exception:
        return False

@pytest.fixture(scope="module", autouse=True)
def check_server():
    if not is_server_running():
        pytest.skip(f"Flask server is not running on {FLASK_URL}")

def test_aspect_virupa_ui_filtering(page: Page):
    """
    Tests the 3-tier visual filter for Aspects (Drishti) by intercepting
    the backend JSON payload and injecting mock aspects.
    """
    # 1. Define the mock aspect data representing our 3 edge cases
    mock_aspects = [
        {"from_planet": "Jupiter", "virupas": 15, "raw_virupas": 15, "from_dignity_name": "Own Sign", "from_dignity_pct": 75},   # Tier 1: < 20v (Should be invisible)
        {"from_planet": "Venus", "virupas": 30, "raw_virupas": 30, "from_dignity_name": "Neutral", "from_dignity_pct": 50},       # Tier 2: 20-44v (Should be tooltip only)
        {"from_planet": "Saturn", "virupas": 55, "raw_virupas": 55, "from_dignity_name": "Enemy's Sign", "from_dignity_pct": 25} # Tier 3: >= 45v (Should be visible badge)
    ]

    # 2. Intercept the network request and inject the mock aspects into the Sun's data
    def handle_route(route):
        url = route.request.url
        if "/biwheel" in url:
            route.continue_()
            return
        if "angelina-jolie" in url:
            response = route.fetch()
            json_data = response.json()
            # Strip bulky SVG bundle to prevent CDP buffer overflow over WebSocket
            if "svgs" in json_data:
                json_data["svgs"] = {}
            if "data" in json_data and "planetary_evaluation" in json_data["data"]:
                p_eval = json_data["data"]["planetary_evaluation"]["planets"]
                if "Sun" in p_eval:
                    p_eval["Sun"]["aspect_details"] = mock_aspects
                    if "vitality" in p_eval["Sun"]:
                        p_eval["Sun"]["vitality"]["aspect_details"] = mock_aspects
            route.fulfill(json=json_data)
        else:
            route.continue_()

    # Apply the interception specifically to the chart API endpoint
    page.route("**/api/chart/**", handle_route)
    page.route("**/api/generate_chart**", handle_route)
    page.route("**/api/get_chart**", handle_route)

    # 3. Load the page and wait for the Master Diagnostics Table
    page.goto(FLASK_URL)
    page.wait_for_timeout(800)
    page.evaluate("loadChart('angelina-jolie')")
    page.wait_for_timeout(1000)
    page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
    page.wait_for_selector("#master-diagnostic-tbody tr")

    # 4. Target the Sun's row and its "Environmental Vision" (Aspects) cell
    sun_row = page.locator("#master-diagnostic-tbody tr.diagnostic-row:has-text('Sun')")
    aspects_cell = sun_row.locator("td").nth(5) # Environmental Vision (Aspects/Yuti) is Column 6 (index 5)

    # Assert 1: The < 20v aspect (Jupiter) is completely invisible in the main cell text
    expect(aspects_cell).not_to_contain_text("Jupiter")

    # Assert 2: The 20-44v aspect (Venus) is NOT in the main text badge...
    main_badges = aspects_cell.locator(".aspect-badge-main")
    expect(main_badges).not_to_contain_text("Venus")

    # ...but Venus DOES exist inside the hover tooltip (data-tooltip attribute)
    tooltip_content = aspects_cell.get_attribute("data-tooltip") or aspects_cell.inner_html()
    assert "Venus" in tooltip_content, "The 30v Venus aspect is missing from the tooltip!"

    # Assert 3: The >= 45v aspect (Saturn) IS visible directly as a main badge in the cell
    expect(aspects_cell).to_contain_text("Saturn (55v)")
    # Assert the qualitative text for a Malefic was correctly generated
    expect(aspects_cell).to_contain_text("Pressure") # Checking for "Constructive Pressure" or "Destructive Pressure"
