from PyQt6.QtCore import pyqtSignal, QAbstractTableModel, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QTabWidget,
    QWidget,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QTableView,
    QHeaderView,
    QLabel
)

from ConvertToLDraw.brick_data.ldrawObject import LdrawObject, Subpart
from ConvertToLDraw.brick_data.brickcolour import Brickcolour, is_brickcolour, get_contrast_colour
from ConvertToLDraw.ui_elements.brickcolourwidget import BrickcolourWidget, BrickcolourDialog, ColourCategoriesDialog
from ConvertToLDraw.ui_elements.line_generation_dialog import LineGenerationDialog, LinePreset


class SubpartPanel(QTabWidget):
    model_updated = pyqtSignal()
    show_preview = pyqtSignal(Subpart)

    def __init__(self, mainmodel: LdrawObject, main_window):
        super().__init__()

        self.main_window = main_window
        for sp in mainmodel.subparts:
            self.__add_tab(sp)
        self.setMovable(True)
        self.tabBar().tabMoved.connect(mainmodel.subpart_order_changed)

    def __add_tab(self, subpart: Subpart):
        tab = SubpartTab(subpart, main_window=self.main_window)
        index = self.addTab(tab, subpart.name)
        tab.name_changed.connect(lambda name: self.subpart_name_changed(self.indexOf(tab), name))
        tab.colour_changed.connect(self.model_updated.emit)
        tab.show_preview.connect(self.relay_preview_data)

    def subpart_name_changed(self, index, name):
        self.setTabText(index, name)
        self.model_updated.emit()

    def setDisabled(self, value: bool):
        self.currentWidget().setDisabled(value)
        self.tabBar().setDisabled(value)

    def relay_preview_data(self, subpart: Subpart):
        self.show_preview.emit(subpart)

    def update_children(self):
        for index in range(self.count()):
            tab = self.widget(index)
            tab.refresh_content()


class ColourPanel(QWidget):
    model_updated = pyqtSignal()

    def __init__(self, mainmodel: LdrawObject, main_window):
        super().__init__()
        mainlayout = QVBoxLayout()
        self.setLayout(mainlayout)
        subpart = mainmodel.subparts[0]
        self.content = SubpartTab(subpart, single_part=True, main_window=main_window)
        self.content.colour_changed.connect(self.model_updated.emit)
        mainlayout.addWidget(self.content)

    def update_children(self):
        self.content.refresh_content()

