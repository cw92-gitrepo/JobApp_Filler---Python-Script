import re


class Config:

    #Initializes a config hashmap from the config.txt file that hashes config to config setting
    def __init__(self):
        file = "config.txt"
        self.configs = {}
        with open(file, "r") as s:

            #Cleans the line read from the config.txt file if it's a config section header to be a a lowercase string
            regex = re.compile('[^a-zA-Z_]') 
            text = s.readline
            if not text[0] =='(':
                self.configs = {regex.sub('',text).lower()}
            self.configs[text] = s.readline

    #Returns config settings given the appropiate config name
    def get(self,config):
        return self.configs[config]

#Creates a singleton class on import
config = Config()