"""Controller: the launch window -> one application -> back to the launch window.

    wait_for_launch ──► attach to Chrome ──► find the portal tab ──► choose config
       ▲     │                                                           │
       │  "Change..." ─► file picker              last resume (or file picker if none)
       │                                                                 │
       │                       error popup ─► file picker ◄── fails ── read + write
       │                                                                 │ works
       └──────────────────── status: "Filled ..." ◄──────────────────────┘

main.py is the only module that imports both the GUI and the logic. The layers
below raise AppError subclasses; this file catches them and shows a popup.
"""

import tkinter as tk
import traceback
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright

from readers.resume_reader import read_resume, supported_extensions
from util import gui
from util.browser import attach, find_page, open_pages
from util.errors import AppError, ConfigError, PortalNotFoundError
from util.settings import PROGRAM_DIR, last_resume, remember_resume
from writers.portal_writer import (
    PortalConfig,
    config_fields,
    load_config,
    missing_fields,
    portal_for,
    save_config,
    saved_configs,
    supported_portals,
    write_resume,
)


def main() -> None:
    root = gui.create_root()
    status = ""
    first_run = True
    while True:
        action = gui.wait_for_launch(root, status, first_run, last_resume())
        if action is None:  # window closed
            break
        if action == gui.CHANGE_RESUME:
            pick_resume(root)
            continue  # back to the launch window, now showing the new file
        status = run_once(root)
        first_run = False
    root.destroy()


def run_once(root: tk.Tk) -> str:
    """Fill one application. Returns the status line for the next launch window."""
    try:
        # The with-block calls playwright.stop() on exit, even after an error.
        # Stopping only disconnects; it does not close the user's Chrome.
        with sync_playwright() as playwright:
            page = find_portal_page(attach(playwright))
            portal = portal_for(page.url) or ""
            config = choose_config(root, portal)
            if config is None:
                return "Cancelled."
            return fill_until_done(root, page, portal, config)
    except AppError as error:
        gui.show_error(root, error.title, error.message)
        return f"Last run stopped: {error.title}."
    except Exception as error:  # a bug, not a user problem: keep the app alive, keep the details
        traceback.print_exc()
        gui.show_error(
            root, "Unexpected error", f"{type(error).__name__}: {error}\n\nDetails are in the console."
        )
        return "Last run stopped: unexpected error."


def find_portal_page(browser: Browser) -> Page:
    page = find_page(browser, lambda url: portal_for(url) is not None)
    if page is None:
        open_urls = "\n".join(f"  {tab.url!r}" for tab in open_pages(browser))
        raise PortalNotFoundError(
            f"None of your open tabs is on a supported portal ({', '.join(supported_portals())}).\n\n"
            f"Open tabs:\n{open_urls}\n\n"
            "Open the application in Chrome first. If it's open but shows '' above, reload that tab."
        )
    return page


def fill_until_done(root: tk.Tk, page: Page, portal: str, config: PortalConfig) -> str:
    # Uses the last resume without asking. Only when there isn't one, or it
    # failed, does the file picker open; a bad file or a page hiccup goes back
    # to the picker so you can fix it and try again without reconnecting.
    path = last_resume()
    while True:
        if path is None:
            path = pick_resume(root)
            if path is None:
                return "Cancelled."
        try:
            write_resume(page, read_resume(path), config)
        except AppError as error:
            gui.show_error(root, error.title, error.message)
            path = None  # ask for a file next time round
            continue
        return f"Filled the {portal.title()} application from {path.name}. Review it before submitting."


def pick_resume(root: tk.Tk) -> Path | None:
    current = last_resume()
    start_dir = current.parent if current else PROGRAM_DIR
    path = gui.ask_resume_file(root, start_dir, supported_extensions())
    if path is not None:
        remember_resume(path)
    return path


def choose_config(root: tk.Tk, portal: str) -> PortalConfig | None:
    """The saved answers for this portal's extra questions. None if the user cancelled."""
    questions = config_fields(portal)
    if not questions:
        return {}  # this portal asks nothing beyond the resume

    saved = saved_configs(portal)
    names = [path.stem for path in saved]
    choice = gui.choose_config(root, portal, names) if names else gui.NEW_CONFIG
    if choice is None:
        return None
    if choice == gui.NEW_CONFIG:
        return create_config(root, portal, questions)

    config = load_config(saved[names.index(choice)])
    new_questions = missing_fields(portal, config)  # added to the writer since this was saved
    if new_questions:
        result = gui.ask_answers(root, f"New {portal.title()} questions", new_questions)
        if result is None:
            return None
        config |= result[1]
        save_config(portal, choice, config)
    return config


def create_config(root: tk.Tk, portal: str, questions: dict[str, str]) -> PortalConfig | None:
    answers: dict[str, str] = {}
    name = "default"
    while True:
        result = gui.ask_answers(root, f"New {portal.title()} config", questions, initial=answers, name=name)
        if result is None:
            return None
        name, answers = result[0] or "", result[1]
        try:
            save_config(portal, name, answers)
            return answers
        except ConfigError as error:  # bad name: say why, reopen the form with the answers kept
            gui.show_error(root, error.title, error.message)


if __name__ == "__main__":
    main()
