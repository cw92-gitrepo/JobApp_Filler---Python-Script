"""Error types shared by every part of the program."""


class ResumeAppError(Exception):
    """Base class for expected, user-facing problems."""
    title = "Something went wrong"


class ResumeFormatError(ResumeAppError):
    """The resume file exists but its contents can't be used."""
    title = "Problem with resume file"


class UnsupportedFileTypeError(ResumeAppError):
    """No reader is registered for the chosen file type."""
    title = "Unsupported file type"


class BrowserConnectionError(ResumeAppError):
    """Chrome isn't running with remote debugging, or the connection failed."""
    title = "Can't reach Chrome"


class UnsupportedPortalError(ResumeAppError):
    """No open tab is on a supported job portal."""
    title = "No supported portal found"