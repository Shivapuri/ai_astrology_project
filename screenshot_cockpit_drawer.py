import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use widescreen viewport to properly display the 3-column layout
        page = await browser.new_page(viewport={"width": 1920, "height": 1200})
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)

        # Load chart
        await page.evaluate("loadChart('angelina-jolie')")
        await page.wait_for_timeout(2500)

        # Set single pane (widescreen)
        await page.evaluate("""() => {
            const container = document.getElementById('grid-container');
            container.innerHTML = '<div class="grid-cell" id="cell1" style="width:100%; height:100%;"><div class="grid-cell-content"></div></div>';
        }""")
        await page.wait_for_timeout(500)

        # Assign master diagnostic widget to cell1
        await page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
        await page.wait_for_timeout(1000)

        # Click Jupiter row to open drawer
        jup_row = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row[data-id='Jupiter']")
        await jup_row.click()
        await page.wait_for_timeout(1000)

        # Screenshot Jupiter drawer
        jup_drawer = page.locator("#cell1 #drawer-Jupiter .diagnostic-drawer-cockpit")
        await jup_drawer.screenshot(path="screenshot_cockpit_jupiter.png")
        print("Captured screenshot_cockpit_jupiter.png")

        # Also screenshot Venus drawer
        venus_row = page.locator("#cell1 .master-diagnostic-table tbody tr.diagnostic-row[data-id='Venus']")
        await venus_row.click()
        await page.wait_for_timeout(1000)
        venus_drawer = page.locator("#cell1 #drawer-Venus .diagnostic-drawer-cockpit")
        await venus_drawer.screenshot(path="screenshot_cockpit_venus.png")
        print("Captured screenshot_cockpit_venus.png")

        # Also take full master diagnostic widget screenshot
        await page.locator("#cell1").screenshot(path="screenshot_master_diagnostic_with_cockpit.png")
        print("Captured screenshot_master_diagnostic_with_cockpit.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
