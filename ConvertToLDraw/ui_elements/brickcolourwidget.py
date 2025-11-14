import math

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
    QTreeView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QSpinBox,
    QSlider
)

from PyQt6.QtCore import Qt, pyqtSignal, QAbstractTableModel, QAbstractItemModel, QModelIndex, QMimeData, QByteArray
from PyQt6.QtGui import QColor

from collections import OrderedDict

from numpy import array_split

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
        self.colourslistmodel = BrickcolourListmodel(self.all_colours)
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


class BrickcolourListmodel(QAbstractTableModel):
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


class SplitColourDialog(QDialog):
    def __init__(self, colours: OrderedDict, has_outlines: bool = False):
        super().__init__()
        self.input_colours = colours
        self.has_outlines = has_outlines
        self.item_count = len(colours) + int(self.has_outlines)
        self.colour_groups = None

        self.setWindowTitle("Split Subpart by Colours")
        self.main_layout = QVBoxLayout()

        self.number_label = QLabel("Choose the number of groups to split into:\n"
                                   "(Groups can be added/removed in the next step)")
        self.main_layout.addWidget(self.number_label)

        self.number_input = QSpinBox()
        self.number_input.setRange(2, self.item_count)
        self.number_input.setSingleStep(1)
        self.main_layout.addWidget(self.number_input)

        self.number_slider = QSlider(Qt.Orientation.Horizontal)
        self.number_slider.setRange(2, self.item_count)
        self.number_slider.setSingleStep(1)
        self.number_slider.setPageStep(1)
        self.number_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.number_slider.valueChanged.connect(self.number_input.setValue)
        self.number_input.valueChanged.connect(self.number_slider.setValue)
        self.main_layout.addWidget(self.number_slider)

        if self.has_outlines:
            self.item_count_label = QLabel(f"There are {len(self.input_colours)} colours + outlines")
        else:
            self.item_count_label = QLabel(f"There are {len(self.input_colours)} colours")
        self.main_layout.addWidget(self.item_count_label)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.number_button_box = QDialogButtonBox(buttons)
        self.number_button_box.buttons()[0].setText("Next")
        self.number_button_box.accepted.connect(self.show_colours)
        self.number_button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.number_button_box)
        self.splitcoloursmodel = None
        self.splitview = None
        self.setLayout(self.main_layout)

    def show_colours(self):
        splits = self.number_input.value()
        self.main_layout.removeWidget(self.number_label)
        self.main_layout.removeWidget(self.number_input)
        self.main_layout.removeWidget(self.number_slider)
        self.main_layout.removeWidget(self.item_count_label)
        self.main_layout.removeWidget(self.number_button_box)
        self.number_label.deleteLater()
        self.number_input.deleteLater()
        self.number_slider.deleteLater()
        self.item_count_label.deleteLater()
        self.number_button_box.deleteLater()
        self.splitcoloursmodel = SplitColourTreemodel(self.input_colours, self.has_outlines, splits)
        self.splitview = QTreeView()
        self.main_layout.addWidget(self.splitview)
        self.splitview.setModel(self.splitcoloursmodel)
        self.splitview.expandAll()
        self.splitview.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.splitview.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.splitcoloursmodel.modelReset.connect(self.rows_moved)

        group_button_layout = QHBoxLayout()

        self.add_group_button = QPushButton("+Add Group")
        self.add_group_button.clicked.connect(lambda: self.splitcoloursmodel.add_groups())
        group_button_layout.addWidget(self.add_group_button)

        self.remove_empty_groups_button = QPushButton("-Remove Empty Groups")
        self.remove_empty_groups_button.clicked.connect(self.splitcoloursmodel.remove_empty_groups)
        group_button_layout.addWidget(self.remove_empty_groups_button)

        self.remove_empty_groups_button.setDisabled(True)
        if splits == self.item_count:
            self.add_group_button.setDisabled(True)

        self.main_layout.addLayout(group_button_layout)

        self.splitcoloursmodel.modelChanged.connect(self.on_model_updated)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.dialog_accepted)
        button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(button_box)

        header_height = self.splitview.header().size().height()
        row_height = self.splitview.rowHeight(self.splitcoloursmodel.index(0, 0))
        new_height = row_height * (self.item_count + splits + 1) + header_height
        max_height = int(math.floor(self.screen().size().height()*3/5))
        self.splitview.setMinimumHeight(min(new_height, max_height))

    def rows_moved(self):
        self.splitview.expandAll()

    def dialog_accepted(self):
        self.colour_groups = self.splitcoloursmodel.get_data()
        self.accept()

    def on_model_updated(self, group_count: int, has_empty_groups: bool):
        self.add_group_button.setDisabled(group_count >= self.item_count)
        self.remove_empty_groups_button.setEnabled(has_empty_groups)


