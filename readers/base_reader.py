from abc import ABC, abstractmethod


class Reader(ABC):

    @abstractmethod
    def read_from_file(file):
        pass


#TODO: add get_contents method