from dataclasses import dataclass, field
from datetime import date

#Data class that holds all relevant information in a resume for the writer to pull from. 
#Data is pulled up through the reader, passed to the formatter, then input here.

@dataclass
class Resume:

    @dataclass
    class UserPersonal:
        first : str | None = None
        last : str | None = None
        phone : str | None = None
        email : str | None = None
        streetadr : str | None = None
        country : str | None = None
        city : str | None = None
        state : str | None = None
        zipcode : str | None = None

    @dataclass
    class UserGeneral:

        skills : list[str] = field(default_factory=list)
        clearance : str | None = None
        certifications : list[str] = field(default_factory=list)
        projects : list[str] = field(default_factory=list)

    @dataclass
    class Employment:

        employer : str
        title : str
        location : str
        start_date : date
        end_date : date | None = None
        responsibilities : list[str] = field(default_factory=list)
        supervisor : str | None = None
        supervisor_contact : str | None = None

    @dataclass
    class Education:

        school : str
        degree : str
        major : str
        gpa : str
        ongoing : bool
        start_date : date
        end_date : date | None = None
        minor : str | None = None

    personal_info: UserPersonal = field(default_factory=UserPersonal)
    gen_info: UserGeneral = field(default_factory=UserGeneral)
    employment_history: list[Employment] = field(default_factory=list)
    education_history: list[Education] = field(default_factory=list)


