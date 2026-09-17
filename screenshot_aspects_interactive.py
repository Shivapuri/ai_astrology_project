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
        await page.wait_for_timeout(2000)
        
        # 1. Switch to a workspace with chart and master diagnostic or rashi drishti
        await page.evaluate("changeWorkspace('deep-diagnostic')")
        await page.wait_for_timeout(1500)
        await page.screenshot(path="screenshot_aspects_initial.png")
        print("Captured screenshot_aspects_initial.png")

        # 2. Click Mars in the Master Diagnostic Table
        await page.evaluate("selectAstrologicalEntity('planet', 'Mars', 'D1')")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_aspects_mars_selected.png")
        print("Captured screenshot_aspects_mars_selected.png")

        # 3. Click Jupiter (Benefic) on the chart or table
        await page.evaluate("selectAstrologicalEntity('planet', 'Jupiter', 'D1')")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_aspects_jupiter_selected.png")
        print("Captured screenshot_aspects_jupiter_selected.png")

        # 4. Click Lagna (Ascendant)
        await page.evaluate("selectAstrologicalEntity('planet', 'Lagna', 'D1')")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_aspects_lagna_selected.png")
        print("Captured screenshot_aspects_lagna_selected.png")

        # 5. Click Aries (Sign Aspect / Rasi Drishti)
        await page.evaluate("window.clearAstrologicalEntitySelection(); selectAstrologicalEntity('sign', 'Aries', 'D1');")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_aspects_aries_selected.png")
        print("Captured screenshot_aspects_aries_selected.png")

        # 6. Capture closeup of chart with aspect arrows and degree badges
        chart_el = page.locator(".grid-cell[data-widget='chart'] svg").first
        if await chart_el.count() > 0:
            await page.evaluate("window.clearAstrologicalEntitySelection(); selectAstrologicalEntity('sign', 'Aries', 'D1');")
            await page.wait_for_timeout(500)
            await chart_el.screenshot(path="screenshot_chart_aries_aspects.png")
            print("Captured screenshot_chart_aries_aspects.png")

            await page.evaluate("window.clearAstrologicalEntitySelection(); selectAstrologicalEntity('planet', 'Mars', 'D1');")
            await page.wait_for_timeout(500)
            await chart_el.screenshot(path="screenshot_chart_mars_aspects.png")
            print("Captured screenshot_chart_mars_aspects.png")

            await page.evaluate("window.clearAstrologicalEntitySelection(); selectAstrologicalEntity('planet', 'Jupiter', 'D1');")
            await page.wait_for_timeout(500)
            await chart_el.screenshot(path="screenshot_chart_jupiter_aspects.png")
            print("Captured screenshot_chart_jupiter_aspects.png")

        # 7. Capture closeup of Master Diagnostic table with dynamic aspect badges
        diag_el = page.locator("#widget-master-diagnostic")
        if await diag_el.count() > 0:
            await page.evaluate("window.clearAstrologicalEntitySelection(); selectAstrologicalEntity('planet', 'Jupiter', 'D1');")
            await page.wait_for_timeout(500)
            await diag_el.screenshot(path="screenshot_diag_table_jupiter_aspects.png")
            print("Captured screenshot_diag_table_jupiter_aspects.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
