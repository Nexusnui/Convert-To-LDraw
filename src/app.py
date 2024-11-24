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
    QDoubleSpinBox,
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

        # Input File Selection
        input_label = QLabel("Input File")
        input_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        file_select_inputs.addWidget(input_label)
        input_layout = QHBoxLayout()

        self.input_file_line = QLineEdit()
        self.input_file_line.setPlaceholderText("Select file to load")
        self.input_file_line.setReadOnly(True)
        input_layout.addWidget(self.input_file_line)

        self.load_input_button = QPushButton("Load File")
        input_layout.addWidget(self.load_input_button)
        self.load_input_button.clicked.connect(self.load_file)

        file_select_inputs.addLayout(input_layout)

        # Enable Multicolour Check
        multicolour_check_layout = QHBoxLayout()
        multicolour_check_layout.addWidget(QLabel("Multicolour"))
        self.multicolour_check = QCheckBox()
        multicolour_check_layout.addWidget(self.multicolour_check)
        self.multicolour_check.setChecked(True)
        file_select_inputs.addLayout(multicolour_check_layout)
        # Todo: Add Functionality

        # Enable Multi Objects Check
        multi_object_check_layout = QHBoxLayout()
        multi_object_check_layout.addWidget(QLabel("Multiple objects"))
        self.multi_object_check = QCheckBox()
        multi_object_check_layout.addWidget(self.multi_object_check)
        self.multi_object_check.setChecked(True)
        file_select_inputs.addLayout(multi_object_check_layout)
        # Todo: Add Functionality

        # Set Scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale"))
        self.scale_input = QDoubleSpinBox()
        self.scale_input.setValue(1.0)
        self.scale_input.setMaximum(999.999)
        self.scale_input.setMinimum(0.001)
        self.scale_input.setDecimals(3)
        scale_layout.addWidget(self.scale_input)
        file_select_inputs.addLayout(scale_layout)
        # Todo: Add Functionality

        # Reload Button
        self.reload_button = QPushButton("Reload Model")
        self.reload_button.setIcon(QIcon(os.path.join(basedir, "icons/reload-icon.svg")))
        self.reload_button.clicked.connect(lambda a: self.load_file(True))
        file_select_inputs.addWidget(self.reload_button)

        # Output File Selection
        output_label = QLabel("Output File")
        output_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        file_select_inputs.addWidget(output_label)
        output_layout = QHBoxLayout()

        self.output_file_line = QLineEdit()
        self.output_file_line.setReadOnly(True)
        self.output_file_line.setPlaceholderText("Select output file")
        output_layout.addWidget(self.output_file_line)

        self.select_output_button = QPushButton("Select")
        output_layout.addWidget(self.select_output_button)
        self.select_output_button.clicked.connect(self.select_output_file)

        file_select_inputs.addLayout(output_layout)

        # Convert Button
        self.convert_button = QPushButton("Convert File")
        file_select_area.addWidget(self.convert_button)
        self.convert_button.clicked.connect(self.convert_file)

    # Part settings area:
        part_settings_area = QVBoxLayout()
        part_settings_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        part_settings_label = QLabel("Part Settings")
        part_settings_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        part_settings_area.addWidget(part_settings_label)

        part_settings_inputs = QVBoxLayout()
        part_settings_frame = QFrame()
        part_settings_frame.setFrameStyle(1)
        part_settings_frame.setLayout(part_settings_inputs)
        part_settings_area.addWidget(part_settings_frame)

        # Partname Input
        partname_layout = QHBoxLayout()
        partname_layout.addWidget(QLabel("Part Name"))
        self.partname_line = QLineEdit()
        self.partname_line.setPlaceholderText("UntitledModel")
        partname_layout.addWidget(self.partname_line)
        part_settings_inputs.addLayout(partname_layout)

        # Bricklink Number Input
        bl_number_layout = QHBoxLayout()
        bl_number_layout.addWidget(QLabel("BL Number(Optional)"))
        self.bl_number_line = QLineEdit()
        self.bl_number_line.setPlaceholderText("Bricklinknumber")
        bl_number_layout.addWidget(self.bl_number_line)
        part_settings_inputs.addLayout(bl_number_layout)

        # Author Input
        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("Author (Optional)"))
        self.author_line = QLineEdit()
        self.author_line.setPlaceholderText("Your Name/Alias")
        author_layout.addWidget(self.author_line)
        part_settings_inputs.addLayout(author_layout)

        # Color Selection (Entire Part)
        self.custom_color_input = BrickcolourWidget("Custom Color")
        self.custom_color_input.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        part_settings_inputs.addWidget(self.custom_color_input)

        self.apply_color_button = QPushButton("Apply Colour")
        self.apply_color_button.clicked.connect(self.apply_custom_colour)
        part_settings_inputs.addWidget(self.apply_color_button)

    # Preview Area
        preview_area = QHBoxLayout()

        self.preview_button = QPushButton("Show Preview")
        self.preview_button.clicked.connect(self.show_preview)
        self.preview_button.setDisabled(True)
        preview_area.addWidget(self.preview_button)

        self.loaded_file_status_label = QLabel("No file loaded")
        preview_area.addWidget(self.loaded_file_status_label)

    # Add Elements to Main Layout
        top_layout.addLayout(part_settings_area)
        top_layout.addLayout(file_select_area)
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(preview_area)
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.disable_settings(True)
        self.load_input_button.setDisabled(False)
        self.setCentralWidget(widget)

    def load_file(self, reload=False):
        filepath = self.input_file_line.text()
        filename = os.path.basename(filepath)
        if reload:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Reload Model?")
            dlg.setText(f'Reloading resets all colours and other changes\n Reload "{filename}"?')
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            answer = dlg.exec()
            if answer == QMessageBox.StandardButton.No:
                return
        self.disable_settings(True)
        previous_status_text = self.loaded_file_status_label.text()
        self.loaded_file_status_label.setText(f"Loading File")
        if not reload:
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            dialog.setNameFilter("3D File (*.stl  *.3mf *.obj *.off *.ply *.gltf *.glb *.xaml *.stp *.step *.dae);;"
                                 "Unknown Compatibility (*.brep *.igs *.iges *.bdf *.msh *.inp *.diff *.mesh);;"
                                 "Any File (*.*)")
            dialog.setViewMode(QFileDialog.ViewMode.Detail)
            if dialog.exec():
                filepath = dialog.selectedFiles()[0]
        if filepath and len(filepath) > 0:
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
                self.load_input_button.setDisabled(False)
            else:
                self.reset_part_settings()
                self.ldraw_object = loaded_part
                self.input_file_line.setText(filepath)
                name = ".".join(filename.split(".")[:-1])
                filedir = os.path.dirname(filepath)
                self.partname_line.setText(name)
                self.output_file_line.setText(f"{filedir}/{name}.dat")

                x_length = mm_float_to_string(self.ldraw_object.size[0])
                y_length = mm_float_to_string(self.ldraw_object.size[1])
                z_length = mm_float_to_string(self.ldraw_object.size[2])
                self.loaded_file_status_label.setText(f"Current Model: {filename} ({x_length}×{y_length}×{z_length})")

                if not self.file_loaded:
                    self.file_loaded = True
                self.disable_settings(False)
        # No file Selected
        else:
            if self.file_loaded:
                self.loaded_file_status_label.setText(previous_status_text)
                self.disable_settings(False)
            else:
                self.loaded_file_status_label.setText("No file loaded")
                self.load_input_button.setDisabled(False)


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

    def apply_custom_colour(self):
        self.disable_settings(True)
        colour = self.custom_color_input.colour
        colour_name = colour.colour_code
        if colour.colour_type == "LDraw":
            colour_name = colour.ldrawname
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Override Colours?")
        dlg.setText(f'Override all colours with "{colour_name}"')
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        answer = dlg.exec()
        if answer == QMessageBox.StandardButton.Yes:
            self.ldraw_object.set_main_colour(colour)
        self.disable_settings(False)
        # Todo: Check for multicolor/multiobject


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
        self.apply_color_button.setChecked(False)
        self.custom_color_input.changecolour(Brickcolour("16"), False)

    def disable_settings(self, value: bool):
        self.load_input_button.setDisabled(value)
        self.output_file_line.setReadOnly(value)
        self.select_output_button.setDisabled(value)
        self.apply_color_button.setDisabled(value)
        self.preview_button.setDisabled(value)
        self.convert_button.setDisabled(value)
        self.partname_line.setReadOnly(value)
        self.bl_number_line.setReadOnly(value)
        self.author_line.setReadOnly(value)
        self.custom_color_input.setDisabled(value)
        self.reload_button.setDisabled(value)


    def convert_file(self):
        self.disable_settings(True)
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
                self.disable_settings(False)
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
                self.disable_settings(False)
                return
        elif len(os.path.basename(filepath)) == 0:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("No Outputfile")
            dlg.setText("No output file specified")
            dlg.setIcon(QMessageBox.Icon.Warning)
            self.disable_settings(False)
            dlg.exec()
            return
        elif not os.path.isdir(os.path.dirname(filepath)):
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Invalid output directory")
            dlg.setText(f"'{os.path.dirname(filepath)}' is not a valid output directory")
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.exec()
            self.disable_settings(False)
            return
        if self.custom_color_input.colour is None:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Invalid Colour")
            dlg.setText("The custom colour is invalid")
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.exec()
            self.disable_settings(False)
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
        self.disable_settings(False)


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
