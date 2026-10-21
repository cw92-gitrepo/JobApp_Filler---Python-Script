"""Resume data model: what a reader produces and a writer consumes."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class UserPersonal:
    # All optional: a form may not need every value, and a sheet may leave cells blank.
    first: str | None = None
    last: str | None = None
    phone: str | None = None  # strings, not ints: keep leading zeros, "+1", dashes
    email: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    linkedin: str | None = None  # full URL, e.g. "https://www.linkedin.com/in/ada"


@dataclass
class UserGeneral:
    # default_factory, not `= []`: a plain default would be ONE list shared by
    # every UserGeneral ever created.
    skills: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    websites: list[str] = field(default_factory=list)  # portfolio, GitHub, ...
    clearance: str | None = None


@dataclass
class Employment:
    employer: str
    title: str
    location: str
    start_date: date
    end_date: date | None = None  # None means "current job"
    responsibilities: list[str] = field(default_factory=list)
    supervisor: str | None = None
    supervisor_contact: str | None = None

    @property
    def is_current(self) -> bool:
        return self.end_date is None


@dataclass
class Education:
    school: str
    degree: str
    major: str
    start_date: date
    end_date: date | None = None  # None means "ongoing"
    gpa: str | None = None  # text, so "3.80" stays "3.80"
    minor: str | None = None

    @property
    def is_ongoing(self) -> bool:
        return self.end_date is None


@dataclass
class Resume:
    personal: UserPersonal = field(default_factory=UserPersonal)
    general: UserGeneral = field(default_factory=UserGeneral)
    employment: list[Employment] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
