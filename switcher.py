from detection import portal_detector, file_detector
from models import valid_in_out

from typing import TypeAlias

usr_site: string = ""
usr_file: string = ""
sites = valid_in_out.sites
file_types = valid_in_out.files_types

site = portal_detector()
file = file_detector()

match  