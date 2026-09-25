from data.resume import Resume
from abc import ABC, abstractmethod


class Reader(ABC):

    @abstractmethod
    def read_from_file(file):
        pass

    def get_file_data(self, file):  
        resume = Resume()
        resume = self.read_from_file()
        return (resume)
