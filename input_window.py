
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog


class Input_window():
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.label = tk.Label(self.window, text ="Job App Filling Assistant")
        self.button_dir = tk.Button(text = "Select", command = openFile)
        self.button_submit = tk.Button(text = "Submit", )
        self.resume_path = tk.Entry(self.window, fg="black", bg = "blue", width = 50)
        self.label.pack()

    def openFile(self, filetypes):
        self.supported_files = [[]]
        for filetype in filetypes:
            str(filetype)
            self.supported_files.append([filetype][filetype])

        self.dir = filedialog.askopenfilename(filetypes=self.supported_files)


    def warning(self, warning_title, warning_text):
        self.validation_warning = messagebox.showwarning(title = warning_title, message= warning_text)
        

    def run(self):
        self.window.mainloop()

#TODO: determine what tecnologies to use in order to create a user prompt window