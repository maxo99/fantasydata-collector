import logging

from fp_scraper.config import FP_EMAIL, FP_PASSWORD
from fp_scraper.handlers.captcha import SolveCaptcha

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
        if page.url.startswith("https://www.fantasypros.com/get-started/"):
            logger.info("Login successful, without captcha")
            await page.wait_for_load_state("networkidle")
        else:
            solver = SolveCaptcha(page)
            await solver.start()
            logger.info("Captcha solved")

        await page.click('button:has-text("Remind me later")')
        await page.wait_for_load_state("networkidle")
    except Exception as e:
        logger.error("Login failed")
        raise e
