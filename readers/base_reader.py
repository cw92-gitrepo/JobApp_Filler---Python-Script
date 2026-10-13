from abc import ABC, abstractmethod
from pathlib import Path
from data.resume import Resume
from util.errors import UnsupportedFileTypeError

class Reader(ABC):
     usr_personal = ()
     usr_general = ()
     usr_employment = list[Resume.Employment]
     usr_education = list[Resume.Education]

     @abstractmethod
     def __init__(self, this, file:str):
               path = Path(file)
               suffix = path.suffix

     def create_resume_employment(self, employment:list[str]):
          #TODO: Determine order of list so that employment data fields can be filled.
          #TODO: Append the new employment object to the employment history data member
          pass
          
     def create_resume_education(self, employment:list[str]):
          #TODO: Determine order of list so that education data fields can be filled.
          #TODO: Append the new education object to the education list data member
          pass
     
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