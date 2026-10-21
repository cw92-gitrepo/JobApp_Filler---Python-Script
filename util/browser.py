"""Attach to the user's own Chrome and find a tab. No UI and no portal logic."""

from collections.abc import Callable

from playwright.sync_api import Browser, Page, Playwright
from playwright.sync_api import Error as PlaywrightError

from util.errors import BrowserNotFoundError

CDP_URL = "http://localhost:9222"
CONNECT_TIMEOUT_MS = 5_000


def attach(playwright: Playwright) -> Browser:
    # Connects to a Chrome the user already started with --remote-debugging-port.
    # Playwright does not launch or own this browser.
    try:
        return playwright.chromium.connect_over_cdp(CDP_URL, timeout=CONNECT_TIMEOUT_MS)
    except PlaywrightError:
        raise BrowserNotFoundError(
            f"Couldn't connect to Chrome at {CDP_URL}.\n\n"
            "Close every Chrome window, then start Chrome with:\n"
            '  chrome.exe --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\\chrome-profile"\n\n'
            f"You can check it worked by opening {CDP_URL}/json/version."
        ) from None


def open_pages(browser: Browser) -> list[Page]:
    # contexts[0] is Chrome's default context: the window the user is logged into.
    return browser.contexts[0].pages


def find_page(browser: Browser, is_wanted: Callable[[str], bool]) -> Page | None:
    # The caller decides what "wanted" means (here: "is a known portal"), so
    # util/ never has to import writers/.
    for page in open_pages(browser):
        if is_wanted(page.url):
            return page
    return None
