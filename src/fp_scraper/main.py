import asyncio
import logging
import sys
from datetime import datetime

from playwright.async_api import Page, async_playwright
from playwright_stealth import Stealth

from fp_scraper.config import DOWNLOAD_DIR
from fp_scraper.constants import BROWSER_ARGS, FP_RANKINGS_PAGE
from fp_scraper.handlers import content as content_handler
from fp_scraper.pages import player_rankings as player_rankings_page
from fp_scraper.pages.common import login
from fp_scraper.request_recorder import RequestRecorder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    record_mode = "--record" in sys.argv
    replay_mode = "--replay" in sys.argv
    headless = "--headless" in sys.argv
    process_results = False

    recorder = None
    if RequestRecorder and (record_mode or replay_mode):
        recorder = RequestRecorder()
        mode = "record" if record_mode else "replay"
        recorder.set_cassette(
            f"fantasypros_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}", mode=mode
        )

    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=headless, args=BROWSER_ARGS)
        logger.info(f"Launching browser with {headless=} and {BROWSER_ARGS=}")
        
        context = None
        if record_mode:
            context = await browser.new_context(
                record_video_dir="videos/",
                record_video_size={"width": 640, "height": 480},
            )
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page: Page = await context.new_page()
        else:
            page: Page = await browser.new_page()

        if recorder:
            logger.info(f"Using request recorder in {recorder.mode} mode")
            recorder.setup_recording(page)

        try:
            await page.goto(FP_RANKINGS_PAGE, wait_until="domcontentloaded", timeout=60000)

            await login(page)
            await player_rankings_page.download_all_rankings(page)
            process_results = True
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            await page.screenshot(path=DOWNLOAD_DIR / "error_screenshot.png")

        finally:
            if record_mode and context:
                await context.tracing.stop(path = DOWNLOAD_DIR / "trace.zip")


            if recorder and record_mode:
                recorder.save_cassette()
            await browser.close()

    if process_results:
        content_handler.merge_csvs()


if __name__ == "__main__":
    asyncio.run(main())
