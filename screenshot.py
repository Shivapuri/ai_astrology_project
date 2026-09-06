import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(2000)
        
        try:
            await page.click('button:has-text("Load")')
            await page.wait_for_timeout(2000)

            # Assign Phase 8 widgets to cells for visual inspection
            await page.evaluate("""
                assignWidget('chart', document.getElementById('cell1'));
                assignWidget('dashas-timeline', document.getElementById('cell2'));
                assignWidget('ashtakavarga', document.getElementById('cell3'));
                assignWidget('vimshopaka', document.getElementById('cell4'));
            """)
            await page.wait_for_timeout(1000)

            await page.screenshot(path="screenshot_new_layout.png")
            
            # Click maximize on Ashtakavarga table to verify modal
            btn = page.locator('.grid-cell[data-widget="ashtakavarga"] .btn-widget-maximize').first
            if await btn.count() > 0:
                await btn.click()
                await page.wait_for_timeout(800)
                await page.screenshot(path="screenshot_maximize_modal.png")
                # Close modal
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)

            # Assign Nakshatras to cell2 to visually inspect Phase 3 fields
            await page.evaluate("assignWidget('nakshatras', document.getElementById('cell2'));")
            await page.wait_for_timeout(800)
            await page.screenshot(path="screenshot_nakshatras.png")
        except Exception as e:
            print("Error:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
