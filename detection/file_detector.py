from prompts import prompt
import traceback

class file_detector:

    def __init__(self):
        self.types = {}

    def get_types(self,file):
        types = {}
        try: 
            with open(file, "r") as s:
                pair = s.readline.split()
                types[pair[0]] = [pair[1]]
            self.types = types
        except:
             prompt.invalidfile("get_typess")
    
    def detect_type(self, file):
        try:
            extension = file.split('.')[-1]
            return self.types[extension]
        except:
            prompt.invalid()