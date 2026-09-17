import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1500)
        
        # Load Shivapuri chart
        await page.evaluate("loadChart('589fabff-bf49-405a-9372-6d9566bf6955')")
        await page.wait_for_timeout(2000)
        
        # Select Mars
        await page.evaluate("window.clearAstrologicalEntitySelection(); selectAstrologicalEntity('planet', 'Mars', 'D1');")
        await page.wait_for_timeout(1000)
        
        # Capture chart closeup for Mars
        chart_el = page.locator(".grid-cell[data-widget='chart'] svg").first
        if await chart_el.count() > 0:
            await chart_el.screenshot(path="screenshot_shivapuri_mars_closeup.png")
            print("Captured screenshot_shivapuri_mars_closeup.png")
            
            # Select Jupiter
            await page.evaluate("window.clearAstrologicalEntitySelection(); selectAstrologicalEntity('planet', 'Jupiter', 'D1');")
            await page.wait_for_timeout(1000)
            await chart_el.screenshot(path="screenshot_shivapuri_jupiter_closeup.png")
            print("Captured screenshot_shivapuri_jupiter_closeup.png")
            
        await page.screenshot(path="screenshot_shivapuri_mars_full.png")
        print("Captured screenshot_shivapuri_mars_full.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
