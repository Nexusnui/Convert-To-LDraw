from stlToDat import stl_to_dat
from src.brick_data.brickcolour import is_brickcolour, Brickcolour, get_contrast_colour
import customtkinter
from tkinter import messagebox as tkMessageBox
import os

os.chdir(os.path.dirname(__file__))


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x240")
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
        self.colour_code_Var = customtkinter.StringVar()
        self.colour_toggle_Var = customtkinter.StringVar(value="off")

        self.colour_code_Var.trace("w", self.update_colour_preview)
        self.colour_toggle_Var.trace("w", self.update_colour_preview)

        customtkinter.CTkLabel(self.main_frame, text="Input File:").grid(sticky="w", columnspan=2, row=0, column=0)
        self.input_file_path_label = customtkinter.CTkEntry(self.main_frame, textvariable=self.input_file_Var)
        self.input_file_path_label.grid(sticky="we", columnspan=2, row=1, column=0)

        self.load_file_button = customtkinter.CTkButton(self.main_frame, text="Select Input File",
                                                        command=self.get_input_file)
        self.load_file_button.grid(sticky="ew", row=1, column=2)

        customtkinter.CTkLabel(self.main_frame, text="LDraw Colour Code:").grid(sticky="w", columnspan=2,
                                                                               row=2, column=0)
        self.colour_code_label = customtkinter.CTkEntry(self.main_frame, textvariable=self.colour_code_Var)
        self.colour_code_label.grid(sticky="ew", columnspan=2, row=3, column=0)
        self.colour_toggle_checkbox = customtkinter.CTkCheckBox(self.main_frame, text="Apply",
                                                                variable=self.colour_toggle_Var, onvalue="on",
                                                                offvalue="off")
        self.colour_toggle_checkbox.grid(sticky="ew", columnspan=2, row=3, column=2)

        customtkinter.CTkLabel(self.main_frame, text="Colour Preview:").grid(sticky="w", columnspan=1,
                                                                            row=4, column=0)
        self.colour_preview = customtkinter.CTkLabel(self.main_frame, text="Main_Colour", text_color="#00008F",
                                                     fg_color="#FFFF80", padx=3, corner_radius=6)
        self.colour_preview.grid(sticky="w", columnspan=2, row=4, column=1)

        customtkinter.CTkLabel(self.main_frame, text="Output File:").grid(sticky="w", columnspan=2, row=5, column=0)
        self.output_file_label = customtkinter.CTkEntry(self.main_frame, textvariable=self.output_file_Var)
        self.output_file_label.grid(sticky="ew", columnspan=2, row=6, column=0)

        self.output_file_button = customtkinter.CTkButton(self.main_frame, text="Select Output File",
                                                          command=self.set_output_file)
        self.output_file_button.grid(sticky="ew", row=6, column=2)

        self.convert_file_button = customtkinter.CTkButton(self.main_frame, text="convert file", command=self.convert_file)
        self.convert_file_button.grid(sticky="ew", row=7, column=1)

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

    def update_colour_preview(self, *args):
        set_colour = Brickcolour("16")
        if self.colour_toggle_Var.get() == "on":
            set_colour = Brickcolour(self.colour_code_Var.get())
        if set_colour is not None:
            if set_colour.colour_type == "LDraw" and set_colour.ldrawname is not None:
                text_colour = get_contrast_colour(set_colour.rgb_values)
                self.colour_preview.configure(text=set_colour.ldrawname, text_color=text_colour,
                                              fg_color=set_colour.rgb_values)
                return
            elif set_colour.colour_type == "Direct":
                self.colour_preview.configure(text=set_colour.rgb_values, text_color=set_colour.rgb_edge,
                                              fg_color=set_colour.rgb_values)
                return
            else:
                self.colour_preview.configure(text="Unknown or invalid colour", text_color="#FFFFFF",
                                              fg_color="#000000")
        elif len(self.colour_code_Var.get()) == 0:
            self.colour_preview.configure(text="", fg_color="transparent")
            return
        else:
            self.colour_preview.configure(text="Unknown or invalid colour", text_color="#FFFFFF", fg_color="#000000")

    def convert_file(self):
        input_file_path = self.input_file_Var.get()
        output_file_path = self.output_file_Var.get()
        colour_code = "16"
        if self.colour_toggle_Var.get() == "on":
            colour_code = self.colour_code_Var.get()
            colour_check = is_brickcolour(colour_code)
            if not colour_check[0]:
                tkMessageBox.showwarning(colour_check[1], colour_check[2])
                return

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

        number_triangles = stl_to_dat(input_file_path, output_file_path, colour_code)
        tkMessageBox.showwarning('Converted File', f'stl file converted to "{output_file_path}"\n'
                                                   f'Part contains {number_triangles} triangles.')


if __name__ == "__main__":
    app = App()
    app.mainloop()
