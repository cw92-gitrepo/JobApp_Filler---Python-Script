from ui import user_prompt
import switcher


#call user_prompt()
##gets user's file path
##gets user's web portal

#call switcher(file path, portal)
##determines what reader to call then calls and passes (file path) to it
##determines what writer to call using portal_detector() then passes (resume) to it
usr_portal = portal_detector()
usr_file_type = file_detector()

switcher.call_reader(usr_file_type)
switcher.call_writer(usr_portal)
