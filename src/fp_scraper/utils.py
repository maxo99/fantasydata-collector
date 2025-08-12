import logging
import random

from playwright.async_api import Page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def delay_page(page: Page):
    delay = random.randint(1, 3) * 1000
    logger.info(f"Delaying for {delay} milliseconds")
    await page.wait_for_timeout(delay)
