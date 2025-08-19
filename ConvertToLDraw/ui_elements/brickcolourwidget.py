from ConvertToLDraw.brick_data.brickcolour import (
    Brickcolour,
    get_contrast_colour,
    is_brickcolour,
    get_all_brickcolours,
    search_brickcolour_by_rgb_colour,
    search_by_color_name
)

from ConvertToLDraw.brick_data.colour_categories import colour_categories

from colorpicker import ColorPicker

from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QApplication,
    QVBoxLayout,
    QTabWidget,
    QTableView,
    QHeaderView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem
)

from PyQt6.QtCore import pyqtSignal, QAbstractTableModel, Qt
from PyQt6.QtGui import QColor

import re


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

        self.label = QLabel(labeltext)
        self.layout.addWidget(self.label)
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


class BrickcolourDialog(QDialog):

    def __init__(self, initial_colour: Brickcolour = None, start_in_direct_mode: bool = False):
        super().__init__()
        self.setWindowTitle("Select LDraw Colour")
        # Todo: Better Initial Size

        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        # Widget for picking direct colours
        self.direct_color_widget = ColorPicker()

        # Widget for picking LDraw colour
        ldraw_wigdet = QWidget()
        ldraw_wigdet_layout = QVBoxLayout()
        ldraw_wigdet.setLayout(ldraw_wigdet_layout)

        search_inputs = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("LDraw or Lego Name")
        self.search_bar.textChanged.connect(self.search)
        search_inputs.addWidget(self.search_bar)

        clear_button = QPushButton("🗑️")
        clear_button.clicked.connect(self.search_bar.clear)
        clear_button.setStyleSheet("color: white; background-color: red;")
        search_inputs.addWidget(clear_button)

        self.search_category_input = QComboBox()
        self.search_category_input.addItems(["Name", "Colour Values"])
        self.search_category_input.currentIndexChanged.connect(self.update_search_bar)
        search_inputs.addWidget(self.search_category_input)

        ldraw_wigdet_layout.addLayout(search_inputs)

        self.ldraw_colour_table = QTableView()
        self.ldraw_colour_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.ldraw_colour_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.ldraw_colour_table.setCornerButtonEnabled(False)

        self.all_colours = get_all_brickcolours()
        self.colourslistmodel = Brickcolourlistmodel(self.all_colours)
        self.ldraw_colour_table.setModel(self.colourslistmodel)
        self.ldraw_colour_table.clicked.connect(self.on_select_brickcolour)
        self.ldraw_colour_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.ldraw_colour_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.ldraw_colour_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.ldraw_colour_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.ldraw_colour_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.ldraw_colour_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.ldraw_colour_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.ldraw_colour_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.Stretch)
        ldraw_wigdet_layout.addWidget(self.ldraw_colour_table)
        colunm_wdith = self.ldraw_colour_table.horizontalHeader().sectionSize(0)
        row_height = self.ldraw_colour_table.verticalHeader().sectionSize(0)
        new_width = int(colunm_wdith*2.5)
        new_height = row_height*6
        self.ldraw_colour_table.setMinimumSize(new_width, new_height)

        self.tab_widget.addTab(ldraw_wigdet, "LDraw Color")

        self.tab_widget.addTab(self.direct_color_widget, "Direct Colour")
        main_layout.addWidget(self.tab_widget)
        if start_in_direct_mode:
            self.tab_widget.setCurrentIndex(1)

        bottom_layout = QHBoxLayout()
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        bottom_layout.addWidget(button_box)
        self.preview = QLineEdit()
        self.preview.setReadOnly(True)
        bottom_layout.addWidget(self.preview)
        simular_colour_button = QPushButton("Show Simular Colours")
        simular_colour_button.clicked.connect(self.show_simular_colours)
        bottom_layout.addWidget(simular_colour_button)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
        self.direct_color_widget.colorChanged.connect(self.update_brickcolor)

        if initial_colour is not None:
            self.update_brickcolor(initial_colour)
        else:
            self.update_brickcolor(Brickcolour("16"))

    def update_brickcolor(self, colour):
        if isinstance(colour, QColor):
            text_colour = get_contrast_colour(colour.name())
            self.preview.setStyleSheet(f"background-color : {colour.name()}; color : {text_colour};")
            self.brickcolour = Brickcolour(colour.name())
            self.preview.setText(self.brickcolour.colour_code)
        if isinstance(colour, Brickcolour):
            self.direct_color_widget.setHex(colour.rgb_values[1:])
            text_colour = get_contrast_colour(colour.rgb_values)
            self.preview.setStyleSheet(f"background-color : {colour.rgb_values}; color : {text_colour};")
            self.brickcolour = colour
            preview_text = self.brickcolour.colour_code
            if colour.colour_type == "LDraw":
                preview_text = f"{preview_text}: {self.brickcolour.ldrawname}"
            self.preview.setText(preview_text)

    def on_select_brickcolour(self, index):
        self.update_brickcolor(self.colourslistmodel.data(index, Qt.ItemDataRole.UserRole))

    def search(self, text: str):
        search_type = self.search_category_input.currentIndex()
        if len(text) == 0:
            self.reset_colours()
        elif search_type == 0:
            search_results = search_by_color_name(text, self.all_colours)
            self.colourslistmodel.updateData(search_results)
        elif search_type == 1:
            if re.search('^#[a-f,A-F,0-9]{6}$', text):
                search_brickcolour_by_rgb_colour(text, self.all_colours)
                self.colourslistmodel.updateData()

    def update_search_bar(self, value):
        self.reset_colours()
        if value == 0:
            self.search_bar.setPlaceholderText("LDraw or Lego Name")
        else:
            self.search_bar.setPlaceholderText("Enter HTML Colour like:#D67923")
        if len(self.search_bar.text()) > 0:
            print(self.search_bar.text())
            self.search(self.search_bar.text())

    def reset_colours(self):
        self.all_colours = get_all_brickcolours()
        self.colourslistmodel.updateData(self.all_colours)

    def show_simular_colours(self):
        self.search_bar.setText(self.brickcolour.rgb_values)
        self.search_category_input.setCurrentIndex(1)
        self.update_search_bar(1)
        self.tab_widget.setCurrentIndex(0)


