import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1500)
        
        # Load Angelina Jolie chart
        await page.evaluate("loadChart('angelina-jolie')")
        await page.wait_for_timeout(1500)
        
        # 1. Assign Master Graha Diagnostics to the first grid cell
        await page.evaluate("""
            const firstCell = document.querySelector('.grid-cell');
            if (firstCell) {
                assignWidget('master-diagnostic', firstCell);
            }
        """)
        await page.wait_for_timeout(1000)
        
        first_cell = page.locator(".grid-cell").first
        await first_cell.screenshot(path="screenshot_master_diag_cell.png")
        print("Captured screenshot_master_diag_cell.png")
        
        # 2. Maximize Master Graha Diagnostics Modal
        await page.evaluate("openFloatingMasterDiagnostic()")
        await page.wait_for_timeout(1000)
        
        modal = page.locator("#widgetMaximizeModal")
        await modal.screenshot(path="screenshot_master_diag_maximized.png")
        print("Captured screenshot_master_diag_maximized.png")
        
        # 3. Switch to D9 Navamsa in maximized view
        v_select = page.locator("#widgetMaximizeContainer .varga-select")
        if await v_select.count() > 0:
            await v_select.select_option("D9")
            await page.wait_for_timeout(1000)
            await modal.screenshot(path="screenshot_master_diag_d9.png")
            print("Captured screenshot_master_diag_d9.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
