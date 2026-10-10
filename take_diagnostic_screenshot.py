import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1000})
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)

        # Load Shivapuri Baba chart
        await page.evaluate("loadChart('589fabff-bf49-405a-9372-6d9566bf6955')")
        await page.wait_for_timeout(2500)

        # Assign master diagnostic widget to cell1
        await page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
        await page.wait_for_timeout(800)

        # Screenshot cell1
        await page.locator("#cell1").screenshot(path="screenshot_master_diagnostic_cell1.png")
        print("Captured screenshot_master_diagnostic_cell1.png")

        # Now maximize master diagnostic widget
        await page.evaluate("maximizeTableFromWidget(document.querySelector('#cell1 .btn-widget-maximize'))")
        await page.wait_for_timeout(800)

        # Focus screenshot on the modal table body
        modal_table = page.locator("#widgetMaximizeContainer .master-diagnostic-table")
        await modal_table.screenshot(path="screenshot_master_diag_tbody.png")
        print("Captured screenshot_master_diag_tbody.png")

        # Also screenshot Lagna and Sun rows specifically
        lagna_row = page.locator("#widgetMaximizeContainer tbody tr[data-id='Lagna']")
        await lagna_row.screenshot(path="screenshot_lagna_row.png")
        print("Captured screenshot_lagna_row.png")

        sun_row = page.locator("#widgetMaximizeContainer tbody tr[data-id='Sun']")
        await sun_row.screenshot(path="screenshot_sun_row.png")
        print("Captured screenshot_sun_row.png")

        # And Venus row specifically
        venus_row = page.locator("#widgetMaximizeContainer tbody tr[data-id='Venus']")
        await venus_row.screenshot(path="screenshot_venus_row.png")
        print("Captured screenshot_venus_row.png")

        # And Rahu row specifically
        rahu_row = page.locator("#widgetMaximizeContainer tbody tr[data-id='Rahu']")
        await rahu_row.screenshot(path="screenshot_rahu_row.png")
        print("Captured screenshot_rahu_row.png")

        # Click Mars row to open drawer and screenshot drawer
        mars_row = page.locator("#widgetMaximizeContainer tbody tr[data-id='Mars']")
        await mars_row.click()
        await page.wait_for_timeout(800)
        mars_drawer = page.locator("#widgetMaximizeContainer #drawer-Mars")
        await mars_drawer.screenshot(path="screenshot_mars_drawer.png")
        print("Captured screenshot_mars_drawer.png")

        # Now load Priyanka Chopra chart and capture table
        await page.evaluate("loadChart('priyanka-chopra')")
        await page.wait_for_timeout(2000)
        modal_table_priyanka = page.locator("#widgetMaximizeContainer .master-diagnostic-table")
        await modal_table_priyanka.screenshot(path="screenshot_priyanka_chopra_table.png")
        print("Captured screenshot_priyanka_chopra_table.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
