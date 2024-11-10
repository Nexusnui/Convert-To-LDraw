from brick_data.brickcolour import Brickcolour, get_contrast_colour, is_brickcolour
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QLineEdit, QApplication

class BrickcolourWidget(QWidget):
    def __init__(self, labeltext: str = "Brick Colour", colour: Brickcolour = Brickcolour("16")):
        super().__init__()

        self.layout = QHBoxLayout()

        self.colour = colour

        self.preview = QLineEdit()
        self.preview.setReadOnly(True)
        self.__update_preview()

        self.colourinput = QLineEdit()
        self.colourinput.setText(self.colour.colour_code)
        self.colourinput.textChanged.connect(self.changecolour)
        selectbutton = QPushButton("Select")
        #Todo connect to color dialog

        self.layout.addWidget(QLabel(labeltext))
        self.layout.addWidget(self.preview)
        self.layout.addWidget(self.colourinput)
        self.layout.addWidget(selectbutton)

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

    def changecolour(self, colour: str | Brickcolour):
        if isinstance(colour, str):
            if is_brickcolour(colour):
                self.colour = Brickcolour(colour)
            else:
                self.colour = None
        elif isinstance(colour, Brickcolour):
            self.colour = colour
        self.__update_preview()


#Todo: Add Colordialog

if __name__ == "__main__":
    app = QApplication([])
    colourwidget = BrickcolourWidget(colour=Brickcolour("27"))
    colourwidget.show()

    app.exec()
