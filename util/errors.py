"""The app's own exceptions.

Lower layers (readers, writers, browser) raise these; main.py catches AppError
and the GUI shows `title` and the message in a popup. Nothing here imports the
GUI or the logic, so both can import it.

    AppError
    ├── BrowserNotFoundError   Chrome isn't reachable on the debugging port
    ├── PortalNotFoundError    no open tab is on a supported portal
    ├── UnsupportedFileError   no reader for this file extension
    ├── ResumeDataError        the file opened, but a value is missing or wrong
    ├── ConfigError            a saved portal config can't be used
    ├── FillError              the portal page didn't behave as the writer expected
    └── PluginError            a reader/writer module exists but is broken
"""


class AppError(Exception):
    title = "Something went wrong"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class BrowserNotFoundError(AppError):
    title = "Chrome not reachable"


class PortalNotFoundError(AppError):
    title = "No job application tab"


class UnsupportedFileError(AppError):
    title = "Unsupported file type"


class ResumeDataError(AppError):
    title = "Problem in the resume file"


class ConfigError(AppError):
    title = "Problem with the saved config"


class FillError(AppError):
    title = "Couldn't fill the application"


class PluginError(AppError):
    title = "Broken reader or writer"
