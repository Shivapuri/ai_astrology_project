import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1100})
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)

        # Select a native if available
        await page.evaluate("""
            const sel = document.getElementById('nativeSelect');
            if (sel && sel.options.length > 1) {
                sel.selectedIndex = 1;
                loadChart();
            }
        """)
        await page.wait_for_timeout(2500)

        # Open floating full report modal
        await page.evaluate("if (window.openFloatingReport) openFloatingReport();")
        await page.wait_for_timeout(1500)

        # 1. Capture Section 5 (Elemental & Modal Balance)
        elem_sec = page.locator("#widgetMaximizeContainer .report-elemental-modal-section")
        if await elem_sec.count() > 0:
            await elem_sec.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await elem_sec.screenshot(path="screenshot_report_elemental_modal.png")
            print("Captured screenshot_report_elemental_modal.png")
        else:
            print("WARNING: .report-elemental-modal-section not found in modal!")

        # 2. Capture Section 6 (Interactive Planetary Synthesis Desk)
        desk_sec = page.locator("#widgetMaximizeContainer .report-planet-synthesis-section")
        if await desk_sec.count() > 0:
            await desk_sec.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await desk_sec.screenshot(path="screenshot_report_planetary_desk.png")
            print("Captured screenshot_report_planetary_desk.png")
        else:
            print("WARNING: .report-planet-synthesis-section not found in modal!")

        # 3. Test clicking a different planet in the selector bar
        chips = page.locator("#widgetMaximizeContainer .btn-planet-chip")
        chip_count = await chips.count()
        print(f"Found {chip_count} planet chips in selector bar")
        if chip_count > 1:
            # Click the second planet chip
            await chips.nth(1).click()
            await page.wait_for_timeout(600)
            await desk_sec.screenshot(path="screenshot_report_planetary_desk_clicked.png")
            print("Captured screenshot_report_planetary_desk_clicked.png")

        # 4. Test expanding "View Sign Architecture (Flowchart)" in Section 2
        toggle_btn = page.locator("#widgetMaximizeContainer #card-col-rashi .btn-toggle-flowchart")
        if await toggle_btn.count() > 0:
            await toggle_btn.scroll_into_view_if_needed()
            await toggle_btn.click()
            await page.wait_for_timeout(800)
            rising_sec = page.locator("#widgetMaximizeContainer .report-rising-signs-section")
            await rising_sec.screenshot(path="screenshot_report_rising_flowchart_toggled.png")
            print("Captured screenshot_report_rising_flowchart_toggled.png")

        # 5. Full modal screenshot
        modal_card = page.locator("#widgetMaximizeCard")
        if await modal_card.count() > 0:
            await modal_card.screenshot(path="screenshot_report_modal_full_view.png")
            print("Captured screenshot_report_modal_full_view.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
