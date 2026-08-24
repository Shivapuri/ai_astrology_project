import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        
        await page.goto('http://127.0.0.1:5001')
        await page.click('button:has-text("Load")')
        await page.wait_for_timeout(1000)
        await page.click('g[data-id="Sun"]')
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_highlight.png")
        await browser.close()

asyncio.run(main())