class SubpartTab(QWidget):
    name_changed = pyqtSignal(str)
    colour_changed = pyqtSignal()
    show_preview = pyqtSignal(Subpart)

    def __init__(self, subpart: Subpart, main_window, single_part=False, ):
        super().__init__()
        self.subpart = subpart
        self.main_window = main_window

        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)

        self.line_preset = LinePreset.Low
        self.line_angle = LinePreset.Low.value
        self.merge_vertices = False

    # Main Settings Area
        self.main_settings = QFormLayout()

        # Name Input and Subpart Preview Button
        if not single_part:
            self.name_line = QLineEdit()
            self.name_line.setText(self.subpart.name)
            self.main_settings.addRow("Name", self.name_line)
            self.name_line.textChanged.connect(self.apply_name_change)
            self.preview_button = QPushButton("Open Subpart in Preview")
            self.preview_button.clicked.connect(self.send_preview_data)

        # Generate Outlines, Override / Set Colour
        self.colour_inputs = QWidget()
        self.colour_inputs_layout = QHBoxLayout()
        self.main_settings.addRow(self.colour_inputs)
        self.colour_inputs.setLayout(self.colour_inputs_layout)

        self.generate_outlines_button = QPushButton("Generate Outlines")
        self.generate_outlines_button.clicked.connect(self.generate_outlines)
        self.colour_inputs_layout.addWidget(self.generate_outlines_button)

        if self.subpart.multicolour:
            self.multicolour_view_enabled = True
            self.merge_colours_button = QPushButton("Merge Duplicate Colours")
            self.merge_colours_button.clicked.connect(self.merge_duplicate_colours)
            self.colour_inputs_layout.addWidget(self.merge_colours_button)

            self.map_colours_button = QPushButton("Convert to Ldraw Colours")
            self.map_colours_button.clicked.connect(self.map_colours_to_LDraw)
            self.colour_inputs_layout.addWidget(self.map_colours_button)

            main_colour_text = "Override Colour"
            brick_colour = Brickcolour("16")
        else:
            self.multicolour_view_enabled = False
            main_colour_text = "Subpart Colour"
            brick_colour = self.subpart.main_colour
        self.main_colour_input = BrickcolourWidget(main_colour_text, brick_colour)
        self.main_settings.addRow(self.main_colour_input)
        if self.subpart.multicolour:
            self.apply_colour_button = QPushButton("Apply Override Colour")
            self.apply_colour_button.clicked.connect(self.apply_main_colour)
            self.main_settings.addRow(self.apply_colour_button)
            self.multicolour_widget = QTableView()
            self.multicolour_widget.setCornerButtonEnabled(False)
            button_colour = self.palette().button().color()
            self.subpartcolourlist = Subpartcolourlistmodel(self.subpart, button_colour)
            self.subpartcolourlist.colour_changed.connect(self.colour_changed.emit)
            self.multicolour_widget.setModel(self.subpartcolourlist)
            self.multicolour_widget.clicked.connect(self._on_select_brickcolour)
            self.multicolour_widget.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.multicolour_widget.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
            self.multicolour_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            self.multicolour_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            row_height = self.multicolour_widget.verticalHeader().sectionSize(0)
            width = self.multicolour_widget.size().width()
            new_widget_height = row_height * 5
            if len(self.subpart.colours) < 5:
                new_widget_height = (len(self.subpart.colours) + 1) * row_height
            self.multicolour_widget.setMinimumSize(width, new_widget_height)
            # Model Info Label
            self.right_info_label = QLabel(f"{len(self.subpart.mesh.faces)} Triangles "
                                           f"with {len(self.subpart.colours)} Different Colours")
        else:
            self.right_info_label = QLabel(f"{len(self.subpart.mesh.faces)} Triangles")
            self.main_colour_input.colour_changed.connect(self.apply_main_colour)
        infolabels_layout = QHBoxLayout()
        self.left_info_label = QLabel("No Outlines Generated")
        infolabels_layout.addWidget(self.left_info_label)
        infolabels_layout.addStretch()
        infolabels_layout.addWidget(self.right_info_label)



    # Add Elements to Main Layout
        self.mainlayout.addLayout(self.main_settings)
        if self.subpart.multicolour:
            self.mainlayout.addWidget(self.multicolour_widget)
        self.mainlayout.addStretch()
        self.mainlayout.addLayout(infolabels_layout)
        if not single_part:
            self.mainlayout.addWidget(self.preview_button)

    def apply_name_change(self, new_name: str):
        self.subpart.name = new_name
        self.name_changed.emit(new_name)

    def apply_main_colour(self, colour: Brickcolour = None):
        if self.subpart.multicolour:
            self.setDisabled(True)
            colour = self.main_colour_input.colour
            colour_name = colour.colour_code
            if colour.colour_type == "LDraw":
                colour_name = colour.ldrawname
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Override Colours?")
            dlg.setText(f'Override all colours with "{colour_name}"\n'
                        f'(Only reversible by reloading the file)')
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            answer = dlg.exec()
            if answer == QMessageBox.StandardButton.Yes:
                self.subpart.apply_color(colour)
                self._change_to_single_colour_view()
                self.colour_changed.emit()
            else:
                self.setDisabled(False)
                return
        elif colour is None:
            return
        else:
            self.subpart.apply_color(colour)
            self.colour_changed.emit()
        self.setDisabled(False)

    def send_preview_data(self):
        self.show_preview.emit(self.subpart)

    def changecolour(self, colour: Brickcolour, key):
        self.subpart.apply_color(colour, key)
        self.colour_changed.emit()

    def merge_duplicate_colours(self):
        self.setDisabled(True)
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Merge Duplicate Colours?")
        dlg.setText(f'Merge duplicate colours?\n'
                    f'(Only reversible by reloading the file)')
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        answer = dlg.exec()
        if answer == QMessageBox.StandardButton.Yes:
            self.subpart.merge_duplicate_colours()
            self.subpartcolourlist.refresh_data()
            if not self.subpart.multicolour:
                self._change_to_single_colour_view()
                self.right_info_label.setText(f"{len(self.subpart.mesh.faces)} Triangles")
            else:
                self.right_info_label.setText(f"{len(self.subpart.mesh.faces)} Triangles "
                                              f"with {len(self.subpart.colours)} Different Colours")
        self.setDisabled(False)

    def map_colours_to_LDraw(self):
        categories_dialog = ColourCategoriesDialog(
            message="Select Colour Categories Direct/HTML will be matched with.\n"
                    "(Only Reversible by reloading and may take a while)"
        )

        self.main_window.show_loading_screen("Mapping Colours\nCould take a bit of time")

        if categories_dialog.exec():
            colour_categories = categories_dialog.get_selected_items()
            if len(colour_categories) == 0:
                QMessageBox.warning(self, "Nothing Selected", "No Categories selected\nMapping Aborted")
                return
            self.main_window.disable_settings(True)
            self.subpart.map_to_ldraw_colours(colour_categories)
            self.refresh_content()
            self.main_window.disable_settings(False)
            self.colour_changed.emit()
        self.main_window.hide_loading_screen()

    def generate_outlines(self):
        if len(self.subpart.outlines) == 0:
            outline_dialog = LineGenerationDialog(self, self.line_preset, self.line_angle, self.merge_vertices)
        else:
            outline_dialog = LineGenerationDialog(self, self.line_preset, self.line_angle, self.merge_vertices, True)
        if outline_dialog.exec():
            if outline_dialog.delete_flag:
                self.subpart.outlines = []
            else:
                self.line_preset = outline_dialog.preset
                self.line_angle = outline_dialog.angle
                self.merge_vertices = outline_dialog.merge_vertices
                self.subpart.generate_outlines(self.line_angle, self.merge_vertices)
                self.colour_changed.emit()
            self.refresh_content()

    def _on_select_brickcolour(self, index):
        if index.column() in [0, 2]:
            self.multicolour_widget.clearSelection()
        if index.column() == 2:
            colour_key = self.subpartcolourlist.data(index, Qt.ItemDataRole.UserRole)
            initial_color = self.subpart.colours[colour_key][0]
            color_picker = BrickcolourDialog(initial_color)
            color_picker.accepted.connect(lambda: self.changecolour(color_picker.brickcolour, colour_key))
            color_picker.exec()

    def _change_to_single_colour_view(self):
        self.subpart.multicolour = False
        self.mainlayout.removeWidget(self.multicolour_widget)
        self.multicolour_widget.deleteLater()
        self.main_colour_input.colour_changed.connect(self.apply_main_colour)
        self.main_settings.removeWidget(self.apply_colour_button)
        self.apply_colour_button.deleteLater()
        self.colour_inputs_layout.removeWidget(self.map_colours_button)
        self.colour_inputs_layout.removeWidget(self.merge_colours_button)
        self.map_colours_button.deleteLater()
        self.merge_colours_button.deleteLater()
        self.main_colour_input.label.setText("Subpart Colour")
        self.main_colour_input.changecolour(self.subpart.main_colour, False)
        self.multicolour_view_enabled = False

    def refresh_content(self):
        if not self.subpart.multicolour:
            if self.multicolour_view_enabled:
                self._change_to_single_colour_view()
            self.main_colour_input.changecolour(self.subpart.main_colour, send_emit=False, set_text=True)
            self.right_info_label.setText(f"{len(self.subpart.mesh.faces)} Triangles")
        elif self.subpart.multicolour:
            self.subpartcolourlist.refresh_data()
            self.right_info_label.setText(f"{len(self.subpart.mesh.faces)} Triangles "
                                          f"with {len(self.subpart.colours)} Different Colours")
        if len(self.subpart.outlines) > 0:
            self.left_info_label.setText(f"{len(self.subpart.outlines)} Outlines")
            self.generate_outlines_button.setText("Edit Outlines")
        else:
            self.left_info_label.setText("No Outlines Generated")
            self.generate_outlines_button.setText("Generate Outlines")


