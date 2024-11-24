from brick_data.brickcolour import Brickcolour, get_contrast_colour, is_brickcolour, get_all_brickcolours
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QLineEdit, QApplication, QColorDialog, \
    QVBoxLayout, QTabWidget, QTableView

from PyQt6.QtCore import pyqtSignal, QAbstractTableModel, Qt
from PyQt6.QtGui import QColor


class BrickcolourWidget(QWidget):
    colour_changed = pyqtSignal(Brickcolour)

    def __init__(self, labeltext: str = "Brick Colour", colour: Brickcolour = Brickcolour("16")):
        super().__init__()

        self.layout = QHBoxLayout()

        self.colour = colour

        self.preview = QLineEdit()
        self.preview.setReadOnly(True)
        self.__update_preview()

        self.colourinput = QLineEdit()
        self.colourinput.setText(self.colour.colour_code)
        self.colourinput.textEdited.connect(self.changecolour)
        self.select_button = QPushButton("Select")
        self.select_button.clicked.connect(self.open_color_picker)

        self.layout.addWidget(QLabel(labeltext))
        self.layout.addWidget(self.preview)
        self.layout.addWidget(self.colourinput)
        self.layout.addWidget(self.select_button)

        self.setLayout(self.layout)

    def __update_preview(self):
        if self.colour is None:
            self.preview.setStyleSheet("background-color : black; color : white;")
            self.preview.setText("Invalid/Unknown")
            return
        if self.colour.colour_type == "LDraw":
            self.preview.setText(self.colour.ldrawname)
        elif self.colour.colour_type == "Direct":
            self.preview.setText(self.colour.colour_code)
        text_colour = get_contrast_colour(self.colour.rgb_values)
        self.preview.setStyleSheet(f"background-color : {self.colour.rgb_values}; color : {text_colour};")

    def changecolour(self, colour: str | Brickcolour, send_emit=True, set_text=False):
        if isinstance(colour, str):
            if is_brickcolour(colour)[0]:
                self.colour = Brickcolour(colour)
                if send_emit:
                    self.colour_changed.emit(self.colour)
            else:
                self.colour = None
        elif isinstance(colour, Brickcolour):
            self.colour = colour
            if send_emit:
                self.colour_changed.emit(self.colour)
        if not send_emit or set_text:
            self.colourinput.setText(self.colour.colour_code)
        self.__update_preview()

    def setDisabled(self, a0):
        self.colourinput.setDisabled(a0)
        self.select_button.setDisabled(a0)

    def open_color_picker(self):
        initial_color = Brickcolour("16")
        if self.colour is not None:
            initial_color = self.colour
        color_picker = BrickcolourDialog(initial_color)
        color_picker.accepted.connect(lambda: self.changecolour(color_picker.brickcolour, set_text=True))
        color_picker.exec()


class BrickcolourDialog(QColorDialog):
    def __init__(self, initial_color: Brickcolour = None):
        super().__init__()

        main_layout = QVBoxLayout()
        tab_widget = QTabWidget()

        # Widget for picking direct colours
        html_widget = QWidget()
        html_widget.setLayout(self.layout())

        # Widget for picking LDraw colour
        ldraw_wiget = QTableView()
        ldraw_wiget.setCornerButtonEnabled(False)

        self.bickcolourlist = Brickcolourlistmodel(get_all_brickcolours())
        ldraw_wiget.setModel(self.bickcolourlist)
        ldraw_wiget.clicked.connect(self.on_select_brickcolour)

        tab_widget.addTab(ldraw_wiget, "LDraw Color")

        tab_widget.addTab(html_widget, "Direct Colour")
        main_layout.addWidget(tab_widget)

        bottom_layout = QHBoxLayout()
        dialogbox = html_widget.children().pop()
        bottom_layout.addWidget(dialogbox)
        self.preview = QLineEdit()
        self.preview.setReadOnly(True)
        bottom_layout.addWidget(self.preview)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
        self.update_brickcolor(self.currentColor())
        self.currentColorChanged.connect(self.update_brickcolor)

        if initial_color is not None:
            self.update_brickcolor(initial_color)
        else:
            self.update_brickcolor(Brickcolour("16"))

    def update_brickcolor(self, colour):
        if isinstance(colour, QColor):
            text_colour = get_contrast_colour(colour.name())
            self.preview.setStyleSheet(f"background-color : {colour.name()}; color : {text_colour};")
            self.brickcolour = Brickcolour(colour.name())
            self.preview.setText(self.brickcolour.colour_code)
        if isinstance(colour, Brickcolour):
            text_colour = get_contrast_colour(colour.rgb_values)
            self.preview.setStyleSheet(f"background-color : {colour.rgb_values}; color : {text_colour};")
            self.brickcolour = colour
            preview_text = self.brickcolour.colour_code
            if colour.colour_type == "LDraw":
                preview_text = f"{preview_text}: {self.brickcolour.ldrawname}"
            self.preview.setText(preview_text)

    def on_select_brickcolour(self, index):
        self.update_brickcolor(self.bickcolourlist.data(index, Qt.ItemDataRole.UserRole))


class Brickcolourlistmodel(QAbstractTableModel):
    def __init__(self, colorlist):
        super().__init__()
        self._data = colorlist

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == Qt.ItemDataRole.DecorationRole and index.column() in [0,2]:
            html_color = self._data[index.row()].rgb_values
            return QColor(html_color)
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 3:
            html_color = self._data[index.row()].rgb_edge
            return QColor(html_color)
        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() in [1, 4, 5, 7]:
            return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignRight
        if role == Qt.ItemDataRole.UserRole:
            return self._data[index.row()]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:

            if orientation == Qt.Orientation.Horizontal:
                return ["LDraw Name", "Colour Code", "Value", "Edge", "Alpha", "Luminance", "Material", "Lego IDs",
                        "Lego Names", "Category"][section]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return 10


if __name__ == "__main__":
    app = QApplication([])
    colourwidget = BrickcolourWidget(colour=Brickcolour("27"))
    colourwidget.show()

    app.exec()
