from PyQt6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QGroupBox,
    QPlainTextEdit,
    QPushButton
)

from PyQt6.QtGui import QClipboard


class ExceptionDialog(QDialog):
    def __init__(self, parent=None,
                 clipboard: QClipboard = None,
                 title: str = "Exception Message",
                 message: str = "An Exception occurred",
                 traceback_str: str = "No Traceback given"
                 ):
        super().__init__(parent)
        self.clipboard = clipboard
        self.setWindowTitle(title)
        main_layout = QVBoxLayout()

        # Todo: Add Warning Icon
        message_label = QLabel(message)
        main_layout.addWidget(message_label)

        traceback_area = QGroupBox("Exception Traceback")
        traceback_layout = QVBoxLayout()
        traceback_area.setLayout(traceback_layout)

        main_layout.addWidget(traceback_area)

        # Todo: Better Size
        self.traceback_content = QPlainTextEdit(traceback_str)
        self.traceback_content.setReadOnly(True)
        traceback_layout.addWidget(self.traceback_content)

        traceback_copy_button = QPushButton("Copy Traceback")
        traceback_copy_button.clicked.connect(self.copy_tracback)
        traceback_layout.addWidget(traceback_copy_button)


        accept_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        accept_box.accepted.connect(self.accept)
        main_layout.addWidget(accept_box)
        self.setLayout(main_layout)

    def copy_tracback(self):
        self.traceback_content.selectAll()
        if self.clipboard is not None:
            self.clipboard.setText(self.traceback_content.toPlainText())


if __name__ == "__main__":
    app = QApplication([])

    exc_dia = ExceptionDialog(clipboard=app.clipboard())
    exc_dia.exec()

