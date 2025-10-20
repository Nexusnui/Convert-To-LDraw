from PyQt6.QtWidgets import (
    QHBoxLayout,
    QApplication,
    QVBoxLayout,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QCheckBox,
    QPushButton,
    QMessageBox
)

from enum import Enum


class LinePreset(Enum):
    Low = 85
    Medium = 45
    High = 10
    Custom = None


preset_names = [e.name for e in LinePreset]


class LineGenerationDialog(QDialog):

    def __init__(self, parent=None,
                 initial_preset: LinePreset = LinePreset.Low,
                 initial_angle: float = 0,
                 merge_vertices: bool = False,
                 is_edit: bool = False):
        super().__init__(parent)
        if is_edit:
            self.setWindowTitle("Edit Outlines")
        else:
            self.setWindowTitle("Generate Outlines")

        self.merge_vertices = merge_vertices

        self.preset = initial_preset
        self.delete_flag = False
        if self.preset == LinePreset.Custom:
            self.angle = initial_angle
        else:
            self.angle = self.preset.value

        main_layout = QVBoxLayout()

        main_inputs = QFormLayout()

        self.preset_selection = QComboBox()
        self.preset_selection.addItems(preset_names)
        self.preset_selection.setCurrentIndex(preset_names.index(self.preset.name))
        self.preset_selection.currentIndexChanged.connect(self.preset_changed)

        main_inputs.addRow("Sensitivity", self.preset_selection)

        self.angle_input = QDoubleSpinBox()
        self.angle_input.valueChanged.connect(self.angle_changed)
        self.angle_input.setMaximum(180)
        self.angle_input.setMinimum(0)
        self.angle_input.setSuffix("°")
        self.angle_input.setValue(self.angle)
        if self.preset != LinePreset.Custom:
            self.angle_input.setDisabled(True)

        main_inputs.addRow("Minimum Angle", self.angle_input)

        main_layout.addLayout(main_inputs)

        advanced_section = QGroupBox("Advanced")
        advanced_layout = QVBoxLayout()
        merge_vertices_check = QCheckBox("Fix Normals ℹ️")
        merge_vertices_check.setChecked(self.merge_vertices)
        merge_vertices_check.setToolTip("This can sometimes helps if no lines are generated.\n"
                                        "But line generation may take longer on large models.")
        merge_vertices_check.checkStateChanged.connect(self.merge_check_changed)
        advanced_layout.addWidget(merge_vertices_check)
        advanced_section.setLayout(advanced_layout)

        main_layout.addWidget(advanced_section)
        if is_edit:
            delete_button = QPushButton("Delete Outlines")
            delete_button.setStyleSheet("color: white; background-color: red;")
            delete_button.clicked.connect(self.delete_button_pressed)
            main_layout.addWidget(delete_button)

        bottom_layout = QHBoxLayout()
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        bottom_layout.addWidget(button_box)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def angle_changed(self, angle):
        self.angle = angle

    def preset_changed(self, index):
        self.preset = LinePreset[self.preset_selection.currentText()]
        if self.preset == LinePreset.Custom:
            self.angle_input.setDisabled(False)
        else:
            self.angle_input.setDisabled(True)
            self.angle = self.preset.value
            self.angle_input.setValue(self.preset.value)

    def merge_check_changed(self, check):
        self.merge_vertices = not self.merge_vertices

    def delete_button_pressed(self):
        answer = QMessageBox.question(self, "Delete Outline?", "Do you want delete the outlines?")

        if answer == QMessageBox.StandardButton.Yes:
            print("Delete")
            self.delete_flag = True
            self.accept()


if __name__ == "__main__":
    app = QApplication([])

    line_dia = LineGenerationDialog(
        initial_preset=LinePreset.Custom,
        initial_angle=45,
        merge_vertices=True,
        is_edit=True
    )
    line_dia.exec()

    print(f"{line_dia.preset=}\n"
          f"{line_dia.angle=}\n"
          f"{line_dia.merge_vertices}\n"
          f"{line_dia.delete_flag=}")
