import os
import platform

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QFrame,
    QCheckBox,
    QFileDialog,
    QMessageBox,
)

from brick_data.brickcolour import Brickcolour
from brick_data.ldrawObject import LdrawObject
from brickcolourwidget import BrickcolourWidget

basedir = os.path.dirname(__file__)

if platform.system() == "Windows":
    try:
        from ctypes import windll  # Only exists on Windows.

        myappid = "nexusnui.converttoldraw.1.1.0"
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ldraw_object = None
        self.file_loaded = False

        self.setWindowTitle("Convert To LDraw")
        self.main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        # File Selection Area:
        file_select_area = QVBoxLayout()
        file_select_label = QLabel("File Selection")
        file_select_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        file_select_area.addWidget(file_select_label)

        file_select_inputs = QVBoxLayout()
        file_select_frame = QFrame()
        file_select_frame.setFrameStyle(1)
        file_select_frame.setLayout(file_select_inputs)
        file_select_area.addWidget(file_select_frame)

        input_label = QLabel("Input File")
        input_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        file_select_inputs.addWidget(input_label)
        input_layout = QHBoxLayout()

        self.input_file_line = QLineEdit()
        self.input_file_line.setPlaceholderText("Select file to load")
        self.input_file_line.setReadOnly(True)
        input_layout.addWidget(self.input_file_line)

        load_input_button = QPushButton("Load File")
        input_layout.addWidget(load_input_button)
        load_input_button.clicked.connect(self.load_file)

        file_select_inputs.addLayout(input_layout)

        output_label = QLabel("Output File")
        output_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        file_select_inputs.addWidget(output_label)
        output_layout = QHBoxLayout()

        self.output_file_line = QLineEdit()
        self.output_file_line.setReadOnly(True)
        self.output_file_line.setPlaceholderText("Select output file")
        output_layout.addWidget(self.output_file_line)

        self.select_output_button = QPushButton("Select")
        self.select_output_button.setDisabled(True)
        output_layout.addWidget(self.select_output_button)
        self.select_output_button.clicked.connect(self.select_output_file)

        file_select_inputs.addLayout(output_layout)

        convert_button = QPushButton("Convert File")
        file_select_area.addWidget(convert_button)
        convert_button.clicked.connect(self.convert_file)

        # Part settings area:
        part_settings_area = QVBoxLayout()
        part_settings_label = QLabel("Part Settings")
        part_settings_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        part_settings_area.addWidget(part_settings_label)

        part_settings_inputs = QVBoxLayout()
        part_settings_frame = QFrame()
        part_settings_frame.setFrameStyle(1)
        part_settings_frame.setLayout(part_settings_inputs)
        part_settings_area.addWidget(part_settings_frame)

        partname_layout = QHBoxLayout()
        partname_layout.addWidget(QLabel("Part Name"))
        self.partname_line = QLineEdit()
        self.partname_line.setPlaceholderText("UntitledModel")
        partname_layout.addWidget(self.partname_line)
        part_settings_inputs.addLayout(partname_layout)

        bl_number_layout = QHBoxLayout()
        bl_number_layout.addWidget(QLabel("BL Number(Optional)"))
        self.bl_number_line = QLineEdit()
        self.bl_number_line.setPlaceholderText("Bricklinknumber")
        bl_number_layout.addWidget(self.bl_number_line)
        part_settings_inputs.addLayout(bl_number_layout)

        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("Author (Optional)"))
        self.author_line = QLineEdit()
        self.author_line.setPlaceholderText("Your Name/Alias")
        author_layout.addWidget(self.author_line)
        part_settings_inputs.addLayout(author_layout)

        apply_color_layout = QHBoxLayout()
        apply_color_layout.addWidget(QLabel("Apply Custom Color"))
        self.apply_color_check = QCheckBox()
        self.apply_color_check.setDisabled(True)
        apply_color_layout.addWidget(self.apply_color_check)
        apply_color_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        part_settings_inputs.addLayout(apply_color_layout)

        self.custom_color_input = BrickcolourWidget("Custom Color")
        self.custom_color_input.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.custom_color_input.setDisabled(True)
        self.custom_color_input.colour_changed.connect(self.update_custom_colour)
        part_settings_inputs.addWidget(self.custom_color_input)
        self.apply_color_check.stateChanged.connect(self.disable_custom_colour)

        # Preview Area
        preview_area = QHBoxLayout()

        self.preview_button = QPushButton("Show Preview")
        self.preview_button.clicked.connect(self.show_preview)
        self.preview_button.setDisabled(True)
        preview_area.addWidget(self.preview_button)

        self.loaded_file_status_label = QLabel("No File loaded")
        preview_area.addWidget(self.loaded_file_status_label)

        # Add Elements to Main Layout
        top_layout.addLayout(part_settings_area)
        top_layout.addLayout(file_select_area)
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(preview_area)
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def load_file(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("3D File (*.stl  *.3mf *.obj *.off *.ply *.gltf *.glb *.xaml *.stp *.step *.dae);;"
                             "Unknown Compatibility (*.brep *.igs *.iges *.bdf *.msh *.inp *.diff *.mesh);;"
                             "Any File (*.*)")
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        self.output_file_line.setReadOnly(True)
        self.select_output_button.setDisabled(True)
        self.apply_color_check.setDisabled(True)
        self.preview_button.setDisabled(True)
        self.reset_part_settings()
        self.loaded_file_status_label.setText(f"Loading File")

        if dialog.exec():
            filepath = dialog.selectedFiles()[0]
            if filepath:
                filename = os.path.basename(filepath)
                try:
                    loaded_part = LdrawObject(filepath)
                except Exception:
                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("Failed to load file")
                    dlg.setText("File was not a 3D object or the format is unsupported")
                    dlg.setIcon(QMessageBox.Icon.Critical)
                    dlg.exec()
                    self.loaded_file_status_label.setText(f"Failed to Load: {filename}")
                else:
                    self.ldraw_object = loaded_part
                    self.input_file_line.setText(filepath)
                    name = ".".join(filename.split(".")[:-1])
                    filedir = os.path.dirname(filepath)
                    self.partname_line.setText(name)
                    self.output_file_line.setText(f"{filedir}/{name}.dat")

                    self.output_file_line.setReadOnly(False)
                    self.select_output_button.setDisabled(False)
                    self.apply_color_check.setDisabled(False)
                    self.preview_button.setDisabled(False)
                    x_length = mm_float_to_string(self.ldraw_object.size[0])
                    y_length = mm_float_to_string(self.ldraw_object.size[1])
                    z_length = mm_float_to_string(self.ldraw_object.size[2])
                    self.loaded_file_status_label.setText(f"Current Model: {filename} ({x_length}×{y_length}×{z_length})")

                    if not self.file_loaded:
                        self.file_loaded = True
                    elif (self.custom_color_input.colour is not None
                          and self.apply_color_check.checkState() == Qt.CheckState.Checked):
                        self.update_custom_colour(self.custom_color_input.colour)

    def select_output_file(self):
        current_path = self.output_file_line.text()
        current_filename = os.path.basename(current_path)
        current_base_dir = os.path.dirname(current_path)
        default_filename = ""
        if len(current_path) > 0 and os.path.isdir(current_base_dir):
            default_filename = current_path
        filepath, _ = QFileDialog.getSaveFileName(
            self, "part save location", default_filename, "LDraw Part (*.dat)"
        )
        if filepath:
            self.output_file_line.setText(filepath)

    def update_custom_colour(self, colour: Brickcolour):
        self.ldraw_object.set_main_colour(colour)

    def disable_custom_colour(self, s):
        if self.custom_color_input.colour is None or s == Qt.CheckState.Unchecked.value:
            if self.ldraw_object.main_colour.colour_code != "16":
                self.update_custom_colour(Brickcolour("16"))
        elif self.custom_color_input.colour.colour_code != "16":
            self.update_custom_colour(self.custom_color_input.colour)
        self.custom_color_input.setDisabled(
            s != Qt.CheckState.Checked.value)

    def show_preview(self):
        hex_bg_color = self.palette().window().color().name()
        r = int(hex_bg_color[1:3], 16)
        g = int(hex_bg_color[3:5], 16)
        b = int(hex_bg_color[5:7], 16)
        self.ldraw_object.scene.show(resolution=(900, 900), caption="Part Preview", background=(r, g, b, 255))

    def reset_part_settings(self):
        self.partname_line.clear()
        self.bl_number_line.clear()
        self.author_line.clear()
        self.apply_color_check.setChecked(False)
        self.custom_color_input.changecolour(Brickcolour("16"), False)

    def convert_file(self):
        partname = self.partname_line.text()
        if len(partname) == 0:
            partname = "UntitledModel"
            dlg = QMessageBox(self)
            dlg.setWindowTitle("No Partname")
            dlg.setText(f"No partname was set.\nWant to save as 'UntitledModel'")
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            answer = dlg.exec()
            if answer == QMessageBox.StandardButton.No:
                return
        bl_number = self.bl_number_line.text()
        author = self.author_line.text()
        self.ldraw_object.name = partname
        self.ldraw_object.author = author
        self.ldraw_object.bricklinknumber = bl_number
        filepath = self.output_file_line.text()
        if os.path.isfile(filepath):
            dlg = QMessageBox(self)
            dlg.setWindowTitle("File already Exists")
            dlg.setText(f"There is already a file with the same name:\n{filepath}\nOverride?")
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            answer = dlg.exec()
            if answer == QMessageBox.StandardButton.No:
                return
        elif len(os.path.basename(filepath)) == 0:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("No Outputfile")
            dlg.setText("No output file specified")
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.exec()
            return
        elif not os.path.isdir(os.path.dirname(filepath)):
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Invalid output directory")
            dlg.setText(f"'{os.path.dirname(filepath)}' is not a valid output directory")
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.exec()
            return
        if self.custom_color_input.colour is None:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Invalid Colour")
            dlg.setText("The custom colour is invalid")
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.exec()
            return
        try:
            self.ldraw_object.convert_to_dat_file(filepath)
        except Exception:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Conversion Failed")
            dlg.setText("Conversion may have failed due to unknown error")
            dlg.setIcon(QMessageBox.Icon.Critical)
            dlg.exec()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Conversion Successfull")
            dlg.setText(f"Model was saved to {filepath}")
            dlg.setIcon(QMessageBox.Icon.Information)
            dlg.exec()


def mm_float_to_string(number: float | int):
    if number >= 100:
        return f"{(number / 100):.2f}m"
    elif number >= 10:
        return f"{(number / 10):.2f}cm"
    return f"{number:.2f}mm"


if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(os.path.join(basedir, "icons/ConvertToLDraw_icon.ico")))

    window = MainWindow()

    window.show()

app.exec()
