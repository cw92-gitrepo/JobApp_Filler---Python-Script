from abc import ABC, abstractmethod
from pathlib import Path
from data.resume import Resume
from typing import Tuple
from dataclasses import fields
from util.errors import UnsupportedFileTypeError

class Reader(ABC):

     def __init__(self, file:str):
          path = Path(file)
          suffix = path.suffix

          self.usr_personal = None
          self.usr_general = None
          self.usr_employment: list[Resume.Employment] = []
          self.usr_education: list[Resume.Education] = []

     #TODO: in reader, make sure information is passed to tuple as correct data types : if passed in normally everything (should) be a string
     def create_resume_usr_info(self, personal:tuple, general:tuple):
          self.usr_personal = Resume.UserPersonal(*personal)
          self.usr_general = Resume.UserGeneral(*general)

     def create_resume_employment(self, employment:tuple):
               self.usr_employment.append(Resume.Employment(*employment))
          
     def create_resume_education(self, education:tuple):
               self.usr_education.append(Resume.Education(*education))
     
     @abstractmethod
     def read_from_file(self, path:Path) -> Resume:
          pass

     def file_check(self, path:Path):
         if not Path(path).is_file():
              raise UnsupportedFileTypeError(
                   """ Issue with file selected. """
                   """ Please double check that the filepath is to a valid file."""
              ) 
         
     

         


#TODO: add get_contents method