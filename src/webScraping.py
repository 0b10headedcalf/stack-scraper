import asyncio
from playwright.async_api import async_playwright


async def scrapeInstagram():
    site_arg = f"https://instagram.com/"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(site_arg)
        print(await page.title())
        await browser.close()

asyncio.run(scrapeInstagram())
