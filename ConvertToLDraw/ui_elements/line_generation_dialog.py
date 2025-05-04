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
    QCheckBox
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
                 merge_vertices: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Generate Outlines Colour")

        self.merge_vertices = merge_vertices

        self.preset = initial_preset
        if self.preset == LinePreset.Custom:
            self.angle = initial_angle
        else:
            self.angle = self.preset.value

        main_layout = QVBoxLayout()

        main_inputs = QFormLayout()

        # Todo: Tooltips Labels

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


if __name__ == "__main__":
    app = QApplication([])

    line_dia = LineGenerationDialog(initial_preset=LinePreset.Custom, initial_angle=45, merge_vertices=True)
    line_dia.exec()

    print(line_dia.preset, line_dia.angle, line_dia.merge_vertices)
