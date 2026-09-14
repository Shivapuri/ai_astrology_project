import os
import time
from playwright.sync_api import sync_playwright

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1440, "height": 900})
        
        # Navigate to local astra instance
        page.goto('http://127.0.0.1:5001', wait_until='networkidle')
        time.sleep(2)

        # Select first native
        native_select = page.locator('#nativeSelect')
        if native_select.count() > 0:
            options = native_select.locator('option').all()
            if len(options) > 1:
                native_select.select_option(index=1)
                time.sleep(1)

        # Setup test container if not present
        page.evaluate("""() => {
            let el = document.getElementById('context-info-content');
            if (!el) {
                el = document.createElement('div');
                el.id = 'context-info-content';
                el.style.cssText = 'position:fixed;top:40px;right:20px;width:550px;height:820px;background:#fffdfa;z-index:99999;overflow-y:auto;box-shadow:0 10px 30px rgba(0,0,0,0.3);border-radius:10px;padding:15px;';
                document.body.appendChild(el);
            }
        }""")

        # Test House 1 Click
        print("Testing House 1 Context Info...")
        page.evaluate("() => { const el = document.getElementById('context-info-content'); el.innerHTML = renderBhavaInspectorHtml(1, 'D1', window.knowledgeBase.house['1']); }")
        time.sleep(1)

        props_card = page.locator('#context-info-content .astra-props-card')
        assert props_card.count() > 0, "Props card not found for House 1"
        print("✓ House 1 Properties Card rendered")

        # Verify badges
        badges = props_card.locator('.prop-badge').all()
        print(f"✓ Found {len(badges)} property badges (Purushartha, Kendra, Trikona)")
        assert len(badges) >= 2, "Expected at least 2 property badges for House 1"

        tab_bar = page.locator('#context-info-content .astra-tab-bar')
        assert tab_bar.count() > 0, "Tab bar not found for House 1"
        
        tab_btns = tab_bar.locator('.astra-tab-btn').all()
        print(f"✓ Found {len(tab_btns)} tab buttons for House 1")
        assert len(tab_btns) == 6, f"Expected 6 tabs for House 1, got {len(tab_btns)}"

        # Click each tab and verify active pane
        for btn in tab_btns:
            tab_name = btn.inner_text()
            btn.click()
            time.sleep(0.2)
            active_pane = page.locator('#context-info-content .astra-tab-pane.active')
            assert active_pane.count() > 0, f"Active pane missing after clicking {tab_name}"
            print(f"  ✓ Tab '{tab_name}' switched cleanly")

        # Test Raw YAML Toggle
        yaml_btn = page.locator('#context-info-content .raw-yaml-toggle-btn')
        yaml_btn.click()
        time.sleep(0.2)
        raw_block = page.locator('#context-info-content .raw-yaml-block')
        assert raw_block.is_visible(), "Raw YAML block should be visible after toggle"
        print("✓ Raw YAML block toggle verified")

        os.makedirs('/tmp/astra_screenshots', exist_ok=True)
        page.screenshot(path='/tmp/astra_screenshots/house_1_context.png')
        print("✓ House 1 screenshot saved to /tmp/astra_screenshots/house_1_context.png")

        # Test Planet Click (Mars)
        print("\nTesting Mars Context Info...")
        page.evaluate("() => { const el = document.getElementById('context-info-content'); el.innerHTML = renderContextInfoHtml('planet', 'Mars', 'D1'); }")
        time.sleep(1)

        p_props_card = page.locator('#context-info-content .astra-props-card')
        assert p_props_card.count() > 0, "Props card not found for Mars"
        print("✓ Mars Properties Card rendered")

        p_badges = p_props_card.locator('.prop-badge').all()
        print(f"✓ Found {len(p_badges)} property badges for Mars (Guna, Element, Exalted, Debilitated)")
        assert len(p_badges) >= 3, "Expected at least 3 property badges for Mars"

        p_tab_bar = page.locator('#context-info-content .astra-tab-bar')
        p_tab_btns = p_tab_bar.locator('.astra-tab-btn').all()
        print(f"✓ Found {len(p_tab_btns)} tab buttons for Mars")
        assert len(p_tab_btns) == 7, f"Expected 7 tabs for Mars, got {len(p_tab_btns)}"

        for btn in p_tab_btns:
            tab_name = btn.inner_text()
            btn.click()
            time.sleep(0.2)
            active_pane = page.locator('#context-info-content .astra-tab-pane.active')
            assert active_pane.count() > 0, f"Active pane missing after clicking {tab_name}"
            print(f"  ✓ Planet tab '{tab_name}' switched cleanly")

        # Check Native Lagna Banner in 12 Lagnas tab
        lagnas_tab_btn = page.locator('#context-info-content .astra-tab-btn:has-text("12 Lagnas")')
        lagnas_tab_btn.click()
        time.sleep(0.2)
        lagna_box = page.locator('#context-info-content .lagna-highlight-box')
        assert lagna_box.count() > 0, "Lagna highlight box missing in 12 Lagnas tab"
        print("✓ Native Lagna highlight banner verified in 12 Lagnas tab")

        page.screenshot(path='/tmp/astra_screenshots/mars_context.png')
        print("✓ Mars screenshot saved to /tmp/astra_screenshots/mars_context.png")

        browser.close()
        print("\n🎉 ALL CONTEXT INFO TESTS PASSED 100%!")

if __name__ == '__main__':
    run_test()
