FP_RANKINGS_PAGE = "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php"

CAPTCHA_IDENTIFIERS = [
    # reCAPTCHA v2
    "//iframe[contains(@src, 'recaptcha')]",
    "//div[contains(@class, 'g-recaptcha')]",
    "//div[@data-sitekey]",
    # reCAPTCHA v3
    "//script[contains(@src, 'recaptcha')]",
    # hCaptcha
    "//iframe[contains(@src, 'hcaptcha')]",
    "//div[contains(@class, 'h-captcha')]",
    # Text indicators
    "//div[contains(text(), 'captcha')]",
    "//div[contains(text(), 'CAPTCHA')]",
    "//*[contains(text(), 'Verify you are human')]",
    # Cloudflare CAPTCHA
    "//iframe[@id='cf-chl-widget']",
    "//*[contains(text(), 'Cloudflare')]",
]

BROWSER_ARGS = [
    # "--deny-permission-prompts",
    # "--no-default-browser-check",
    # "--no-first-run",
    # "--deny-permission-prompts",
    # "--disable-popup-blocking",
    # "--ignore-certificate-errors",
    # "--no-service-autorun",
    # "--password-store=basic",
    # "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)
    #  AppleWebKit/537.36 (KHTML, like Gecko)
    # Chrome/90.0.4430.212 Safari/537.36",
    # "--window-size=640,480",
    "--start-maximized",
    # "--disable-audio-output",
]
