import logging

from playwright.async_api import Page

from fp_scraper.config import FP_EMAIL, FP_PASSWORD
from fp_scraper.handlers.captcha import SolveCaptcha, check_for_captcha
from fp_scraper.utils import delay_page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def login(page: Page):
    try:
        logger.info("Starting login process")

        await page.click("text=Get Started")
        await delay_page(page)

        if not FP_EMAIL or not FP_PASSWORD:
            raise ValueError(
                "FANTASYPROS_EMAIL and FANTASYPROS_PASSWORD must be set in .env file"
            )
        await page.fill('input[id="username"]', FP_EMAIL)
        await page.fill('input[id="password"]', FP_PASSWORD)
        await delay_page(page)

        await page.click('button[type="submit"]')
        logger.info("Login submitted")
        await page.wait_for_load_state()

        captcha_present = await check_for_captcha(page)
        captcha_stopped = await page.get_by_text("Unable to sign in").is_visible()
        if captcha_stopped and captcha_present:
            try:
                logger.info("Captcha detected, attempting to solve")
                solver = SolveCaptcha(page)
                await solver.start()
                logger.info("Captcha solved")
                await page.click('button[type="submit"]')
                await page.wait_for_load_state()
            except Exception as e:
                logger.error(f"Captcha solving failed: {e}")

        else:
            logger.info("Login successful, without captcha")
            await page.wait_for_load_state()

        await page.click('//a[@aria-label="dismiss page"]')
        await page.wait_for_load_state()
    except Exception as e:
        logger.error("Login failed")
        raise e
