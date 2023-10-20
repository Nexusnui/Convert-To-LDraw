from stlToDat import stlToDat
import customtkinter
from tkinter import messagebox as tkMessageBox
import os

os.chdir(os.path.dirname(__file__))

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x220")
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
        self.color_code_Var = customtkinter.StringVar()
        self.color_toggle_Var = customtkinter.StringVar(value="off")

        customtkinter.CTkLabel(self.main_frame, text="Input File:").grid(sticky="w", columnspan=2, row=0, column=0)
        self.input_file_path_label = customtkinter.CTkEntry(self.main_frame, textvariable=self.input_file_Var)
        self.input_file_path_label.grid(sticky="we", columnspan=2, row=1, column=0)

        self.load_file_button = customtkinter.CTkButton(self.main_frame, text="Select Input File",
                                                        command=self.get_input_file)
        self.load_file_button.grid(sticky="ew", row=1, column=2)

        customtkinter.CTkLabel(self.main_frame, text="LDraw Color Code:").grid(sticky="w", columnspan=2,
                                                                               row=2, column=0)
        self.color_code_label = customtkinter.CTkEntry(self.main_frame, textvariable=self.color_code_Var)
        self.color_code_label.grid(sticky="ew", columnspan=2, row=3, column=0)
        self.color_toggle_checkbox = customtkinter.CTkCheckBox(self.main_frame, text="Apply",
                                                               variable=self.color_toggle_Var, onvalue="on",
                                                               offvalue="off")
        self.color_toggle_checkbox.grid(sticky="ew", columnspan=2, row=3, column=2)

        customtkinter.CTkLabel(self.main_frame, text="Output File:").grid(sticky="w", columnspan=2, row=4, column=0)
        self.output_file_label = customtkinter.CTkEntry(self.main_frame, textvariable=self.output_file_Var)
        self.output_file_label.grid(sticky="ew", columnspan=2, row=5, column=0)

        self.output_file_button = customtkinter.CTkButton(self.main_frame, text="Select Output File",
                                                        command=self.set_output_file)
        self.output_file_button.grid(sticky="ew", row=5, column=2)

        self.convertFileButton = customtkinter.CTkButton(self.main_frame, text="convert file", command=self.convertFile)
        self.convertFileButton.grid(sticky="ew", row=6, column=1)


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

        output_file_path = customtkinter.filedialog.asksaveasfilename(confirmoverwrite=True, defaultextension="dat",
                                                                      initialfile=suggested_name,
                                                                      filetypes=[('dat files', '*.dat')])
        if len(output_file_path) > 0:
            self.output_file_Var.set(output_file_path)

    def convertFile(self):
        input_file_path = self.input_file_Var.get()
        output_file_path = self.output_file_Var.get()
        color_code = "16"
        if self.color_toggle_Var.get() == "on":
            color_code = self.color_code_Var.get()

        if not os.path.isfile(input_file_path):
            tkMessageBox.showwarning("invalid input file", f"'{input_file_path}' is not a valid input file")
            return
        elif len(os.path.basename(output_file_path)) == 0:
            tkMessageBox.showwarning("no outputfile", "There is no outputfile")
            return
        elif not os.path.isdir(os.path.dirname(output_file_path)):
            tkMessageBox.showwarning("invalid output directory",
                                     f"'{os.path.dirname(output_file_path)}' is not a valid output directory")
            return
        elif len(color_code) < 1:
            tkMessageBox.showwarning("No Color Code", "Apply Checkbox was toggled, but no color code provided")
            return
        elif not color_code.startswith("0x2"):
            if not color_code.isdigit():
                tkMessageBox.showwarning("Invalid Color Code",
                                         "The provided color code is not a number.\n "
                                         "Use a code from the LDraw Colour Definition Reference.\n"
                                         "If you wanted to use a Direct/HTML color the format is 0x2RRGGBB "
                                         "(R,B and G are hexadecimal).")
                return
        elif color_code.startswith("0x2"):
            if len(color_code) > 9:
                tkMessageBox.showwarning("Invalid Color Code",
                                         "The provided color seems to be a Direct/HTML color but is to long.")
                return
            elif len(color_code) < 9:
                tkMessageBox.showwarning("Invalid Color Code",
                                         "The provided color seems to be a Direct/HTML color but is to short.")
                return
            for i in range(2, 9):
                if color_code[i] not in ["A", "B", "C", "D", "E", "F"] and not color_code[i].isdigit():
                    tkMessageBox.showwarning("Invalid Color Code",
                                             f"The provided color seems to be a Direct/HTML color, but contains a invalid charcter at position: {i-1} - '{color_code[i]}'.\n"
                                             f"Valid characters are 0-9 and A-F(uppercase)")
                    return
        number_triangles = stlToDat(input_file_path, output_file_path, color_code)
        tkMessageBox.showwarning('Converted File', f'stl file converted to "{output_file_path}"\n'
                                                   f'Part contains {number_triangles} triangles.')

if __name__ == "__main__":
    app = App()
    app.mainloop()