from detection import portal_detector, file_detector
from Configs import valid_in_out
from typing import TypeAlias

class switcher(usr_file_type, usr_portal):
    
    portals = valid_in_out.sites
    file_types = valid_in_out.files_types

    if usr_portal not in portals:
        raise Exception("Web Portal unsupported")
    if usr_file_type not in file_types:
        raise Exception("File extension unsupported")

    

    def call_reader(file):

        #TODO: implement reading logic
        pass

    def call_writer(portal):
        #TODO: implement writing logic
        pass