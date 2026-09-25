from prompts import prompt

class file_detector:

    def __init__(self):
        file = "filetypes.txt"
        self.types = {}
        with open(file, "r") as s:
            key = s.readline.split()
            self.types[key] = s.readline

    def get_types(self,file):
        self.types = {}
        try: 
            
        except:
             prompt.get("err_filetype")
    
    def detect_type(self, file):
        try:
            extension = file.split('.')[-1]
            return self.types[extension]
        except:
            prompt.get("err_filetype")