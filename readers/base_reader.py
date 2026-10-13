from abc import ABC, abstractmethod
from pathlib import Path
from util.errors import UnsupportedFileTypeError

class Reader(ABC):

    @abstractmethod
    def __init__(self, this, file:str):
            path = Path(file)
            suffix = path.suffix

    @abstractmethod
    def read_from_file(self, path:Path):
        pass

    def file_check(self, path:Path):
         if not Path(path).is_file():
              raise UnsupportedFileTypeError(
                   """ Issue with file selected. """
                   """ Please double check that the filepath is to a valid file."""
              ) 


#TODO: add get_contents method