class Subpartcolourlistmodel(QAbstractTableModel):
    colour_changed = pyqtSignal()

    def __init__(self, subpart: Subpart, button_colour):
        super().__init__()
        self._data = subpart
        self._data_keys = list(subpart.colours.keys())
        self.button_colour = button_colour

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            brick_colour = self._data.colours[self._data_keys[index.row()]][0]
            if index.column() == 0:
                return brick_colour.ldrawname
            elif index.column() == 1:
                return brick_colour.colour_code
            else:
                return "Select"
        if role == Qt.ItemDataRole.ToolTipRole:
            brick_colour = self._data.colours[self._data_keys[index.row()]][0]
            if index.column() == 0:
                return f'"{brick_colour.ldrawname}"'
            elif index.column() == 1:
                return f'"{brick_colour.colour_code}"'
        if role == Qt.ItemDataRole.BackgroundRole:
            if index.column() == 0:
                brick_colour = self._data.colours[self._data_keys[index.row()]][0]
                return QColor(brick_colour.rgb_values)
            elif index.column() == 2:
                return QColor(self.button_colour)
        if role == Qt.ItemDataRole.ForegroundRole and index.column() == 0:
            brick_colour = self._data.colours[self._data_keys[index.row()]][0]
            contrastcolour = get_contrast_colour(brick_colour.rgb_values)
            return QColor(contrastcolour)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.UserRole:
            return self._data_keys[index.row()]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ["LDraw Name", "Colour Code", ""][section]

    def rowCount(self, index):
        return len(self._data.colours)

    def columnCount(self, index):
        return 3

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            if is_brickcolour(value)[0]:
                new_colour = Brickcolour(value)
                if new_colour.ldrawname == "Undefined":
                    dlg = QMessageBox(self.parent())
                    dlg.setWindowTitle("Undefined Colour")
                    dlg.setText(f'The Colour Code "{new_colour.colour_code}" is unknown\n'
                                f'Apply anyway?')
                    dlg.setIcon(QMessageBox.Icon.Warning)
                    dlg.setStandardButtons(
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    answer = dlg.exec()
                    if answer != QMessageBox.StandardButton.Yes:
                        return False

                colour_key = self.data(index, Qt.ItemDataRole.UserRole)

                self._data.apply_color(new_colour, colour_key)
                self.colour_changed.emit()
            return True

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled
        elif index.column() == 1:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        elif index.column() == 2:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def refresh_data(self):
        self.beginResetModel()
        self._data_keys = list(self._data.colours.keys())
        self.endResetModel()

if __name__ == "__main__":
    app = QApplication([])
    testfile = "Path/To/Testfile"
    testmodel = LdrawObject(testfile)

    # subpartpanel = SubpartPanel(testmodel)
    # subpartpanel.show()

    colourpanel = ColourPanel(testmodel)
    colourpanel.show()

    app.exec()
