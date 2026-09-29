import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 950})
        
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(2000)

        # 1. Load native chart
        kailash_id = "5cfd145f-8366-4313-ad4f-63bdc1900b53"
        await page.evaluate(f"loadChart('{kailash_id}')")
        await page.wait_for_timeout(2000)

        # 2. Toggle Nakshatra Display ON
        await page.evaluate("setNakshatraDisplay(true)")
        await page.wait_for_timeout(2000)

        # 3. Capture South Indian Chart with Nakshatras
        await page.evaluate("setGlobalChartStyle('south')")
        await page.wait_for_timeout(1000)
        await page.locator("#grid-container").screenshot(path="screenshot_live_south_nakshatras.png")
        print("Captured screenshot_live_south_nakshatras.png")

        # 4. Capture North Indian Chart with Nakshatras
        await page.evaluate("setGlobalChartStyle('north')")
        await page.wait_for_timeout(1000)
        await page.locator("#grid-container").screenshot(path="screenshot_live_north_nakshatras.png")
        print("Captured screenshot_live_north_nakshatras.png")

        # 5. Capture Bi-Wheel Chart with Nakshatras
        await page.evaluate("setGlobalChartStyle('biwheel')")
        await page.wait_for_timeout(1000)
        await page.locator("#grid-container").screenshot(path="screenshot_live_biwheel_nakshatras.png")
        print("Captured screenshot_live_biwheel_nakshatras.png")

        # Reset setting to false for clean state
        await page.evaluate("setNakshatraDisplay(false)")
        await page.wait_for_timeout(500)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
