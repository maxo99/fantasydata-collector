# FantasyPros Rankings Pull

Testing functionality of pywright-python for collecting fantasy football data.

## Install

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
