import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        async def on_response(response):
            if "track" in response.url:
                print(response.url)
                
        page.on("response", on_response)
        await page.goto("https://open.spotify.com/intl-it/track/0CokSRCu5hZgPxcZBaEzVE")
        await asyncio.sleep(5)
        await browser.close()

asyncio.run(main())
