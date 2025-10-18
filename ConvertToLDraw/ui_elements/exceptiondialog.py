from PyQt6.QtWidgets import (
    QHBoxLayout,
    QApplication,
    QVBoxLayout,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QGroupBox,
)


class ExceptionDialog(QDialog):
    def __init__(self, parent=None,
                 title: str = "Exception Message",
                 message: str = "An Exception occurred",
                 traceback_str: str = "No Traceback given"
                 ):
        super().__init__(parent)
        self.setWindowTitle(title)
        main_layout = QVBoxLayout()

        # Todo: Add Warning Icon
        message_label = QLabel(message)
        main_layout.addWidget(message_label)

        traceback_area = QGroupBox("Exception Traceback")
        traceback_layout = QVBoxLayout()
        traceback_area.setLayout(traceback_layout)

        main_layout.addWidget(traceback_area)

        # Todo: Scrollable and copyable traceback
        traceback_content = QLabel(traceback_str)
        traceback_layout.addWidget(traceback_content)
        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication([])

    line_dia = ExceptionDialog()
    line_dia.exec()

