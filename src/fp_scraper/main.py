import asyncio
import logging
from datetime import datetime

import pandas as pd
from playwright.async_api import Page, async_playwright
from playwright_stealth import Stealth

from fp_scraper.captcha_solver import SolveCaptcha
from fp_scraper.config import DOWNLOAD_DIR, FP_EMAIL, FP_PASSWORD
from fp_scraper.constants import BROWSER_ARGS, FP_RANKINGS_PAGE
from fp_scraper.request_recorder import RequestRecorder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def login(page):
    try:
        await page.click("text=Get Started")
        await page.fill('input[id="username"]', FP_EMAIL)
        await page.fill('input[id="password"]', FP_PASSWORD)

        # await page.wait_for_load_state("networkidle")
        await page.click('button[type="submit"]')
        logger.info("Login submitted")

        solver = SolveCaptcha(page)
        await solver.start()
        logger.info("Captcha solved")

        await page.click('button:has-text("Remind me later")')
        await page.wait_for_load_state("networkidle")
    except Exception as e:
        logger.error("Login failed")
        raise e


# async def wait_for_captcha(page: Page):
#     try:
#         await page.wait_for_selector(
#             "iframe[src*='recaptcha'], div.g-recaptcha, div.h-captcha, iframe#cf-chl-widget",
#             timeout=10000,
#         )
#         logger.info("Captcha detected")
#         return True
#     except Exception as e:
#         logger.info(f"No captcha detected {e=}")
#         return False


async def get_dropdown_options(page: Page):
    try:
        logger.info("Retrieving dropdown options")
        dropdown_button = page.locator('//*[@id="select-advanced-2136961"]/div/button')
        await dropdown_button.click()

        options = await page.locator('//*[@id="select-advanced-2136961"]//li').all()
        option_texts = []
        for option in options:
            text = await option.text_content()
            if text:
                option_texts.append(text.strip())
        logger.info(f"Dropdown options retrieved: {option_texts}")

        await dropdown_button.click()
        return option_texts
    except Exception as e:
        logger.error("Failed to retrieve dropdown options")
        raise e


async def download_csv_for_option(page: Page, option_text: str):
    dropdown_button = page.locator('//*[@class="select-advanced__button"]/div/button')
    await dropdown_button.click()

    option = page.locator(
        f'//*[@id="select-advanced-2136961"]//li:has-text("{option_text}")'
    )
    await option.click()
    await page.wait_for_load_state("networkidle")

    async with page.expect_download() as download_info:
        await page.locator(
            '//*[@id="rankings-app"]/div[2]/div[2]/div[3]/div/button[1]/i'
        ).click()

    download = await download_info.value
    filename = f"{option_text.replace(' ', '_').replace('/', '_')}.csv"
    await download.save_as(DOWNLOAD_DIR / filename)
    return filename


def merge_csvs():
    csv_files = list(DOWNLOAD_DIR.glob("*.csv"))
    if not csv_files:
        print("No CSV files found to merge")
        return

    all_dataframes = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df["Source"] = csv_file.stem
        all_dataframes.append(df)

    merged_df = pd.concat(all_dataframes, ignore_index=True)

    duplicates = merged_df[merged_df.duplicated(subset=["Player Name"], keep=False)]
    if not duplicates.empty:
        print(f"WARNING: Found {len(duplicates)} duplicate player entries:")
        print(duplicates[["Player Name", "Source"]].to_string(index=False))

    output_file = DOWNLOAD_DIR / "merged_rankings.csv"
    merged_df.to_csv(output_file, index=False)
    print(f"Merged data saved to: {output_file}")


async def main():
    import sys

    record_mode = "--record" in sys.argv
    replay_mode = "--replay" in sys.argv

    recorder = None
    if RequestRecorder and (record_mode or replay_mode):
        recorder = RequestRecorder()
        mode = "record" if record_mode else "replay"
        recorder.set_cassette(
            f"fantasypros_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}", mode=mode
        )

    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=False, args=BROWSER_ARGS)
        page: Page = await browser.new_page()

        if recorder:
            logger.info(f"Using request recorder in {recorder.mode} mode")
            recorder.setup_recording(page)

        try:
            await page.goto(FP_RANKINGS_PAGE, timeout=60000)

            await login(page)
            await page.goto(FP_RANKINGS_PAGE, timeout=60000)

            options = await get_dropdown_options(page)
            print(f"Found {len(options)} options: {options}")

            for option in options:
                print(f"Downloading CSV for: {option}")
                try:
                    filename = await download_csv_for_option(page, option)
                    print(f"Downloaded: {filename}")
                except Exception as e:
                    print(f"Error downloading {option}: {e}")

        except Exception as e:
            print(f"Error during scraping: {e}")
            await page.screenshot(path=DOWNLOAD_DIR / "error_screenshot.png")

        finally:
            if recorder and record_mode:
                recorder.save_cassette()
            await browser.close()

    merge_csvs()


if __name__ == "__main__":
    asyncio.run(main())