class SplitColourTreemodel(QAbstractItemModel):
    modelChanged = pyqtSignal(int, bool)  # groupcount, has empty groups

    def __init__(self, colours: OrderedDict, has_outlines: bool = False, splits: int = 2):
        super().__init__()
        self.colours = colours
        colour_keys = list(colours.keys())
        if has_outlines:
            colour_keys.append("outlines")

        # Creates a list containing lists of colour keys
        self._data = [arr.tolist() for arr in array_split(colour_keys, splits)]
        self.pointers = []

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()):
        if parent.isValid():
            if parent.internalPointer()[1] is None:
                pointer = (parent.internalPointer()[0], row)
                if pointer in self.pointers:
                    pointer = self.pointers[self.pointers.index(pointer)]
                else:
                    self.pointers.append(pointer)
                return self.createIndex(row, 0, pointer)
            else:
                raise NotImplementedError(f"index requested:\n"
                                          f"row: {row}\n"
                                          f"Parent Internal Pointer {parent.internalPointer()}")
        else:
            pointer = (row, None)
            if pointer in self.pointers:
                pointer = self.pointers[self.pointers.index(pointer)]
            else:
                self.pointers.append(pointer)
            return self.createIndex(row, 0, pointer)

    def parent(self, index):
        if index.isValid:
            if index.internalPointer()[1] is None:
                return QModelIndex()
            else:
                pointer = self.pointers[self.pointers.index((index.internalPointer()[0], None))]
                return self.createIndex(pointer[0], 0, pointer)
        else:
            return QModelIndex()

    def rowCount(self, index: QModelIndex = QModelIndex()):
        if index.isValid():
            if index.internalPointer()[1] is None:
                return len(self._data[index.internalPointer()[0]])
            else:
                return 0
        else:
            return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return 1

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            if index.internalPointer()[1] is None:
                return f"Group {index.internalPointer()[0]+1}"
            else:
                colour_index = self._data[index.internalPointer()[0]][index.internalPointer()[1]]
                if colour_index != "outlines":
                    return str(self.colours[colour_index][0])
                else:
                    return "Outlines"
        elif role == Qt.ItemDataRole.BackgroundRole:
            if index.internalPointer()[1] is not None:
                colour_index = self._data[index.internalPointer()[0]][index.internalPointer()[1]]
                if colour_index != "outlines":
                    brick_colour: Brickcolour = self.colours[colour_index][0]
                    return QColor(brick_colour.rgb_values)
                else:
                    return QColor(Brickcolour("24").rgb_values)
        elif role == Qt.ItemDataRole.ForegroundRole:

            if index.internalPointer()[1] is not None:
                colour_index = self._data[index.internalPointer()[0]][index.internalPointer()[1]]
                if colour_index != "outlines":
                    brick_colour: Brickcolour = self.colours[colour_index][0]
                    return QColor(get_contrast_colour(brick_colour.rgb_values))
                else:
                    return QColor(get_contrast_colour(Brickcolour("24").rgb_values))

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return "Colour Groups"

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def flags(self, index: QModelIndex):
        if index.isValid():
            if index.internalPointer()[1] is None:
                return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsDropEnabled
            else:
                return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | \
                    Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsUserCheckable
        return Qt.ItemFlag.ItemIsEnabled

    def mimeTypes(self):
        return ['text/plain', "custom/indices"]

    def mimeData(self, indexes):
        indexes.sort(key=lambda e: e.internalPointer())
        data = []
        for index in indexes:
            data.append(f"{index.internalPointer()[0]},{index.internalPointer()[1]}")
        data_text = ";".join(data)
        mimedata = QMimeData()
        mimedata.setText(data_text)
        return mimedata

    def dropMimeData(self, data, action, row, column, parent):
        # Rebuilt 'move from' pointers from string
        from_pointers = [tuple(int(idx_str) for idx_str in ptr_str.split(",")) for ptr_str in data.text().split(";")]
        if row > 0:
            upper_item = self._data[parent.internalPointer()[0]][row-1]
        values = [self._data[ptr[0]][ptr[1]] for ptr in from_pointers]
        from_pointers.reverse()
        for ptr in from_pointers:
            self._data[ptr[0]].pop(ptr[1])
        if row > 0:
            insert_index = self._data[parent.internalPointer()[0]].index(upper_item) + 1
            self._data[parent.internalPointer()[0]][insert_index:insert_index] = values
        elif row == 0:
            self._data[parent.internalPointer()[0]][0:0] = values
        else:
            self._data[parent.internalPointer()[0]].extend(values)
        self.update_model()
        return True

    def add_groups(self, count: int = 1):
        for i in range(count):
            self._data.append([])
        self.update_model()

    def remove_empty_groups(self):
        indexes = []
        for index, group in enumerate(self._data):
            if len(group) == 0:
                indexes.append(index)
        indexes.reverse()
        for index in indexes:
            self._data.pop(index)
        self.update_model()

    def update_model(self):
        group_count = len(self._data)
        has_empty_groups = False
        for group in self._data:
            if len(group) == 0:
                has_empty_groups = True
                break
        self.modelChanged.emit(group_count, has_empty_groups)
        self.beginResetModel()
        self.endResetModel()

    def get_data(self):
        return self._data


if __name__ == "__main__":
    app = QApplication([])
    colourwidget = BrickcolourWidget(colour=Brickcolour("27"))
    colourwidget.show()

    app.exec()

    colour_cat_dia = ColourCategoriesDialog()
    colour_cat_dia.exec()
    print(colour_cat_dia.get_selected_items())