class Brickcolourlistmodel(QAbstractTableModel):
    def __init__(self, colorlist):
        super().__init__()
        self._data = colorlist

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 9:
                return self._data[index.row()][index.column()].split(":")[1]
            else:
                return self._data[index.row()][index.column()]
        if role == Qt.ItemDataRole.DecorationRole and index.column() in [0, 2]:
            html_color = self._data[index.row()].rgb_values
            return QColor(html_color)
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 3:
            html_color = self._data[index.row()].rgb_edge
            return QColor(html_color)
        if role == Qt.ItemDataRole.BackgroundRole:
            if index.column() == 9 or index.column() == 1:
                colour_vendor = self._data[index.row()][9].split(":")[0]
                if colour_vendor == "LDraw":
                    return QColor("#B40000")
                else:
                    return QColor("#FAC80A")
        if role == Qt.ItemDataRole.ForegroundRole:
            if index.column() == 9:
                colour_vendor = self._data[index.row()][9].split(":")[0]
                if colour_vendor == "LDraw":
                    return QColor("#ffffff")
                else:
                    return QColor("#000000")
        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() in [1, 4, 5, 7]:
            return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignRight
        if role == Qt.ItemDataRole.UserRole:
            return self._data[index.row()]
        if role == Qt.ItemDataRole.ToolTipRole:
            value = self._data[index.row()][index.column()]
            if value is not None and len(value) > 0:
                return f'"{value}"'

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

    def updateData(self, data=None):
        self.beginResetModel()
        if data is not None:
            self._data = data
        self.endResetModel()


class ColourCategoriesDialog(QDialog):
    def __init__(self, parent=None,
                 title: str = "Colour Categories", message: str = "Select Colour Categories",
                 buttons=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()

        self.setWindowTitle(title)

        message_label = QLabel(message)
        self.list_widget = QListWidget()
        self.items = []
        for category in colour_categories:
            item = QListWidgetItem(category)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            self.list_widget.addItem(item)
            self.items.append(item)

        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.check_all_items)

        if buttons is None:
            buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout.addWidget(message_label)
        main_layout.addWidget(self.list_widget)
        main_layout.addWidget(select_all_button)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def get_selected_items(self):
        selected_items = []
        for item in self.items:
            if item.checkState() == Qt.CheckState.Checked:
                selected_items.append(item.text())
        return selected_items

    def check_all_items(self):
        for item in self.items:
            item.setCheckState(Qt.CheckState.Checked)


if __name__ == "__main__":
    app = QApplication([])
    colourwidget = BrickcolourWidget(colour=Brickcolour("27"))
    colourwidget.show()

    app.exec()

    colour_cat_dia = ColourCategoriesDialog()
    colour_cat_dia.exec()
    print(colour_cat_dia.get_selected_items())
