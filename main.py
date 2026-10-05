# main.py
import pathlib
from config import Processing_Config
from registry import Registry
from input_window import Input_window
from readers.base_reader import Reader
from writers.base_writer import Writer

readers = Registry(config.readers, Reader)
writers = Registry(config.writers, Writer)

#TODO: Implement portal detection logic

def portal_detector():
    pass

#TODO: Add comments. Got cutoff by work.
portal = portal_detector()

window = Input_window()
window.run
filepath = window.filepath

extension = pathlib.Path(filepath).suffix
reader = Registry.create(readers, extension)
reader.read_from_file(filepath)
resume_str = reader.resume_str

writer = Registry.create(writers, portal)
writer.make_resume_from_string(resume_string)
writer.write_to_portal()














input_window.run()

#TODO: Move these calls to the input_window widget that will be made later and have them get called after the user clicks a button
#Follow it up by then calling the readers/writers in the same post button sequence
####### This way data can be local and objects/processes only start after the user has provided valid imput similar to how a 
####### callback would work
reader = readers.create(usr_file)   
writer = writers.create(usr_portal)

