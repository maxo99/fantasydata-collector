# FantasyPros Rankings Pull

Testing functionality of some new python tools for collecting fantasy football data.

## Using

- [playwright-python](https://pypi.org/project/playwright/) - Browser automation
- [playwright-stealth](https://pypi.org/project/playwright-stealth/) - Preconfiguration of Browser detection avoidance techniques
- [pydub](https://pypi.org/project/pydub/) - To create AudioSegment .wav files from the reCAPTCHA audio stream .mp3 files.
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) - To recognize audio from the collected .wav reCAPTCHA audio files.

## Credits

- [Binit-Dhakal/Google-reCAPTCHA-v2-solver-using-playwright-python](https://github.com/Binit-Dhakal/Google-reCAPTCHA-v2-solver-using-playwright-python) - Good example of using audio challenges solving techniques.

## Install

### Requirements

- Tested on Python 3.13
One of:
  - AudioSolving:
    - ffmpeg - For audio processing
    - openai key
  - AntiCaptchaSolver: (will put this in place once audio solving is tested)
    - AntiCaptcha key

```bash
    uv venv
    uv sync
```

## Usage

### Normal Operation (without recording)

```bash
    uv run main.py
```

### With Session Recording (for development and testing)

This setup provides VCR.py-style functionality for your Playwright-based FantasyPros scraper, allowing you to record HTTP requests and responses for testing without hitting the live site repeatedly.

#### Record a session

```bash
    uv run main.py --record
```

#### Replay a session

```bash
    uv run main.py --replay
```

#### Test individual components

```bash
    uv run test_recorder.py
```
