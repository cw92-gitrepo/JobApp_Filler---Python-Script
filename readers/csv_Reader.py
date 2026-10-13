import csv
from pathlib import Path
from base_reader import Reader

class Csv_reader(Reader):

    def read_from_file(self, path:Path):
        self.file_check(path)
        with path.open(newline="", encoding = "utf-8-sig") as f:
            reader = csv.reader(f)
            reader = csv.DictReader(f)
        #if the first cell in a row = x, call a function to assign to resume.x

        pass


    


    pass