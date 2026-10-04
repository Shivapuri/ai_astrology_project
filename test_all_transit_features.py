import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print("Navigating to http://127.0.0.1:5001...")
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1500)

        # 1. Open Transit modal
        print("1. Opening Transit Modal via #btnOpenTransit...")
        await page.locator("#btnOpenTransit").click()
        await page.wait_for_timeout(1000)

        # 2. Check Date Badge & Inputs
        badge_text = await page.locator(".transit-date-display-text").first.inner_text()
        print(f"2. Live Date Badge text: '{badge_text}'")
        assert len(badge_text) > 5, "Badge text is empty!"

        # 3. Check Root Buttons (Lagna, Moon, Sun)
        has_lagna = await page.locator(".btn-transit-root-lagna").first.is_visible()
        has_moon = await page.locator(".btn-transit-root-moon").first.is_visible()
        has_sun = await page.locator(".btn-transit-root-sun").first.is_visible()
        print(f"3. Root buttons present: Lagna={has_lagna}, Moon={has_moon}, Sun={has_sun}")
        assert has_lagna and has_moon and has_sun, "Missing one of the root buttons!"

        # 4. Click Sun (Surya Lagna)
        print("4. Testing Sun (Surya Lagna) root click...")
        await page.locator(".btn-transit-root-sun").first.click()
        await page.wait_for_timeout(1000)
        svg_sun = await page.locator(".transit-svg-container").first.inner_html()
        assert "Surya Lagna" in svg_sun or "Sun" in svg_sun
        print("  -> Sun root successfully rendered!")
        await page.screenshot(path="screenshot_transit_sun_root.png")

        # 5. Click Moon (Chandra Lagna)
        print("5. Testing Moon (Chandra Lagna) root click...")
        await page.locator(".btn-transit-root-moon").first.click()
        await page.wait_for_timeout(1000)
        svg_moon = await page.locator(".transit-svg-container").first.inner_html()
        assert "Chandra Lagna" in svg_moon or "Moon" in svg_moon
        print("  -> Moon root successfully rendered!")
        await page.screenshot(path="screenshot_transit_moon_root.png")

        # 6. Click Lagna (Ascendant)
        print("6. Testing Lagna root click...")
        await page.locator(".btn-transit-root-lagna").first.click()
        await page.wait_for_timeout(1000)
        svg_lagna = await page.locator(".transit-svg-container").first.inner_html()
        assert "Ascendant" in svg_lagna or "Lagna" in svg_lagna
        print("  -> Lagna root successfully rendered!")

        # 7. Test Step Forward
        print("7. Testing Step Forward button...")
        badge_before = await page.locator(".transit-date-display-text").first.inner_text()
        await page.locator(".btn-transit-step-fwd").first.click()
        await page.wait_for_timeout(1000)
        badge_after_fwd = await page.locator(".transit-date-display-text").first.inner_text()
        print(f"  Before: '{badge_before}', After Fwd: '{badge_after_fwd}'")
        assert badge_before != badge_after_fwd, "Date did not advance on step forward!"

        # 8. Test Step Backward
        print("8. Testing Step Backward button...")
        await page.locator(".btn-transit-step-back").first.click()
        await page.wait_for_timeout(1000)
        badge_after_back = await page.locator(".transit-date-display-text").first.inner_text()
        print(f"  After Back: '{badge_after_back}'")
        assert badge_after_fwd != badge_after_back, "Date did not step back!"

        # 9. Test Now button
        print("9. Testing Now button...")
        await page.locator(".btn-transit-step-fast-fwd").first.click()
        await page.wait_for_timeout(600)
        await page.locator(".btn-transit-now").first.click()
        await page.wait_for_timeout(1000)
        badge_now = await page.locator(".transit-date-display-text").first.inner_text()
        print(f"  After Now: '{badge_now}'")

        # 10. Test Play / Pause Animation Loop
        print("10. Testing Play / Pause button...")
        play_btn = page.locator(".btn-transit-play-pause").first
        await play_btn.click()
        print("  -> Clicked Play, waiting 1.5 seconds for animation frames...")
        await page.wait_for_timeout(1500)
        badge_during_play = await page.locator(".transit-date-display-text").first.inner_text()
        print(f"  Date during play: '{badge_during_play}'")
        await play_btn.click() # Pause
        print("  -> Clicked Pause")
        await page.wait_for_timeout(500)

        # 11. Final Screenshot
        await page.screenshot(path="screenshot_transit_verified.png")
        print("Saved screenshot_transit_verified.png")

        print(f"\nConsole Errors ({len(console_errors)}): {console_errors}")
        assert len(console_errors) == 0, f"Encountered console errors: {console_errors}"
        print("\nALL 11 INTERACTIVE TRANSIT TESTS PASSED SUCCESSFULLY!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
