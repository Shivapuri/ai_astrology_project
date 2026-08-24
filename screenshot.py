import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 800})
        
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)
        
        try:
            await page.click('button:has-text("Load")')
            await page.wait_for_timeout(2000)
            
            await page.click('button:has-text("Shadbala")')
            await page.wait_for_timeout(1000)
            await page.screenshot(path="screenshot_shadbala.png")
            
        except Exception as e:
            print("Error clicking:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
