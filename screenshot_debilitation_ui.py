import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        
        # Navigate to Astra
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1500)

        # 1. Load "Kailash (sister) new"
        kailash_id = "5cfd145f-8366-4313-ad4f-63bdc1900b53"
        await page.evaluate(f"loadChart('{kailash_id}')")
        await page.wait_for_timeout(2000)

        # 2. Check Settings Modal
        await page.evaluate("openSettingsModal()")
        await page.wait_for_timeout(800)
        await page.locator("#settingsModal .modal-card").screenshot(path="screenshot_settings_modal.png")
        print("Captured screenshot_settings_modal.png")
        await page.evaluate("closeSettingsModal()")
        await page.wait_for_timeout(500)

        # 3. Check Settings Dropdown
        # Hover / show settings dropdown
        dropdown = page.locator("#settingsMenuDropdown")
        await page.evaluate("document.getElementById('settingsMenuDropdown').style.display = 'block'")
        await page.locator("#settingsMenuDropdown").screenshot(path="screenshot_settings_dropdown.png")
        print("Captured screenshot_settings_dropdown.png")
        await page.evaluate("document.getElementById('settingsMenuDropdown').style.display = ''")
        await page.wait_for_timeout(500)

        # 4. In default 'kala_degree' mode, assign dignities widget to cell1
        await page.evaluate("assignWidget('dignities', document.getElementById('cell1'))")
        await page.wait_for_timeout(1000)
        await page.locator("#cell1").screenshot(path="screenshot_dignities_kala_degree.png")
        print("Captured screenshot_dignities_kala_degree.png")

        # 5. Switch to 'whole_sign' mode
        await page.evaluate("setDebilitationMode('whole_sign')")
        await page.wait_for_timeout(2000)
        await page.locator("#cell1").screenshot(path="screenshot_dignities_whole_sign.png")
        print("Captured screenshot_dignities_whole_sign.png")

        # 6. Switch back to 'kala_degree' mode
        await page.evaluate("setDebilitationMode('kala_degree')")
        await page.wait_for_timeout(1500)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
