from config import config

##########REFRACTOR TO USE JSON. THIS IMPLIMENTATION IS BAD
class Prompts:

    #Initializes a prompt hashmap from the prompts file in config that hashes promptname to prompts
    def __init__(self):
        self.file = config.get("prompts_file")
        self.prompt = {}
        with open(self.file, "r") as f:
            key = f.readline
            self.prompt[key] = f.readline

    #Returns a prompt given a prompt_name
    def get(self, prompt_name):
        return self.prompt[prompt_name]
            
#Creates a singleton class on import
prompts = Prompts()
