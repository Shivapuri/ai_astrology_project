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

        await page.screenshot(path="screenshot_master_diagnostic_modal.png")
        print("Captured screenshot_master_diagnostic_modal.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
