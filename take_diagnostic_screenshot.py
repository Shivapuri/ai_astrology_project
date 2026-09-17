import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1000})
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)

        # Load Angelina Jolie chart
        await page.evaluate("loadChart('angelina-jolie')")
        await page.wait_for_timeout(1500)

        # Assign master diagnostic widget to cell1
        await page.evaluate("assignWidget('master-diagnostic', document.getElementById('cell1'))")
        await page.wait_for_timeout(800)

        # Screenshot cell1
        await page.locator("#cell1").screenshot(path="screenshot_master_diagnostic_cell1.png")
        print("Captured screenshot_master_diagnostic_cell1.png")

        # Now maximize master diagnostic widget
        await page.evaluate("maximizeTableFromWidget(document.querySelector('#cell1 .btn-widget-maximize'))")
        await page.wait_for_timeout(800)

        # Hover over Sun's receipt button in modal to trigger receipt tooltip
        receipt_btn = page.locator("#widgetMaximizeModal .master-diagnostic-table tbody tr:nth-child(2) td:nth-child(8) span:has-text('Receipt')").first
        if await receipt_btn.count() > 0:
            await receipt_btn.hover()
            await page.wait_for_timeout(500)

        await page.screenshot(path="screenshot_master_diagnostic_modal.png")
        print("Captured screenshot_master_diagnostic_modal.png")

        # Scroll down vertically inside modal to verify sticky header
        await page.evaluate("""() => {
            const scroller = document.querySelector('#widgetMaximizeModal .responsive-table-container') ||
                             document.querySelector('#widgetMaximizeModal div[style*="overflow: auto"]') ||
                             document.querySelector('#widgetMaximizeContainer');
            if (scroller) scroller.scrollTop = 250;
        }""")
        await page.wait_for_timeout(500)
        await page.screenshot(path="screenshot_master_diagnostic_scrolled.png")
        print("Captured screenshot_master_diagnostic_scrolled.png")

        # Load Angelina Jolie chart to inspect significant aspects
        await page.evaluate("loadChart('angelina-jolie')")
        await page.wait_for_timeout(1500)
        await page.screenshot(path="screenshot_master_diagnostic_angelina.png")
        print("Captured screenshot_master_diagnostic_angelina.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
