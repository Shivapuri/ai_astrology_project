import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1000})
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)

        # Load first available native
        await page.evaluate("""
            const sel = document.getElementById('nativeSelect');
            if (sel && sel.options.length > 1) {
                sel.selectedIndex = 1;
                loadChart();
            }
        """)
        await page.wait_for_timeout(2500)

        # Assign 'report' widget to cell1
        await page.evaluate("assignWidget('report', document.getElementById('cell1'))")
        await page.wait_for_timeout(800)

        # 1. Capture cell1 Tab 1 (Polarity & Stars)
        await page.locator("#cell1").screenshot(path="screenshot_report_cell1_polarity.png")
        print("Captured screenshot_report_cell1_polarity.png")

        # 2. Switch to Tab 2 (Elements & Axis)
        await page.evaluate("""
            const btn = document.querySelector('#cell1 .report-pill-btn[data-tab="environment"]');
            if (btn) switchReportTab(btn, 'environment');
        """)
        await page.wait_for_timeout(500)
        await page.locator("#cell1").screenshot(path="screenshot_report_cell1_environment.png")
        print("Captured screenshot_report_cell1_environment.png")

        # 3. Switch to Tab 3 (Planetary Rank)
        await page.evaluate("""
            const btn = document.querySelector('#cell1 .report-pill-btn[data-tab="prominence"]');
            if (btn) switchReportTab(btn, 'prominence');
        """)
        await page.wait_for_timeout(500)
        await page.locator("#cell1").screenshot(path="screenshot_report_cell1_prominence.png")
        print("Captured screenshot_report_cell1_prominence.png")

        # 4. Switch to Tab 4 (Synthesis Desk)
        await page.evaluate("""
            const btn = document.querySelector('#cell1 .report-pill-btn[data-tab="synthesis"]');
            if (btn) switchReportTab(btn, 'synthesis');
        """)
        await page.wait_for_timeout(500)
        await page.locator("#cell1").screenshot(path="screenshot_report_cell1_synthesis.png")
        print("Captured screenshot_report_cell1_synthesis.png")

        # 5. Open Full Floating Report Modal and capture
        await page.evaluate("openFloatingReport()")
        await page.wait_for_timeout(800)
        await page.locator("#widgetMaximizeCard").screenshot(path="screenshot_report_modal_full.png")
        print("Captured screenshot_report_modal_full.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
