"""Every tkinter window the app shows. Knows nothing about readers, writers or Playwright.

There is one Tk root for the whole program, and it stays hidden. Each window
below is a modal Toplevel or a standard dialog on top of it, and each function
blocks until the user answers, then returns plain Python values. So main.py
reads top to bottom, and Tk's event loop only runs while a window is waiting
for an answer, never at the same time as Playwright.
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

NEW_CONFIG = "<new>"  # returned by choose_config(); "<" can't appear in a real config name
LAUNCH, CHANGE_RESUME = "launch", "change resume"  # what wait_for_launch() returns
PADDING = 12
CORNER_OFFSET = 200  # px from the right and bottom screen edges after the first run


def create_root() -> tk.Tk:
    root = tk.Tk()
    root.withdraw()  # hidden for the whole run; windows are Toplevels on top of it
    # Keep dialogs above Chrome, which is usually the active window.
    root.attributes("-topmost", True)
    return root


def wait_for_launch(
    root: tk.Tk, status: str = "", first_run: bool = True, resume: Path | None = None
) -> str | None:
    """Show the launch window. Returns LAUNCH, CHANGE_RESUME, or None if it was closed.

    The first time it opens in the middle of the screen; after a run it sits
    near the bottom-right corner, out of the way of the application page.
    """
    window = _modal_window(root, "Job App Script")
    action: str | None = None

    def finish(value: str) -> None:
        nonlocal action  # assign to the variable above, not a new local one
        action = value
        window.destroy()

    if status:
        ttk.Label(window, text=status, wraplength=320).pack(padx=PADDING, pady=(PADDING, 0))

    resume_row = ttk.Frame(window)
    resume_row.pack(fill="x", padx=PADDING, pady=(PADDING, 0))
    resume_text = f"Resume: {resume.name}" if resume else "Resume: Select to continue"
    ttk.Label(resume_row, text=resume_text).pack(side="left")
    change = ttk.Button(resume_row, text="Change...", command=lambda: finish(CHANGE_RESUME))
    change.pack(side="right", padx=(12, 0))

    launch = ttk.Button(window, text="Launch script", command=lambda: finish(LAUNCH))
    launch.pack(padx=PADDING, pady=PADDING, ipadx=24, ipady=6)
    if resume:
        launch.focus_set()
        window.bind("<Return>", lambda _event: finish(LAUNCH))
    else:
        # No resume yet: Launch is grayed out and can't be clicked; Change... gets the focus.
        launch.state(["disabled"])
        change.focus_set()
        window.bind("<Return>", lambda _event: finish(CHANGE_RESUME))
    _place(window, centered=first_run)
    window.wait_window()  # runs Tk's event loop until the window is destroyed
    return action


def ask_resume_file(root: tk.Tk, initial_dir: Path, extensions: list[str]) -> Path | None:
    """File picker filtered to supported types. None if cancelled."""
    patterns = " ".join(f"*.{extension}" for extension in extensions)  # "*.xlsx *.csv"
    chosen = filedialog.askopenfilename(
        parent=root,
        title="Choose your resume file",
        initialdir=initial_dir,
        filetypes=[("Resume files", patterns), ("All files", "*.*")],
    )
    return Path(chosen) if chosen else None  # askopenfilename returns "" on cancel


def choose_config(root: tk.Tk, portal: str, names: list[str]) -> str | None:
    """Pick a saved config (first name is the default) or NEW_CONFIG. None if closed."""
    window = _modal_window(root, f"{portal.title()} config")
    choice: str | None = None

    def finish(value: str) -> None:
        nonlocal choice
        choice = value
        window.destroy()

    ttk.Label(window, text=f"Saved answers for {portal.title()} applications:").grid(
        row=0, column=0, columnspan=2, sticky="w", padx=PADDING, pady=(PADDING, 4)
    )
    selected = tk.StringVar(value=names[0])
    ttk.Combobox(window, textvariable=selected, values=names, state="readonly", width=30).grid(
        row=1, column=0, columnspan=2, sticky="we", padx=PADDING
    )
    ttk.Button(window, text="Use this one", command=lambda: finish(selected.get())).grid(
        row=2, column=0, sticky="we", padx=(PADDING, 4), pady=PADDING
    )
    ttk.Button(window, text="Make a new one", command=lambda: finish(NEW_CONFIG)).grid(
        row=2, column=1, sticky="we", padx=(4, PADDING), pady=PADDING
    )
    window.bind("<Return>", lambda _event: finish(selected.get()))
    _place(window, centered=True)
    window.wait_window()
    return choice


def ask_answers(
    root: tk.Tk,
    title: str,
    questions: dict[str, str],
    initial: dict[str, str] | None = None,
    name: str | None = None,
) -> tuple[str | None, dict[str, str]] | None:
    """A form with one text box per question, plus a "Config name" box if `name` is given.

    Returns (name, {key: answer}), or None if cancelled.
      questions = {"source": "How did you hear about us?"}
      -> ("default", {"source": "Indeed"})
    """
    initial = initial or {}
    window = _modal_window(root, title)
    result: tuple[str | None, dict[str, str]] | None = None

    # One StringVar per question, keyed like `questions`, so answers come back by key.
    answers = {key: tk.StringVar(value=initial.get(key, "")) for key in questions}
    name_var = tk.StringVar(value=name or "")

    row = 0
    for key, question in questions.items():
        ttk.Label(window, text=question, wraplength=420).grid(
            row=row, column=0, sticky="w", padx=PADDING, pady=(PADDING if row == 0 else 6, 0)
        )
        ttk.Entry(window, textvariable=answers[key], width=60).grid(row=row + 1, column=0, padx=PADDING)
        row += 2
    if name is not None:
        ttk.Label(window, text="Config name:").grid(row=row, column=0, sticky="w", padx=PADDING, pady=(10, 0))
        ttk.Entry(window, textvariable=name_var, width=30).grid(
            row=row + 1, column=0, sticky="w", padx=PADDING
        )
        row += 2

    def save() -> None:
        nonlocal result
        result = (
            name_var.get().strip() if name is not None else None,
            {key: var.get().strip() for key, var in answers.items()},
        )
        window.destroy()

    buttons = ttk.Frame(window)
    buttons.grid(row=row, column=0, sticky="e", padx=PADDING, pady=PADDING)
    ttk.Button(buttons, text="Cancel", command=window.destroy).pack(side="right")
    ttk.Button(buttons, text="Save", command=save).pack(side="right", padx=(0, 6))
    window.bind("<Return>", lambda _event: save())
    _place(window, centered=True)
    window.wait_window()
    return result


def show_error(root: tk.Tk, title: str, message: str) -> None:
    messagebox.showerror(title, message, parent=root)


def _place(window: tk.Toplevel, centered: bool) -> None:
    # Ask Tk to lay out the widgets first, so the window knows its real size.
    window.update_idletasks()
    width, height = window.winfo_reqwidth(), window.winfo_reqheight()
    screen_width, screen_height = window.winfo_screenwidth(), window.winfo_screenheight()
    if centered:
        x, y = (screen_width - width) // 2, (screen_height - height) // 2
    else:
        # e.g. 1920x1080 screen, 300x120 window -> x = 1420, y = 760
        x = screen_width - width - CORNER_OFFSET
        y = screen_height - height - CORNER_OFFSET
    window.geometry(f"+{max(x, 0)}+{max(y, 0)}")  # "+x+y" moves without resizing


def _modal_window(root: tk.Tk, title: str) -> tk.Toplevel:
    window = tk.Toplevel(root)
    window.title(title)
    window.resizable(False, False)
    window.attributes("-topmost", True)
    window.grab_set()  # modal: clicks go only to this window until it closes
    window.focus_force()
    return window
