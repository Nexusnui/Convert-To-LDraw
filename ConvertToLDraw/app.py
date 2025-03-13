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
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QDoubleSpinBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QTabWidget
)

from ConvertToLDraw.brick_data.ldrawObject import LdrawObject, Subpart, default_part_licenses
from ConvertToLDraw.brick_data.brick_categories import brick_categories
from ConvertToLDraw.ui_elements.subpartPanel import SubpartPanel, ColourPanel
from ConvertToLDraw.ui_elements.previewPanel import PreviewPanel, register_scheme

basedir = os.path.dirname(__file__)

app_version = "1.3.0"

if platform.system() == "Windows":
    try:
        from ctypes import windll  # Only exists on Windows.

        myappid = f"nexusnui.converttoldraw.{app_version}"
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ldraw_object = None
        self.file_loaded = False
        self.reload_preview = False

        self.setWindowTitle(f"Convert To LDraw {app_version}")
        self.main_layout = QVBoxLayout()
        self.settings_tabs = QTabWidget()

        top_layout = QHBoxLayout()

    # File Selection Area:
        file_select_area = QGroupBox("File Selection")
        file_select_inputs = QFormLayout()
        file_select_area.setLayout(file_select_inputs)

        # Input File Selection
        input_label = QLabel("Input File")
        file_select_inputs.addRow(input_label)
        input_layout = QHBoxLayout()

        self.input_file_line = QLineEdit()
        self.input_file_line.setPlaceholderText("Select file to load")
        self.input_file_line.setReadOnly(True)
        input_layout.addWidget(self.input_file_line)

        self.load_input_button = QPushButton("Load File")
        input_layout.addWidget(self.load_input_button)
        self.load_input_button.clicked.connect(self.load_file)

        file_select_inputs.addRow(input_layout)

        # Enable Multicolour Check
        self.multicolour_check = QCheckBox()
        multicolour_label = QLabel("Multicolour ℹ️")
        multicolour_label.setToolTip("If deactivated aLL objects are single color")
        file_select_inputs.addRow(multicolour_label, self.multicolour_check)
        self.multicolour_check.setChecked(True)

        # Enable Multi Objects Check
        self.multi_object_check = QCheckBox()
        multi_object_label = QLabel("Multiple Objects ℹ️")
        multi_object_label.setToolTip("If deactivated all submodels will be merged\n"
                                      "With multicolor unique colors are applied before merging\n"
                                      "(If the the file does not define colors)")
        file_select_inputs.addRow(multi_object_label, self.multi_object_check)
        self.multi_object_check.setChecked(True)

        # Set Scale
        self.scale_input = QDoubleSpinBox()
        self.scale_input.setValue(1.0)
        self.scale_input.setMaximum(999.999)
        self.scale_input.setMinimum(0.001)
        self.scale_input.setDecimals(3)
        scale_label = QLabel("Scale ℹ️")
        scale_label.setToolTip("Factor used to scale the model")
        file_select_inputs.addRow(scale_label, self.scale_input)

        # Reload Button
        self.reload_button = QPushButton("Reload Model")
        self.reload_button.setIcon(QIcon(os.path.join(basedir, "icons", "reload-icon.svg")))
        self.reload_button.clicked.connect(lambda a: self.load_file(True))
        file_select_inputs.addRow(self.reload_button)

        # Output File Selection
        output_label = QLabel("Output File ℹ️")
        output_label.setToolTip("Place where the Main File is saved.\n"
                                "Subparts are saved in 's' subdirectory located in the same directory")
        file_select_inputs.addRow(output_label)
        output_layout = QHBoxLayout()

        self.output_file_line = QLineEdit()
        self.output_file_line.setReadOnly(True)
        self.output_file_line.setPlaceholderText("Select output file")
        output_layout.addWidget(self.output_file_line)

        self.select_output_button = QPushButton("Select")
        output_layout.addWidget(self.select_output_button)
        self.select_output_button.clicked.connect(self.select_output_file)

        file_select_inputs.addRow(output_layout)

    # Part Settings Area:
        part_settings_area = QGroupBox("Parent Part Settings")
        part_settings_inputs = QFormLayout()
        part_settings_area.setLayout(part_settings_inputs)

        # Partname Input
        self.partname_line = QLineEdit()
        self.partname_line.setPlaceholderText("UntitledModel")
        partname_label = QLabel("Descriptive Part Name ℹ️")
        partname_label.setToolTip("This shows up as the Partname in Editors")
        part_settings_inputs.addRow(partname_label, self.partname_line)

        # Bricklink Number Input
        self.bl_number_line = QLineEdit()
        self.bl_number_line.setPlaceholderText("Bricklinknumber")
        bl_number_label = QLabel("BL Number(Optional) ℹ️")
        bl_number_label.setToolTip("Bricklink Studio uses this to identify a piece\n"
                                   "Leave this empty is there is no Bricklink listing")
        part_settings_inputs.addRow(bl_number_label, self.bl_number_line)

        # Author Input
        self.author_line = QLineEdit()
        self.author_line.setPlaceholderText("Your Name/Alias")
        part_settings_inputs.addRow("Author (Optional)", self.author_line)

        # Category Selection
        self.part_category_input = QComboBox()
        self.part_category_input.addItems(brick_categories)
        self.part_category_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.part_category_input.setEditable(True)
        category_label = QLabel("Part Category (Recommended) ℹ️")
        category_label.setToolTip("Defines the Category the part appears in.\n"
                                  "(Currently not supported by Bricklink Studio)")
        part_settings_inputs.addRow(category_label, self.part_category_input)

        # Keywords Input
        self.keywords_line = QLineEdit()
        self.keywords_line.setPlaceholderText("comma seperated: Wheel, Tire, Car")
        keywords_label = QLabel("Keywords (Optional) ℹ️")
        keywords_label.setToolTip("Keywords make a part easier to search.\n"
                                  "(Currently not supported in Bricklink Studio)")
        part_settings_inputs.addRow(keywords_label, self.keywords_line)

        # License Input
        self.part_license_input = QComboBox()
        self.part_license_input.addItems(default_part_licenses)
        self.part_license_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.part_license_input.setEditable(True)
        part_license_label = QLabel("Part License (Optional) ℹ️")
        part_license_label.setToolTip("License of the Part, set your own one or use one from the list.")
        part_settings_inputs.addRow(part_license_label, self.part_license_input)

        # Convert Button
        self.convert_button = QPushButton("Convert File")
        self.convert_button.clicked.connect(self.convert_file)

    # Loaded File Status Label

        self.loaded_file_status_label = QLabel("No file loaded")
        self.loaded_file_status_label.setAlignment(Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignRight)

    # Subpart and Color Editor Panel
        subpart_area = QWidget()
        self.subpart_area_layout = QVBoxLayout()
        subpart_area.setLayout(self.subpart_area_layout)

    # Preview Panel
        hex_bg_color = self.palette().window().color().name()
        self.preview_panel = PreviewPanel(background_color=hex_bg_color)

    # Add Elements to Main Layout
        top_layout.addWidget(part_settings_area)
        top_layout.addWidget(file_select_area)
        main_settings_widget = QWidget()
        main_settings_widget.setLayout(top_layout)
        self.settings_tabs.addTab(main_settings_widget, "Main Part Settings")

        self.main_layout.addWidget(self.settings_tabs)
        file_select_inputs.addRow(self.convert_button)

        self.settings_tabs.addTab(subpart_area, "Subpart and Colour Settings")
        self.settings_tabs.addTab(self.preview_panel, "Part Preview")
        self.settings_tabs.currentChanged.connect(self.tab_changed_actions)

        self.main_layout.addWidget(self.loaded_file_status_label)
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.disable_settings(True)
        self.enable_load_settings()
        self.setCentralWidget(widget)

    def load_file(self, reload=False):
        filepath = self.input_file_line.text()
        filename = os.path.basename(filepath)
        if reload:
            answer = QMessageBox.warning(
                self,
                "Reload Model?",
                f'Reloading resets all colours and other changes\n Reload "{filename}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
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
            scale = self.scale_input.value()
            multicolour = self.multicolour_check.checkState() == Qt.CheckState.Checked
            multi_object = self.multi_object_check.checkState() == Qt.CheckState.Checked
            try:
                loaded_part = LdrawObject(filepath, scale=scale, multi_object=multi_object, multicolour=multicolour)
            except Exception:
                QMessageBox.critical(self, "Failed to load file", "Not a 3D object or unsupported file format")
                self.loaded_file_status_label.setText(f"Failed to Load: {filename}")
                self.enable_load_settings()
            else:
                if not reload:
                    self.reset_part_settings()

                self.ldraw_object = loaded_part
                self.input_file_line.setText(filepath)
                name = ".".join(filename.split(".")[:-1])
                filedir = os.path.dirname(filepath)
                self.partname_line.setText(name)
                self.output_file_line.setText(f"{filedir}/{name}.dat")

                if self.file_loaded:
                    self.subpart_area_layout.removeWidget(self.subpart_panel)
                    self.subpart_panel.deleteLater()
                if len(self.ldraw_object.subparts) > 1:
                    self.subpart_panel = SubpartPanel(self.ldraw_object, self)
                    self.subpart_panel.show_preview.connect(self.show_preview)
                else:
                    self.subpart_panel = ColourPanel(self.ldraw_object, self)
                self.subpart_area_layout.addWidget(self.subpart_panel)
                self.subpart_panel.model_updated.connect(self.enable_reload)

                x_length = mm_float_to_string(self.ldraw_object.size[0])
                y_length = mm_float_to_string(self.ldraw_object.size[1])
                z_length = mm_float_to_string(self.ldraw_object.size[2])
                self.loaded_file_status_label.setText(f"Current Model: {filename} ({x_length}×{y_length}×{z_length})")

                if not self.file_loaded:
                    self.file_loaded = True
                self.preview_panel.set_main_model(self.ldraw_object, True)
                self.disable_settings(False)
        # No file Selected
        else:
            if self.file_loaded:
                self.loaded_file_status_label.setText(previous_status_text)
                self.disable_settings(False)
            else:
                self.loaded_file_status_label.setText("No file loaded")
                self.enable_load_settings()

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

    def show_preview(self, subpart: Subpart):
        self.preview_panel.load_subpart(subpart)
        self.reload_preview = False
        self.settings_tabs.setCurrentIndex(2)

    def reset_part_settings(self):
        self.partname_line.clear()
        self.bl_number_line.clear()
        self.author_line.clear()
        self.part_category_input.clearEditText()
        self.part_license_input.clearEditText()
        self.keywords_line.clear()

    def disable_settings(self, value: bool):
        self.load_input_button.setDisabled(value)
        self.output_file_line.setReadOnly(value)
        self.select_output_button.setDisabled(value)
        self.convert_button.setDisabled(value)
        self.partname_line.setReadOnly(value)
        self.bl_number_line.setReadOnly(value)
        self.author_line.setReadOnly(value)
        self.reload_button.setDisabled(value)
        self.multicolour_check.setDisabled(value)
        self.multi_object_check.setDisabled(value)
        self.scale_input.setDisabled(value)
        self.part_category_input.setDisabled(value)
        self.part_license_input.setDisabled(value)
        self.keywords_line.setReadOnly(value)
        self.settings_tabs.tabBar().setDisabled(value)
        if self.file_loaded:
            self.subpart_panel.setDisabled(value)

    def enable_load_settings(self):
        self.multicolour_check.setDisabled(False)
        self.multi_object_check.setDisabled(False)
        self.scale_input.setDisabled(False)
        self.load_input_button.setDisabled(False)

    def enable_reload(self):
        self.reload_preview = True

    def tab_changed_actions(self, tab_index):
        if tab_index == 2 and self.reload_preview:
            self.preview_panel.reload_model()
            self.reload_preview = False

    def convert_file(self):
        self.disable_settings(True)
        partname = self.partname_line.text()
        if len(partname) == 0:
            partname = "UntitledModel"
            answer = QMessageBox.warning(
                self,
                "No Partname",
                f"No partname was set.\nWant to save as 'UntitledModel'",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if answer == QMessageBox.StandardButton.No:
                self.disable_settings(False)
                return
        category = self.part_category_input.currentText()
        if category not in brick_categories and len(category) > 0:
            answer = QMessageBox.warning(
                self,
                "Unofficial Category",
                f'The category "{category}" is not one of official LDraw Categories.\n'
                f'Do want to use it anyway?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if answer == QMessageBox.StandardButton.No:
                self.disable_settings(False)
                return
        keywords = []
        for kw in self.keywords_line.text().split(","):
            # Remove redundant spaces
            word = " ".join([w for w in kw.split(" ") if w != ""])
            if len(word) > 0:
                keywords.append(word)
        bl_number = self.bl_number_line.text()
        author = self.author_line.text()
        part_license = self.part_license_input.currentText()
        self.ldraw_object.name = partname
        self.ldraw_object.author = author
        self.ldraw_object.bricklinknumber = bl_number
        self.ldraw_object.category = category
        self.ldraw_object.keywords = keywords
        self.ldraw_object.part_license = part_license
        filepath = self.output_file_line.text()
        if os.path.isfile(filepath):
            answer = QMessageBox.warning(
                self,
                "File already Exists",
                f"There is already a file with the same name:\n{filepath}\nOverride?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if answer == QMessageBox.StandardButton.No:
                self.disable_settings(False)
                return
        elif len(os.path.basename(filepath)) == 0:
            QMessageBox.warning(self, "No Outputfile", "No output file specified")
            self.disable_settings(False)
            return
        elif not os.path.isdir(os.path.dirname(filepath)):
            QMessageBox.warning(self, "Invalid directory", f"'{os.path.dirname(filepath)}' is not a valid directory")
            self.disable_settings(False)
            return
        try:
            self.ldraw_object.convert_to_dat_file(filepath)
        except Exception:
            QMessageBox.critical(self, "Conversion Failed", "Conversion failed due to unknown error")
        else:
            QMessageBox.information(self, "Conversion Successfull", f"Model was saved to {filepath}")
        self.disable_settings(False)


def mm_float_to_string(number: float | int):
    if number >= 100:
        return f"{(number / 100):.2f}m"
    elif number >= 10:
        return f"{(number / 10):.2f}cm"
    return f"{number:.2f}mm"


def run():
    register_scheme()
    app = QApplication([0])
    app.setWindowIcon(QIcon(os.path.join(basedir, "icons", "ConvertToLDraw_icon.ico")))

    window = MainWindow()

    window.show()

    app.exec()


if __name__ == "__main__":
    run()
