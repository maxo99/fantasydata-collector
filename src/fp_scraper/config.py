import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

RUN_ID = datetime.now().strftime("%Y%m%d%H%M%S")

FP_EMAIL = os.getenv("FANTASYPROS_EMAIL")
FP_PASSWORD = os.getenv("FANTASYPROS_PASSWORD")
DOWNLOAD_DIR = Path("downloads" + os.sep + RUN_ID)
DOWNLOAD_DIR.mkdir(exist_ok=True)
MP3_PATH = DOWNLOAD_DIR / "audio.mp3"
WAV_PATH = DOWNLOAD_DIR / "audio.wav"
