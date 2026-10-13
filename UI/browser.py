from playwright.sync_api import sync_playwright

class window:
    def __init__(self, url: str):
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                "browser_profile",
                channel="chrome",
                headless=False,
            )
            page = context.pages[0]
            page.goto(url)
            context.close()
        return self