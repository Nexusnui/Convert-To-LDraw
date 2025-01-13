from PyQt6.QtWidgets import (
    QTabWidget,
    QWidget,
    QApplication,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
)

from brick_data.ldrawObject import LdrawObject, Subpart
from brick_data.brickcolour import Brickcolour
from brickcolourwidget import BrickcolourWidget

class SubpartPanel(QTabWidget):
    def __init__(self, mainmodel: LdrawObject):
        super().__init__()

        for sp in mainmodel.subparts.values():
            self.__add_tab(sp)

    def __add_tab(self, subpart: Subpart):
        tab = SubpartTab(subpart)
        self.addTab(tab, subpart.name)

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
    def __init__(self, subpart: Subpart, single_part=False):
        super().__init__()
        self.subpart = subpart

        mainlayout = QVBoxLayout()
        self.setLayout(mainlayout)

    # Main Settings Area
        main_settings = QFormLayout()

        #Name Input
        if not single_part:
            self.name_line = QLineEdit()
            self.name_line.setText(self.subpart.name)
            main_settings.addRow("Name", self.name_line)
            # Todo: Connect Name Change

        #Override / Set Colour

        if self.subpart.multicolour:
            main_colour_text = "Override Colours"
            brick_colour = Brickcolour("16")
        else:
            main_colour_text = "Subpart Colour"
            brick_colour = self.subpart.main_colour
        self.main_colour_input = BrickcolourWidget(main_colour_text, brick_colour)
        main_settings.addRow(self.main_colour_input)
        if self.subpart.multicolour:
            self.apply_color_button = QPushButton("Apply Colour")
            self.apply_color_button.clicked.connect(self.apply_main_colour)
            main_settings.addRow(self.apply_color_button)
        else:
            pass
            # Todo: Connect Colour Signal to apply colour

        # Todo: Add Multicolour Settings

    # Add Elements to Main Layout
        mainlayout.addLayout(main_settings)

    def apply_main_colour(self):
        print("Apply Colour")
        # Todo: Apply Colour
        # Todo: Check if valid Colour
        # Todo: Warning if multicolour


if __name__ == "__main__":
    app = QApplication([])
    testfile = "Path/To/Testfile"
    testmodel = LdrawObject(testfile)

    #subpartpanel = SubpartPanel(testmodel)
    #subpartpanel.show()

    colourpanel = ColourPanel(testmodel)
    colourpanel.show()

    app.exec()
