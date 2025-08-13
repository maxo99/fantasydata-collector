import logging
import os
from urllib.request import urlretrieve

from playwright.async_api import Page
from pydub import AudioSegment
from speech_recognition import AudioFile, Recognizer

from fp_scraper.config import MP3_PATH, WAV_PATH
from fp_scraper.utils import delay_page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_for_captcha(page: Page):
    try:
        selector = page.locator("//iframe[@title='reCAPTCHA']").first
        # selector = await page.wait_for_selector(
        #     "iframe[src*='recaptcha'], div.g-recaptcha, div.h-captcha, iframe#cf-chl-widget",
        #     timeout=10000,
        # )
        if not selector:
            return False
        if await selector.is_visible():
            logger.info("Captcha detected")
            return True

    except Exception as e:
        logger.info(f"No captcha detected {e=}")
        return False


class SolveCaptcha:
    def __init__(self, page: Page):
        self.page = page
        self.main_frame = None
        self.recaptcha = None

    async def presetup(self):
        try:
            name = await self.page.locator(
                "//iframe[@title='reCAPTCHA']"
            ).first.get_attribute("name")
            self.recaptcha = self.page.frame(name=name)
            if self.recaptcha is None:
                raise ValueError("reCAPTCHA frame not found")

            await self.recaptcha.click("//div[@class='recaptcha-checkbox-border']")
            await delay_page(self.page)

            frame_name = await self.page.locator(
                "//iframe[contains(@src,'https://www.google.com/recaptcha/api2/bframe?')]"
            ).get_attribute("name")
            self.main_frame = self.page.frame(name=frame_name)
            if self.main_frame is None:
                raise ValueError("Main frame not found for reCAPTCHA")

            await self.main_frame.click("id=recaptcha-audio-button")

        except Exception as e:
            logger.error(f"Error during presetup: {e}")
            raise e

    async def start(self):
        try:
            await self.presetup()
            tries = 0
            while tries <= 5:
                await delay_page(self.page)
                try:
                    await self.solve_captcha()
                except Exception as e:
                    print(e)
                    if not self.main_frame:
                        raise e
                    await self.main_frame.click("id=recaptcha-reload-button")
                else:
                    if self.recaptcha is None:
                        raise ValueError("reCAPTCHA frame not initialized")
                    s = self.recaptcha.locator("//span[@id='recaptcha-anchor']")
                    checked = await s.get_attribute("aria-checked")
                    if checked is None:
                        raise ValueError("reCAPTCHA checkbox not found or not checked")
                    if checked != "false":
                        logger.info("Captcha solved successfully")
                        # await self.page.click("id=recaptcha-demo-submit")
                        await delay_page(self.page)
                        break
                tries += 1
        except Exception as e:
            logger.error(f"Error during captcha solving: {e}")
            raise e

    async def solve_captcha(self):
        logger.info("Solving reCAPTCHA audio challenge")
        recognizer = Recognizer()

        if self.main_frame is None:
            raise ValueError("Main frame not initialized for solving captcha")

        try:
            logger.info("Clicking audio challenge button")
            await self.main_frame.click(
                "//button[@aria-labelledby='audio-instructions rc-response-label']"
            )
            href = await self.main_frame.locator(
                "//a[@class='rc-audiochallenge-tdownload-link']"
            ).get_attribute("href")
            if href is None:
                raise ValueError("Audio challenge link not found")
            urlretrieve(href, MP3_PATH)
        except Exception as e:
            logger.error(f"Error during audio download: {e}")
            raise e

        try:
            logger.info("Processing audio file")
            AudioSegment.converter = "ffmpeg"
            AudioSegment.ffmpeg = "ffmpeg"
            AudioSegment.from_mp3(MP3_PATH).export(WAV_PATH, format="wav")
            recaptcha_audio = AudioFile(str(WAV_PATH))
            with recaptcha_audio as source:
                audio = recognizer.record(source)
        except Exception as e:
            logger.error(f"Error during audio processing: {e}")
            raise e

        try:
            logger.info("Recognizing audio...")
            text = recognizer.recognize_openai(audio)  # type: ignore
            print(text)
            if not text or not self.main_frame:
                raise ValueError("Failed to recognize audio")
            await self.main_frame.fill("id=audio-response", text)
            await self.main_frame.click("id=recaptcha-verify-button")
            await delay_page(self.page)
        except Exception as e:
            logger.error(f"Error during audio recognition: {e}")
            raise e

    def __del__(self):
        os.remove(MP3_PATH)
        os.remove(WAV_PATH)


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
