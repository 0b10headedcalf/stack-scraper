import asyncio
from playwright.async_api import async_playwright

site_arg = "https://example.com"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(site_arg)
        print(await page.title())
        await browser.close()

asyncio.run(main())
