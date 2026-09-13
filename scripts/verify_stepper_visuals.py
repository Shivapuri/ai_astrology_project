import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)
        
        # Load a chart
        await page.evaluate("loadChart('589fabff-bf49-405a-9372-6d9566bf6955')")
        await page.wait_for_timeout(1500)
        
        # 1. Capture chart cell with resting stepper
        cell1 = page.locator("#cell1")
        await cell1.screenshot(path="screenshot_stepper_resting.png")
        print("Captured screenshot_stepper_resting.png")
        
        # 2. Hover over chart to reveal stepper
        await cell1.hover()
        await page.wait_for_timeout(400)
        await cell1.screenshot(path="screenshot_stepper_hovered.png")
        print("Captured screenshot_stepper_hovered.png")
        
        # 3. Click +1m button
        btn_plus_1m = cell1.locator("button:has-text('+1m')")
        await btn_plus_1m.click()
        await page.wait_for_timeout(1000)
        
        # 4. Capture active preview state (pinned open with badge, reset, and save buttons)
        await cell1.screenshot(path="screenshot_stepper_active_preview.png")
        print("Captured screenshot_stepper_active_preview.png")
        
        # Also capture the top toolbar to see preview in subtitle
        await page.locator(".top-toolbar").screenshot(path="screenshot_top_toolbar_preview.png")
        print("Captured screenshot_top_toolbar_preview.png")
        
        # 5. Click reset button
        reset_btn = cell1.locator(".stepper-btn-reset")
        await reset_btn.click()
        await page.wait_for_timeout(1000)
        await cell1.screenshot(path="screenshot_stepper_reset.png")
        print("Captured screenshot_stepper_reset.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
