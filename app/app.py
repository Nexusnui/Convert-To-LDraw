from stlToDat import stlToDat
import customtkinter
from tkinter import messagebox as tkMessageBox
import os

os.chdir(os.path.dirname(__file__))

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x150")
        self.iconbitmap("../icons/stlToLDraw_icon.ico")
        self.title("stl to LDraw dat file")
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)

        self.input_file_Var = customtkinter.StringVar()
        self.output_file_Var = customtkinter.StringVar()

        customtkinter.CTkLabel(self.main_frame, text="Input File:").grid(sticky="w", columnspan=2, row=0, column=0)
        self.input_file_path_label = customtkinter.CTkEntry(self.main_frame, textvariable=self.input_file_Var)
        self.input_file_path_label.grid(sticky="we", columnspan=2, row=1, column=0)

        self.load_file_button = customtkinter.CTkButton(self.main_frame, text="Select Input File",
                                                        command=self.get_input_file)
        self.load_file_button.grid(sticky="ew", row=1, column=2)

        customtkinter.CTkLabel(self.main_frame, text="Output File:").grid(sticky="w", columnspan=2, row=2, column=0)
        self.output_file_label = customtkinter.CTkEntry(self.main_frame, textvariable=self.output_file_Var)
        self.output_file_label.grid(sticky="ew", columnspan=2, row=3, column=0)

        self.output_file_button = customtkinter.CTkButton(self.main_frame, text="Select Output File",
                                                        command=self.set_output_file)
        self.output_file_button.grid(sticky="ew", row=3, column=2)

        self.convertFileButton = customtkinter.CTkButton(self.main_frame, text="convert file", command=self.convertFile)
        self.convertFileButton.grid(sticky="ew", row=4, column=1)


    def get_input_file(self):
        input_file_path = customtkinter.filedialog.askopenfilename(filetypes=[('stl files', '*.stl')])

        if len(input_file_path) > 0:
            self.input_file_Var.set(input_file_path)

            if len(self.output_file_Var.get()) == 0:
                output_file_path = os.path.splitext(input_file_path)[0] + ".dat"
                self.output_file_Var.set(output_file_path)

    def set_output_file(self):
        input_file_path = self.input_file_Var.get()
        suggested_name = ""
        if len(os.path.basename(input_file_path)) > 0:
            suggested_name = os.path.basename(input_file_path).split(".")[0]

        output_file_path = customtkinter.filedialog.asksaveasfilename(confirmoverwrite=True, defaultextension="dat", initialfile=suggested_name,filetypes=[('dat files', '*.dat')])
        if len(output_file_path) > 0:
            self.output_file_Var.set(output_file_path)

    def convertFile(self):
        input_file_path = self.input_file_Var.get()
        output_file_path = self.output_file_Var.get()
        if not os.path.isfile(input_file_path):
            tkMessageBox.showwarning("invalid input file", f"'{input_file_path}' is not a valid input file")
            return
        elif len(os.path.basename(output_file_path)) == 0:
            tkMessageBox.showwarning("no outputfile", "There is no outputfile")
            return
        elif not os.path.isdir(os.path.dirname(output_file_path)):
            tkMessageBox.showwarning("invalid output directory", f"'{os.path.dirname(output_file_path)}' is not a valid output directory")
            return
        number_triangles = stlToDat(input_file_path, output_file_path)
        tkMessageBox.showwarning('Converted File', f'stl file converted to "{output_file_path}"\n'
                                                   f'Part contains {number_triangles} triangles.')

if __name__ == "__main__":
    app = App()
    app.mainloop()