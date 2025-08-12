import logging

from playwright.async_api import Page

from fp_scraper.config import FP_EMAIL, FP_PASSWORD
from fp_scraper.handlers.captcha import SolveCaptcha
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

        await page.wait_for_load_state()
        await page.click('button[type="submit"]')
        logger.info("Login submitted")
        if page.url.startswith("https://www.fantasypros.com/get-started/"):
            logger.info("Login successful, without captcha")
            await page.wait_for_load_state()
        else:
            solver = SolveCaptcha(page)
            await solver.start()
            logger.info("Captcha solved")
        await page.click('button[type="submit"]')

        await page.click('button:has-text("Remind me later")')
        await page.wait_for_load_state()
    except Exception as e:
        logger.error("Login failed")
        raise e
