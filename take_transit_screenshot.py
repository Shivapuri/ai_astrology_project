import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)
        
        # Load a native chart
        await page.evaluate("loadChart('angelina-jolie')")
        await page.wait_for_timeout(1000)

        # 1. Capture the main screen showing top toolbar with "🪐 Transits" button & "T" on charts
        await page.screenshot(path="screenshot_main_with_transit_btn.png")
        print("Captured screenshot_main_with_transit_btn.png")

        # 2. Click the new top "🪐 Transits" button to open floating window
        await page.locator("#btnOpenTransit").click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_floating_transit_modal.png")
        print("Captured screenshot_floating_transit_modal.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
