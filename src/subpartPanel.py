from PyQt6.QtCore import pyqtSignal, QAbstractTableModel, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QTabWidget,
    QWidget,
    QApplication,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QTableView
)

from brick_data.ldrawObject import LdrawObject, Subpart
from brick_data.brickcolour import Brickcolour, is_brickcolour
from brickcolourwidget import BrickcolourWidget, BrickcolourDialog

class SubpartPanel(QTabWidget):
    def __init__(self, mainmodel: LdrawObject):
        super().__init__()

        for sp in mainmodel.subparts.values():
            self.__add_tab(sp)

    def __add_tab(self, subpart: Subpart):
        tab = SubpartTab(subpart)
        index = self.addTab(tab, subpart.name)
        tab.name_changed.connect(lambda name: self.setTabText(index, name))

    def setDisabled(self, value: bool):
        self.currentWidget().setDisabled(value)
        self.tabBar().setDisabled(value)


class ColourPanel(QWidget):
    def __init__(self, mainmodel: LdrawObject):
        super().__init__()
        mainlayout = QVBoxLayout()
        self.setLayout(mainlayout)
        subpart = list(mainmodel.subparts.items())[0][1]
        mainlayout.addWidget(SubpartTab(subpart, single_part=True))

class SubpartTab(QWidget):
    name_changed = pyqtSignal(str)
    def __init__(self, subpart: Subpart, single_part=False):
        super().__init__()
        self.subpart = subpart

        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)

    # Main Settings Area
        self.main_settings = QFormLayout()

        #Name Input
        if not single_part:
            self.name_line = QLineEdit()
            self.name_line.setText(self.subpart.name)
            self.main_settings.addRow("Name", self.name_line)
            self.name_line.textChanged.connect(self.apply_name_change)

        #Override / Set Colour

        if self.subpart.multicolour:
            main_colour_text = "Override Colours"
            brick_colour = Brickcolour("16")
        else:
            main_colour_text = "Subpart Colour"
            brick_colour = self.subpart.main_colour
        self.main_colour_input = BrickcolourWidget(main_colour_text, brick_colour)
        self.main_settings.addRow(self.main_colour_input)
        if self.subpart.multicolour:
            self.apply_colour_button = QPushButton("Apply Colour")
            self.apply_colour_button.clicked.connect(self.apply_main_colour)
            self.main_settings.addRow(self.apply_colour_button)
            self.multicolour_widget = QTableView()
            self.multicolour_widget.setCornerButtonEnabled(False)
            self.subpartcolourlist = Subpartcolourlistmodel(self.subpart)
            self.multicolour_widget.setModel(self.subpartcolourlist)
            self.multicolour_widget.clicked.connect(self._on_select_brickcolour)
            self.multicolour_widget.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.multicolour_widget.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        else:
            self.main_colour_input.colour_changed.connect(self.apply_main_colour)


    # Add Elements to Main Layout
        self.mainlayout.addLayout(self.main_settings)
        if self.subpart.multicolour:
            #self.mainlayout.addWidget(self.colour_scroll)
            self.mainlayout.addWidget(self.multicolour_widget)


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
                self.subpart.multicolour = False
                self.mainlayout.removeWidget(self.multicolour_widget)
                self.multicolour_widget.deleteLater()
                self.main_colour_input.colour_changed.connect(self.apply_main_colour)
                self.main_settings.removeWidget(self.apply_colour_button)
                self.apply_colour_button.deleteLater()
                self.main_colour_input.label.setText("Subpart Colour")
            else:
                self.setDisabled(False)
                return
        elif colour is None:
            print("Invalid Colour")
            return
        self.subpart.apply_color(colour)
        self.setDisabled(False)

    def _on_select_brickcolour(self, index):
        if index.column() in [0, 2]:
            self.multicolour_widget.clearSelection()
        if index.column() == 2:
            colour_key = self.subpartcolourlist.data(index, Qt.ItemDataRole.UserRole)
            initial_color = self.subpart.colours[colour_key][0]
            color_picker = BrickcolourDialog(initial_color)
            color_picker.accepted.connect(lambda: self.changecolour(color_picker.brickcolour, colour_key))
            color_picker.exec()
    def changecolour(self, colour: Brickcolour, key):
        self.subpart.apply_color(colour, key)

class Subpartcolourlistmodel(QAbstractTableModel):
    def __init__(self, subpart: Subpart):
        super().__init__()
        self._data = subpart

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            brick_colour = list(self._data.colours.values())[index.row()][0]
            if index.column() == 0:
                return brick_colour.ldrawname
            elif index.column() == 1:
                return brick_colour.colour_code
            else:
                return "Select"
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            brick_colour = list(self._data.colours.values())[index.row()][0]
            return QColor(brick_colour.rgb_values)
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 2:
            html_color = "#FFFFFF"
            # Todo: Correct Select Button Colour/Style
            return QColor(html_color)
        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() == 1:
            return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignRight
        if role == Qt.ItemDataRole.UserRole:
            return list(self._data.colours.items())[index.row()][0]

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
            print(value)
            if is_brickcolour(value):
                colour_key = self.data(index, Qt.ItemDataRole.UserRole)
                new_colour = Brickcolour(value)
                self._data.apply_color(new_colour, colour_key)
                # Todo: Warning for undefiened colour codes
            return True

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled
        elif index.column() == 1:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        elif index.column() == 2:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


if __name__ == "__main__":
    app = QApplication([])
    testfile = "Path/To/Testfile"
    testmodel = LdrawObject(testfile)

    #subpartpanel = SubpartPanel(testmodel)
    #subpartpanel.show()

    colourpanel = ColourPanel(testmodel)
    colourpanel.show()

    app.exec()
