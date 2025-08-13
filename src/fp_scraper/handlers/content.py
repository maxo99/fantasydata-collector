import logging

import pandas as pd

from fp_scraper.config import DOWNLOAD_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def merge_csvs():
    try:
        logger.info("Merging CSV files")

        csv_files = list(DOWNLOAD_DIR.glob("*.csv"))
        if not csv_files:
            logger.error("No CSV files found to merge")
            return

        all_dataframes = []
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            df["Source"] = csv_file.stem
            all_dataframes.append(df)

        merged_df = pd.concat(all_dataframes, ignore_index=True)

        duplicates = merged_df[merged_df.duplicated(subset=["Player Name"], keep=False)]
        if not duplicates.empty:
            logger.warning(f"Found {len(duplicates)} duplicate player entries:")
            logger.warning(duplicates[["Player Name", "Source"]].to_string(index=False))

        output_file = DOWNLOAD_DIR / "merged_rankings.csv"
        merged_df.to_csv(output_file, index=False)
        logger.info(f"Merged data saved to: {output_file}")
    except Exception as e:
        logger.error(f"Error occurred while merging CSV files: {e}")
        raise e
