import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)
        
        # Click the circular button
        try:
            await page.click('#btn-circular')
            print("Clicked circular button")
            await page.wait_for_timeout(1000)
        except Exception as e:
            print("Could not click circular button", e)
            
        await page.screenshot(path="screenshot.png", full_page=True)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
