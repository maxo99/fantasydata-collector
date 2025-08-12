import logging

from playwright.async_api import Page

from fp_scraper.config import DOWNLOAD_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def download_all_rankings(page: Page):
    try:
        # await page.goto(FP_RANKINGS_PAGE, timeout=60000)

        options = await get_dropdown_options(page)
        logger.info(f"Found {len(options)} options: {options}")

        for option in options:
            logger.info(f"Downloading CSV for: {option}")
            try:
                filename = await download_csv_for_option(page, option)
                logger.info(f"Downloaded: {filename}")
            except Exception as e:
                logger.error(f"Error downloading {option}: {e}")
    except Exception as e:
        logger.error(f"Failed to download all rankings: {e}")
        raise e


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
    try:
        dropdown_button = page.locator(
            '//*[@class="select-advanced__button"]/div/button'
        )
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
    except Exception as e:
        logger.error(f"Failed to download CSV for option: {option_text}")
        raise e
