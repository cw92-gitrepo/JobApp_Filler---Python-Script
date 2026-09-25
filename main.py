# main.py
from config import Processing_Config
from registry import Registry
from input_window import Input_window
from readers.base_reader import Reader
from writers.base_writer import Writer

config = Processing_Config.from_file("config.json")
input_window = Input_window()

readers = Registry(config.readers, Reader)
writers = Registry(config.writers, Writer)

input_window.run()

#TODO: Move these calls to the input_window widget that will be made later and have them get called after the user clicks a button
#Follow it up by then calling the readers/writers in the same post button sequence
####### This way data can be local and objects/processes only start after the user has provided valid imput similar to how a 
####### callback would work
reader = readers.create(usr_file)   
writer = writers.create(usr_portal)

