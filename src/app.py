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

        myappid = "nexusnui.converttoldraw.1.0"
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ldraw_object = None

        self.setWindowTitle("Convert To LDraw")
        self.main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        #File Selection Area:
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
        # Todo: connect to convert function

        #Part settings area:
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

        #Preview Button
        preview_button = QPushButton("Show Preview")
        #Todo: Create and Connect to show preview function

        #Add Elements to Main Layout
        top_layout.addLayout(part_settings_area)
        top_layout.addLayout(file_select_area)
        self.main_layout.addLayout(top_layout)
        self.main_layout.addWidget(preview_button)
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def load_file(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("3D File (*.stl  *.3mf *.obj);;Any File (*.*)")
        # Todo: add more file extensions of known compatible file formats'''
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        if dialog.exec():
            filepath = dialog.selectedFiles()[0]
            if filepath:
                try:
                    loaded_part = LdrawObject(filepath)
                except Exception:
                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("Failed to load file")
                    dlg.setText("File was not a 3D object or the format is unsupported")
                    dlg.setIcon(QMessageBox.Icon.Critical)
                    dlg.exec()
                else:
                    self.ldraw_object = loaded_part
                    self.input_file_line.setText(filepath)
                    filename = os.path.basename(filepath)
                    name = ".".join(filename.split(".")[:-1])
                    filedir = os.path.dirname(filepath)
                    self.partname_line.setText(name)
                    self.output_file_line.setText(f"{filedir}/{name}.dat")
                    self.output_file_line.setReadOnly(False)
                    self.select_output_button.setDisabled(False)
                    self.apply_color_check.setDisabled(False)

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
        print(colour)
        self.ldraw_object.set_main_colour(colour)

    def disable_custom_colour(self, s):
        if self.custom_color_input.colour is None or s == Qt.CheckState.Unchecked.value:
            if self.ldraw_object.main_colour.colour_code != "16":
                self.update_custom_colour(Brickcolour("16"))
        elif self.custom_color_input.colour.colour_code != "16":
            self.update_custom_colour(self.custom_color_input.colour)
        self.custom_color_input.setDisabled(
            s != Qt.CheckState.Checked.value)


if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(os.path.join(basedir, "icons/stlToLDraw_icon.ico")))

    window = MainWindow()

    window.show()

app.exec()
