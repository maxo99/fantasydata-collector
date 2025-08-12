import asyncio
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

try:
    from test_recorder import RequestRecorder
except ImportError:
    RequestRecorder = None


async def login(page):
    email = os.getenv("FANTASYPROS_EMAIL")
    password = os.getenv("FANTASYPROS_PASSWORD")

    if not email or not password:
        raise ValueError(
            "FANTASYPROS_EMAIL and FANTASYPROS_PASSWORD must be set in .env file"
        )

    await page.click("text=Get Started")
    await page.fill('input[id="username"]', email)
    await page.fill('input[id="password"]', password)
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")


async def get_dropdown_options(page):
    dropdown_button = page.locator('//*[@id="select-advanced-2136961"]/div/button')
    await dropdown_button.click()

    options = await page.locator('//*[@id="select-advanced-2136961"]//li').all()
    option_texts = []
    for option in options:
        text = await option.text_content()
        option_texts.append(text.strip())

    await dropdown_button.click()
    return option_texts


async def download_csv_for_option(page, option_text, download_dir):
    dropdown_button = page.locator('//*[@id="select-advanced-2136961"]/div/button')
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
    await download.save_as(download_dir / filename)
    return filename


def merge_csvs(download_dir):
    csv_files = list(download_dir.glob("*.csv"))
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

    output_file = download_dir / "merged_rankings.csv"
    merged_df.to_csv(output_file, index=False)
    print(f"Merged data saved to: {output_file}")


async def main():
    import sys
    
    record_mode = "--record" in sys.argv
    replay_mode = "--replay" in sys.argv
    
    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)

    recorder = None
    if RequestRecorder and (record_mode or replay_mode):
        recorder = RequestRecorder()
        mode = "record" if record_mode else "replay"
        recorder.set_cassette("fantasypros_session", mode=mode)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        if recorder:
            recorder.setup_recording(page)

        try:
            await page.goto("https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php")

            await login(page)
            await page.goto("https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php")

            options = await get_dropdown_options(page)
            print(f"Found {len(options)} options: {options}")

            for option in options:
                print(f"Downloading CSV for: {option}")
                try:
                    filename = await download_csv_for_option(page, option, download_dir)
                    print(f"Downloaded: {filename}")
                except Exception as e:
                    print(f"Error downloading {option}: {e}")

        except Exception as e:
            print(f"Error during scraping: {e}")
        
        finally:
            if recorder and record_mode:
                recorder.save_cassette()
            await browser.close()

    merge_csvs(download_dir)


if __name__ == "__main__":
    asyncio.run(main())
