import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 800})
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)
        
        await page.click('button:has-text("Load")')
        await page.wait_for_timeout(1500)
        
        await page.click('button:has-text("Metrics")')
        await page.wait_for_timeout(1000)
        
        # Hover over the Bala column header
        await page.hover('th:has-text("Bala (Age)")')
        await page.wait_for_timeout(500)
        await page.screenshot(path="screenshot_avasthas_hover.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
