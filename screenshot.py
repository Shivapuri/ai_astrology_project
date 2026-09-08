import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)
        
        try:
            # Load Angelina Jolie chart
            await page.evaluate("loadChart('angelina-jolie')")
            await page.wait_for_timeout(1500)

            # 1. Core Predictive Workspace
            await page.evaluate("changeWorkspace('core-predictive')")
            await page.wait_for_timeout(1000)
            await page.screenshot(path="screenshot_core_predictive.png")
            print("Captured screenshot_core_predictive.png")

            # 2. Planetary Information Table close-up
            cell2 = page.locator("#cell2")
            if await cell2.count() > 0:
                await cell2.screenshot(path="screenshot_planetary_info.png")
                print("Captured screenshot_planetary_info.png")

            # 3. The Big Four Vargas Workspace
            await page.evaluate("changeWorkspace('big-four')")
            await page.wait_for_timeout(1000)
            await page.screenshot(path="screenshot_big_four.png")
            print("Captured screenshot_big_four.png")

            # 4. Kala Right-Click Menu Modal
            await page.evaluate("openKalaMenu(400, 180)")
            await page.wait_for_timeout(600)
            await page.screenshot(path="screenshot_kala_menu.png")
            print("Captured screenshot_kala_menu.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(400)

            # 5. ShodasaVargas 16-in-1 Modal
            await page.evaluate("openShodasaVargasModal()")
            await page.wait_for_timeout(1000)
            await page.screenshot(path="screenshot_shodasa_vargas.png")
            print("Captured screenshot_shodasa_vargas.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(400)

            # 6. Tripod of Life Workspace
            await page.evaluate("changeWorkspace('tripod-of-life')")
            await page.wait_for_timeout(1000)
            await page.screenshot(path="screenshot_tripod_of_life.png")
            print("Captured screenshot_tripod_of_life.png")

            # 7. 5-Fold Bhava Inspector in Context Info
            await page.evaluate("assignWidget('info', document.getElementById('c3'))")
            await page.evaluate("document.getElementById('context-info-content').innerHTML = renderBhavaInspectorHtml(10, 'D1')")
            await page.wait_for_timeout(600)
            c3 = page.locator("#c3")
            if await c3.count() > 0:
                await c3.screenshot(path="screenshot_bhava_inspector.png")
                print("Captured screenshot_bhava_inspector.png")

            # 8. 16-Varga Lajjitadi Net Modifiers Widget
            await page.evaluate("assignWidget('varga-lajjitadi-modifiers', document.getElementById('c2'))")
            await page.wait_for_timeout(600)
            c2 = page.locator("#c2")
            if await c2.count() > 0:
                await c2.screenshot(path="screenshot_varga_lajjitadi.png")
                print("Captured screenshot_varga_lajjitadi.png")

            # 9. Rāśi Dṛṣṭi (Jaimini Sign Aspects) Widget
            await page.evaluate("assignWidget('rashi-drishti', document.getElementById('c1'))")
            await page.wait_for_timeout(600)
            c1 = page.locator("#c1")
            if await c1.count() > 0:
                await c1.screenshot(path="screenshot_rashi_drishti.png")
                print("Captured screenshot_rashi_drishti.png")

            # 10. Floating Bhava Chalita Cusps Window (Non-blurry, draggable & resizable)
            await page.evaluate("openBhavaCuspsModal()")
            await page.wait_for_timeout(600)
            await page.screenshot(path="screenshot_floating_bhava_chalita.png")
            print("Captured screenshot_floating_bhava_chalita.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(400)

            # 11. Floating Yoga Judgment Screen (Kala Ishta/Kashta & Subha/Asubha Dig Bala)
            await page.evaluate("openFloatingYogaJudgment()")
            await page.wait_for_timeout(600)
            await page.screenshot(path="screenshot_yoga_judgment.png")
            print("Captured screenshot_yoga_judgment.png")

            # Hover over a value cell in Yoga Judgment to show formula tooltip
            cell = page.locator("#widgetMaximizeContainer .yoga-judgment-table td.val-pos").first
            if await cell.count() > 0:
                await cell.hover()
                await page.wait_for_timeout(400)
                await page.screenshot(path="screenshot_yoga_judgment_tooltip.png")
                print("Captured screenshot_yoga_judgment_tooltip.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(400)

            # 12. Yoga Judgment widget in Grid cell
            await page.evaluate("assignWidget('yoga-judgment', document.getElementById('c1'))")
            await page.wait_for_timeout(600)
            c1 = page.locator("#c1")
            if await c1.count() > 0:
                await c1.screenshot(path="screenshot_yoga_judgment_widget.png")
                print("Captured screenshot_yoga_judgment_widget.png")

            # 13. House cusp click in North chart showing Context & Technical Info
            await page.evaluate("setGlobalChartStyle('north')")
            await page.evaluate("assignWidget('chart', document.getElementById('c1'))")
            await page.evaluate("assignWidget('info', document.getElementById('c2'))")
            await page.wait_for_timeout(800)
            cusp_el = page.locator("#c1 g.interactive[data-type='house']").first
            if await cusp_el.count() > 0:
                await cusp_el.click()
                await page.wait_for_timeout(600)
                await page.screenshot(path="screenshot_house_click_context_info.png")
                print("Captured screenshot_house_click_context_info.png")

            # 14. South Indian Chart Center Views (Sign Matrix & Anatomy)
            await page.evaluate("setGlobalChartStyle('south')")
            await page.evaluate("assignWidget('chart', document.getElementById('c1'))")
            await page.wait_for_timeout(600)
            center = page.locator("#c1 .svg-south .si-center-container")
            if await center.count() > 0:
                # Cycle to 4x3 Matrix view
                await center.click()
                await page.wait_for_timeout(500)
                await page.locator("#c1").screenshot(path="screenshot_south_center_matrix.png")
                print("Captured screenshot_south_center_matrix.png")

                # Cycle to Anatomy view
                await center.click()
                await page.wait_for_timeout(500)
                await page.locator("#c1").screenshot(path="screenshot_south_center_anatomy.png")
                print("Captured screenshot_south_center_anatomy.png")

            # 15. Dedicated Sign Attributes & Anatomy Widget in Cell
            await page.evaluate("assignWidget('sign-attributes', document.getElementById('c2'))")
            await page.wait_for_timeout(600)
            c2 = page.locator("#c2")
            if await c2.count() > 0:
                await c2.screenshot(path="screenshot_sign_attributes_widget.png")
                print("Captured screenshot_sign_attributes_widget.png")

                # Switch to Anatomy tab
                anatomy_tab = page.locator("#c2 .sign-attr-pill-btn", has_text="Kalapurusha Anatomy")
                if await anatomy_tab.count() > 0:
                    await anatomy_tab.click()
                    await page.wait_for_timeout(500)
                    await c2.screenshot(path="screenshot_sign_attributes_anatomy.png")
                    print("Captured screenshot_sign_attributes_anatomy.png")

            # 16. Floating Sign Attributes Modal
            await page.evaluate("openFloatingSignAttributes('D1')")
            await page.wait_for_timeout(600)
            await page.screenshot(path="screenshot_floating_sign_attributes.png")
            print("Captured screenshot_floating_sign_attributes.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(400)

            # 17. Export Astrological PDF Modal
            await page.evaluate("openExportModal()")
            await page.wait_for_timeout(600)
            await page.screenshot(path="screenshot_export_modal.png")
            print("Captured screenshot_export_modal.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(400)

            # 18. Settings Modal with Astrological PDF Export Option Card
            await page.evaluate("openSettingsModal()")
            await page.wait_for_timeout(600)
            await page.screenshot(path="screenshot_settings_export.png")
            print("Captured screenshot_settings_export.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(400)

            # 19. Kala Right-Click Menu with PDF Export Option
            await page.evaluate("openKalaMenu(500, 200)")
            await page.wait_for_timeout(600)
            await page.screenshot(path="screenshot_kala_menu_export.png")
            print("Captured screenshot_kala_menu_export.png")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(400)

        except Exception as e:
            print("Error:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

