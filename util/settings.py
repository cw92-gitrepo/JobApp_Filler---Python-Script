"""Where the program keeps its files, and the remembered resume path.

PROGRAM_DIR is next to the .exe when bundled by PyInstaller (sys.frozen is
set), and next to main.py when run as a script. Saved data goes there rather
than next to this file, because a bundled app unpacks its code into a
temporary folder that is deleted on exit.
"""

import sys
from pathlib import Path

PROGRAM_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent
CONFIG_DIR = PROGRAM_DIR / "configs"  # personal answers; in .gitignore
LAST_RESUME_FILE = CONFIG_DIR / "last_resume.txt"


def last_resume() -> Path | None:
    """The resume used last time, or None if there isn't one or it was moved/deleted."""
    try:
        path = Path(LAST_RESUME_FILE.read_text(encoding="utf-8").strip())
    except OSError:  # first run: the file doesn't exist yet
        return None
    return path if path.is_file() else None


def remember_resume(path: Path) -> None:
    LAST_RESUME_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_RESUME_FILE.write_text(str(path.resolve()), encoding="utf-8")
