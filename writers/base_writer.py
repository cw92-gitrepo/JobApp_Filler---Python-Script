from detection.portal_detector import Portal_detector
from data.resume import Resume
from abc import ABC, abstractmethod


class Writer(ABC):

    @abstractmethod
    def write_from_resume(resume):
        pass

    def write_to_portal(self, usr_resume):  
        resume = Resume()

        #TODO: call portal_dectector method to determine what web portal the user is looking at (easiest would be checking url)
        
        self.read_from_file(portal_detector.run(),usr_resume)
        return None
