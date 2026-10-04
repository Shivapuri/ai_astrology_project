import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        requests = []
        page.on("request", lambda req: requests.append(req.url) if "transit" in req.url else None)

        print("Navigating to http://127.0.0.1:5001...")
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1500)

        await page.evaluate("loadChart('angelina-jolie')")
        await page.wait_for_timeout(1500)

        # Open Transit modal
        print("Clicking #btnOpenTransit...")
        await page.locator("#btnOpenTransit").click()
        await page.wait_for_timeout(1000)

        print(f"Recorded transit requests after open: {len(requests)}")
        for r in requests:
            print(f"  Req: {r}")

        # Check date input value
        date_val = await page.locator(".transit-date-input").first.input_value()
        time_val = await page.locator(".transit-time-input").first.input_value()
        print(f"Initial Date Input Value: '{date_val}', Time: '{time_val}'")

        # Test Step Forward
        requests.clear()
        print("Clicking btn-transit-step-fwd...")
        await page.locator(".btn-transit-step-fwd").first.click()
        await page.wait_for_timeout(1000)
        print(f"Requests after step-fwd: {len(requests)}")
        for r in requests:
            print(f"  Req: {r}")
        date_val_after = await page.locator(".transit-date-input").first.input_value()
        print(f"Date after step-fwd: '{date_val_after}'")

        # Test Play button
        requests.clear()
        print("Clicking btn-transit-play-pause...")
        await page.locator(".btn-transit-play-pause").first.click()
        await page.wait_for_timeout(1500)
        print(f"Requests after 1.5s play: {len(requests)}")
        # Pause it
        await page.locator(".btn-transit-play-pause").first.click()

        # Check console logs
        print("\n--- Browser Console Logs ---")
        for log in console_logs[-20:]:
            print(log)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
