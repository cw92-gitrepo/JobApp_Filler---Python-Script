"""Fills a job application page using the writer that matches its portal.

Dispatch: a tab on "acme.wd5.myworkdayjobs.com" contains "workday", so
writers/writer_workday.py's write() function fills it.

Adding a portal = adding writers/writer_<portal>.py with:
  write(page, resume, config)  fills the whole application, including
                               moving to the next page
  CONFIG_FIELDS                optional: {key: question} for answers the
                               portal asks for that aren't on a resume
where <portal> is a word in that portal's hostname. Nothing in this file changes.

Scope: major portal providers (Workday, Greenhouse), not company-specific
career sites.

Configs: the answers to a portal's CONFIG_FIELDS, saved once under a name
the user picks (configs/<portal>/<name>.json) and reused on later runs.
This file decides WHAT to ask and stores the answers; asking the user is
the GUI's job, so nothing here imports tkinter.
"""

import importlib
import json
import pkgutil
import re
from pathlib import Path
from types import ModuleType
from urllib.parse import urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

import writers
from resume import Resume
from util.errors import ConfigError, FillError, PluginError
from util.settings import CONFIG_DIR

PortalConfig = dict[str, str]  # {"source": "Indeed", "previously_worked_here": "No"}

CONFIG_NAME = re.compile(r"[\w -]+")  # letters, digits, _, space, -: safe as a file name


def portal_for(url: str) -> str | None:
    # Only the hostname is checked, so a search page whose URL merely
    # mentions "workday" in its query string doesn't count as a portal.
    hostname = urlparse(url).hostname or ""
    for portal in supported_portals():
        if portal in hostname:
            return portal
    return None


def write_resume(page: Page, resume: Resume, config: PortalConfig) -> None:
    portal = portal_for(page.url)
    writer = _writer_module(portal)
    try:
        writer.write(page, resume, config)
    except PlaywrightError as error:
        # Playwright errors carry a long call log; the first line says what failed:
        # "Locator.click: Timeout 30000ms exceeded."
        first_line = str(error).splitlines()[0]
        raise FillError(
            f"The {portal} page didn't respond the way the writer expected:\n{first_line}\n\n"
            "Check the page (and delete any half-filled entries), then try again."
        ) from None


def supported_portals() -> list[str]:
    # The writer files themselves are the list of supported portals:
    # writers/writer_workday.py -> ["workday"]
    return [
        module.name.removeprefix("writer_")
        for module in pkgutil.iter_modules(writers.__path__)
        if module.name.startswith("writer_")
    ]


# --- configs -------------------------------------------------------------------


def config_fields(portal: str) -> dict[str, str]:
    # A writer without CONFIG_FIELDS needs no extra answers.
    return getattr(_writer_module(portal), "CONFIG_FIELDS", {})


def missing_fields(portal: str, config: PortalConfig) -> dict[str, str]:
    # Questions the config hasn't answered yet: everything on a first run, or
    # only the new ones if the writer has added a question since the config was saved.
    return {key: question for key, question in config_fields(portal).items() if key not in config}


def saved_configs(portal: str) -> list[Path]:
    # Most recently used first, so the GUI can offer [0] as the default.
    # "Last used" is just the file's modified time; load_config() touches it.
    folder = CONFIG_DIR / portal
    return sorted(folder.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)


def load_config(path: Path) -> PortalConfig:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigError(f"Couldn't read the config {path.name}: {error}") from None
    path.touch()  # mark as most recently used
    return config


def save_config(portal: str, name: str, config: PortalConfig) -> Path:
    if not CONFIG_NAME.fullmatch(name):
        raise ConfigError(f"{name!r} can't be a config name. Use letters, numbers, spaces, - or _.")
    path = CONFIG_DIR / portal / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return path


# --- dispatch helpers ------------------------------------------------------------


def _writer_module(portal: str | None) -> ModuleType:
    module_name = f"writers.writer_{portal}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as error:
        # portal_for() only returns portals whose file exists, so a missing
        # module here means the writer's own import failed (see resume_reader).
        raise PluginError(f"{module_name} needs '{error.name}', which isn't installed.") from None
    if not callable(getattr(module, "write", None)):
        raise PluginError(f"{module_name} has no write(page, resume, config) function.")
    return module
