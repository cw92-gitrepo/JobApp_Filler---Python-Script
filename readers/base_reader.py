from abc import ABC, abstractmethod
from pathlib import Path
from data.resume import Resume
from typing import Tuple
from dataclasses import fields
from util.errors import UnsupportedFileTypeError
from datetime import date, datetime

class Reader(ABC):

     DATE_FIELDS = {"start_date", "end_date"}
     LIST_FIELDS = {"skills", "certifications", "projects", "responsibilities"}
     DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%m/%Y", "%b %Y", "%B %Y")

     def read_from_file(self, path: str | Path) -> Resume:
        path = Path(path)
        self._file_check(path)
        self._reset()
        self._parse(path)        # the child fills the parts via make_*
        return Resume(           # NOTE: the assembly step that was missing
            personal_info=self.usr_personal,
            gen_info=self.usr_general,
            employment_history=self.usr_employment,
            education_history=self.usr_education,
        )
  
     @abstractmethod
     def _parse(self, path: Path) -> None:


     #TODO: in reader, make sure information is passed to tuple as correct data types : if passed in normally everything (should) be a string
     def make_usr_personal(self, personal: dict) -> None:
        self.usr_personal = self._build(Resume.UserPersonal, personal, "Personal")
 
     def make_usr_general(self, general: dict) -> None:
        self.usr_general = self._build(Resume.UserGeneral, general, "General")
 
     def make_employment(self, employment: dict) -> None:
        self.usr_employment.append(self._build(Resume.Employment, employment, "Employment"))
 
     def make_education(self, education: dict) -> None:
        self.usr_education.append(self._build(Resume.Education, education, "Education"))


     def file_check(self, path:Path) -> None:
         if not Path(path).is_file():
              raise ResumeFormatError(
                   """ Issue with file selected. """
                   """ Please double check that the filepath is to a valid file."""
              ) 

     def _date_validation(self, date: str):
         