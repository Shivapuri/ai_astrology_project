import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Go to the Flask app
        await page.goto("http://127.0.0.1:5001")
        
        # Wait for select to be populated, select first valid option if available
        try:
            # wait for page load
            await page.wait_for_timeout(500)
            
            # Find the load button and click it (we just need ANY chart loaded, or the default loaded state)
            # Actually, the user has to select a native first, but let's see if selecting option index 1 works
            select_element = await page.query_selector('#nativeSelect')
            if select_element:
                options = await select_element.query_selector_all('option')
                if len(options) > 1:
                    value = await options[1].get_attribute('value')
                    await page.select_option('#nativeSelect', value)
            
            # Click load chart
            load_btn = await page.query_selector('button:has-text("Load Chart")')
            if load_btn:
                await load_btn.click()
            
            # wait for the split js and chart to render
            await page.wait_for_timeout(2000)
            
        except Exception as e:
            print("Error interacting with UI:", e)
            
        await page.screenshot(path="screenshot.png", full_page=True)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
