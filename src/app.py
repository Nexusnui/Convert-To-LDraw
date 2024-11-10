import os
import platform
from brick_data.brickcolour import Brickcolour, is_brickcolour
from brick_data.ldrawObject import LdrawObject
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
)
from PyQt6.QtGui import QIcon
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

        self.setWindowTitle("Convert To LDraw")
        self.main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        #File Selection Area:
        file_select_area = QVBoxLayout()
        file_select_area.addWidget(QLabel("File Selection"))

        file_select_inputs = QVBoxLayout()
        file_select_frame = QFrame()
        file_select_frame.setFrameStyle(1)
        file_select_frame.setLayout(file_select_inputs)
        file_select_area.addWidget(file_select_frame)

        file_select_inputs.addWidget(QLabel("Input File"))
        input_layout = QHBoxLayout()

        self.input_file_line = QLineEdit()
        self.input_file_line.setPlaceholderText("Select file to load")
        input_layout.addWidget(self.input_file_line)

        select_input_button = QPushButton("Select")
        input_layout.addWidget(select_input_button)
        #Todo: connect to Fileselection Dialog

        file_select_inputs.addLayout(input_layout)

        file_select_inputs.addWidget(QLabel("Output File"))
        output_layout = QHBoxLayout()

        self.output_file_line = QLineEdit()
        self.output_file_line.setPlaceholderText("Select output file")
        output_layout.addWidget(self.output_file_line)

        select_output_button = QPushButton("Select")
        output_layout.addWidget(select_output_button)
        # Todo: connect to Fileselection Dialog

        file_select_inputs.addLayout(output_layout)

        convert_button = QPushButton("Convert File")
        file_select_area.addWidget(convert_button)
        # Todo: connect to convert function

        #Part settings area:
        part_settings_area = QVBoxLayout()
        part_settings_area.addWidget(QLabel("Part Settings"))

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
        apply_color_layout.addWidget(self.apply_color_check)
        part_settings_inputs.addLayout(apply_color_layout)
        #Todo: Connect Checkbox to enable colour selection

        self.custom_color_input = BrickcolourWidget("Custom Color")
        part_settings_inputs.addWidget(self.custom_color_input)

        top_layout.addLayout(part_settings_area)
        top_layout.addLayout(file_select_area)
        self.main_layout.addLayout(top_layout)
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(os.path.join(basedir, "icons/stlToLDraw_icon.ico")))

    window = MainWindow()

    window.show()

app.exec()
