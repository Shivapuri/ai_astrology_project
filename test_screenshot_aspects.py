import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:5001')
        await page.click('button:has-text("Load")')
        await page.wait_for_timeout(1000)
        # Click the Aspects tab
        await page.click('button[data-target="tab-aspects"]')
        await page.wait_for_timeout(500)
        await page.screenshot(path="screenshot_aspects.png")
        await browser.close()

asyncio.run(main())
