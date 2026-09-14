import os
import time
from playwright.sync_api import sync_playwright

FLASK_URL = "http://127.0.0.1:5001"
CHART_ID = "angelina-jolie"
OUTPUT_DIR = "/tmp/astra_screenshots"

def run_all_verifications():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1440, "height": 900})
        
        print(f"Loading {FLASK_URL}...")
        page.goto(FLASK_URL, wait_until='networkidle')
        page.wait_for_timeout(1000)
        
        # Load chart
        print(f"Loading chart: {CHART_ID}")
        page.evaluate(f"loadChart('{CHART_ID}')")
        page.wait_for_timeout(1500)
        
        # Set cell1 = chart, cell2 = info
        print("Setting up layout: cell1 = chart, cell2 = info")
        page.evaluate("""() => {
            const c1 = document.getElementById('cell1');
            const c2 = document.getElementById('cell2');
            if (c1) assignWidget('chart', c1);
            if (c2) assignWidget('info', c2);
        }""")
        page.wait_for_timeout(1000)

        # ==========================================
        # 1. SOUTH INDIAN CHART TESTS
        # ==========================================
        print("\n--- 1. Testing South Indian Chart ---")
        page.evaluate("setGlobalChartStyle('south')")
        page.wait_for_timeout(800)
        
        # Click Planet in South Indian
        p_mars = page.locator("#cell1 .chart-view.active .interactive[data-type='planet'][data-id='Mars']").first
        assert p_mars.count() > 0, "Mars not found in South Indian chart"
        p_mars.click()
        page.wait_for_timeout(500)
        
        info_header = page.locator("#cell2 .astra-props-title").inner_text()
        print(f"  ✓ Clicked Mars in South Indian -> Info header: {info_header}")
        assert "Mars" in info_header
        assert page.locator("#cell2 .astra-tab-btn").count() == 7
        
        page.screenshot(path=f"{OUTPUT_DIR}/1_south_indian_planet_mars.png")
        print(f"  📸 Saved {OUTPUT_DIR}/1_south_indian_planet_mars.png")
        
        # Click House 1 in South Indian
        h1_south = page.locator("#cell1 .chart-view.active .interactive[data-type='house'][data-id='1']").first
        assert h1_south.count() > 0, "House 1 not found in South Indian chart"
        h1_south.click()
        page.wait_for_timeout(500)
        
        h_header = page.locator("#cell2 .astra-props-title").inner_text()
        print(f"  ✓ Clicked House 1 in South Indian -> Info header: {h_header}")
        assert "House 1" in h_header
        assert page.locator("#cell2 .astra-tab-btn").count() == 6
        
        page.screenshot(path=f"{OUTPUT_DIR}/2_south_indian_house_1.png")
        print(f"  📸 Saved {OUTPUT_DIR}/2_south_indian_house_1.png")

        # ==========================================
        # 2. NORTH INDIAN CHART TESTS
        # ==========================================
        print("\n--- 2. Testing North Indian Chart ---")
        page.evaluate("setGlobalChartStyle('north')")
        page.wait_for_timeout(800)
        
        # Click Planet in North Indian
        p_north = page.locator("#cell1 .chart-view.active .interactive[data-type='planet'][data-id='Mars']").first
        if p_north.count() == 0 or not p_north.is_visible():
            p_north = page.locator("#cell1 .chart-view.active .interactive[data-type='planet']:not([data-id='Lagna'])").first
        
        p_id = p_north.get_attribute("data-id")
        p_north.click()
        page.wait_for_timeout(500)
        
        info_header = page.locator("#cell2 .astra-props-title").inner_text()
        print(f"  ✓ Clicked {p_id} in North Indian -> Info header: {info_header}")
        assert p_id in info_header
        assert page.locator("#cell2 .astra-tab-btn").count() == 7
        
        page.screenshot(path=f"{OUTPUT_DIR}/3_north_indian_planet_{p_id.lower()}.png")
        print(f"  📸 Saved {OUTPUT_DIR}/3_north_indian_planet_{p_id.lower()}.png")
        
        # Click House in North Indian
        h1_north = page.locator("#cell1 .chart-view.active .interactive[data-type='house'][data-id='1']").first
        assert h1_north.count() > 0, "House 1 not found in North Indian chart"
        h1_north.click()
        page.wait_for_timeout(500)
        
        h_header = page.locator("#cell2 .astra-props-title").inner_text()
        print(f"  ✓ Clicked House 1 in North Indian -> Info header: {h_header}")
        assert "House 1" in h_header
        assert page.locator("#cell2 .astra-tab-btn").count() == 6
        
        page.screenshot(path=f"{OUTPUT_DIR}/4_north_indian_house_1.png")
        print(f"  📸 Saved {OUTPUT_DIR}/4_north_indian_house_1.png")

        # ==========================================
        # 3. CIRCULAR CHART TESTS
        # ==========================================
        print("\n--- 3. Testing Western Circular Chart ---")
        page.evaluate("setGlobalChartStyle('circular')")
        page.wait_for_timeout(800)
        
        # Click Planet Glyph in Circular
        p_glyph = page.locator("#cell1 .chart-view.active .interactive.planet-glyph").first
        assert p_glyph.count() > 0, "Planet glyph not found in Circular chart"
        circ_p_id = p_glyph.get_attribute("data-id")
        p_glyph.click()
        page.wait_for_timeout(500)
        
        info_header = page.locator("#cell2 .astra-props-title").inner_text()
        print(f"  ✓ Clicked {circ_p_id} in Circular -> Info header: {info_header}")
        assert circ_p_id in info_header
        assert page.locator("#cell2 .astra-tab-btn").count() == 7
        
        page.screenshot(path=f"{OUTPUT_DIR}/5_circular_planet_{circ_p_id.lower()}.png")
        print(f"  📸 Saved {OUTPUT_DIR}/5_circular_planet_{circ_p_id.lower()}.png")
        
        # Click House Number in Circular
        h_circ = page.locator("#cell1 .chart-view.active text.interactive[data-type='house'][data-id='1']").first
        if h_circ.count() == 0:
            h_circ = page.locator("#cell1 .chart-view.active text.interactive[data-type='house']").first
        
        circ_h_id = h_circ.get_attribute("data-id")
        h_circ.click()
        page.wait_for_timeout(500)
        
        h_header = page.locator("#cell2 .astra-props-title").inner_text()
        print(f"  ✓ Clicked House {circ_h_id} in Circular -> Info header: {h_header}")
        assert f"House {circ_h_id}" in h_header
        assert page.locator("#cell2 .astra-tab-btn").count() == 6
        
        page.screenshot(path=f"{OUTPUT_DIR}/6_circular_house_{circ_h_id}.png")
        print(f"  📸 Saved {OUTPUT_DIR}/6_circular_house_{circ_h_id}.png")

        browser.close()
        print("\n🎉 ALL 3 CHART TYPES (NORTH, SOUTH, CIRCULAR) VERIFIED WITH PLANETS & HOUSES 100%!")

if __name__ == '__main__':
    run_all_verifications()
