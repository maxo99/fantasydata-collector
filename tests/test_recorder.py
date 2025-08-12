import asyncio
from playwright.async_api import async_playwright

from fp_scraper import RequestRecorder


async def test_recording():
    recorder = RequestRecorder()
    recorder.set_cassette("test", mode="record")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        recorder.setup_recording(page)

        await page.goto("https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php")
        await page.wait_for_load_state("networkidle")
        await browser.close()

    recorder.save_cassette()


if __name__ == "__main__":
    asyncio.run(test_recording())
