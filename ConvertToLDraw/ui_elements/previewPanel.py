import os
import urllib.parse
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel
)
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlRequestJob, QWebEngineUrlScheme
from PyQt6.QtCore import QBuffer, QIODevice, QUrl, Qt
from ConvertToLDraw.brick_data.ldrawObject import LdrawObject, Subpart

basedir = os.path.dirname(__file__).strip("ui_elements")
template_html_path = os.path.join(os.path.dirname(__file__), "viewer_template.html")


class PreviewPanel(QWidget):

    def __init__(self, main_name: str = None, main_model: LdrawObject = None, background_color: str = "ffffff"):
        super().__init__()
        self.main_model = main_model
        self.current_model = main_model
        self.background_color = background_color
        viewer_url = QUrl.fromLocalFile(template_html_path)
        viewer_url.setUrl(f"{viewer_url.url()}?color={urllib.parse.quote(background_color)}")
        self.viewer_url = viewer_url

        self.main_name = main_name
        self.main_layout = QVBoxLayout()

        self.controls_layout = QHBoxLayout()
        reload_button = QPushButton()
        reload_button.setIcon(QIcon(os.path.join(basedir, "icons", "reload-icon.svg")))
        reload_button.clicked.connect(self.refresh_model)
        self.controls_layout.addWidget(reload_button)

        self.show_main_model_button = QPushButton("Show Main Part")
        self.show_main_model_button.clicked.connect(self.load_main_model)
        self.show_main_model_button.setDisabled(True)
        self.controls_layout.addWidget(self.show_main_model_button)

        self.status_label = QLabel("No Model Loaded")
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addLayout(self.controls_layout)

        self.web_view = QWebEngineView()
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.web_view.setStyleSheet(f"background-color: {background_color};")
        self.ldraw_handler = LDrawHandler()
        self.web_view.page().profile().installUrlSchemeHandler(b"ldraw", self.ldraw_handler)
        if self.main_model is not None:
            self.load_main_model()
        else:
            self.web_view.load(self.viewer_url)

        self.main_layout.addWidget(self.web_view)
        self.main_layout.setStretchFactor(self.web_view, 1)

        self.setLayout(self.main_layout)

    def load_subpart(self, model: Subpart):
        self.current_model = model
        self.show_main_model_button.setDisabled(False)
        self.refresh_model()

    def set_main_model(self, model: LdrawObject, refresh=False):
        self.main_model = model
        if refresh:
            self.show_main_model_button.setDisabled(True)
            self.current_model = self.main_model
            self.status_label.setText(f"Showing Main Part")
            self.refresh_model()

    def refresh_model(self):
        if self.current_model is not None:
            if isinstance(self.current_model, Subpart):
                self.status_label.setText(f"Showing Subpart: '{self.current_model.name}'")
            self.ldraw_handler.set_ldraw_file(get_ldraw_data(self.current_model))
            self.web_view.load(self.viewer_url)

    def load_main_model(self):
        self.current_model = self.main_model
        self.show_main_model_button.setDisabled(True)
        self.status_label.setText(f"Showing Main Part")
        self.refresh_model()

    def reload_model(self):
        if isinstance(self.current_model, Subpart):
            self.status_label.setText(f"Showing Subpart: '{self.current_model.name}'")
        self.ldraw_handler.set_ldraw_file(get_ldraw_data(self.current_model))
        self.web_view.page().runJavaScript("reload_ldraw_model()")


class LDrawHandler(QWebEngineUrlSchemeHandler):
    def __init__(self, parent= None):
        super().__init__(parent)
        self.file = b""

    def requestStarted(self, request: QWebEngineUrlRequestJob):
        buf = QBuffer(parent=self)
        request.destroyed.connect(buf.deleteLater)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        buf.write(self.file)
        buf.seek(0)
        buf.close()
        request.reply(b"text/plain", buf)
        return

    def set_ldraw_file(self, file: str):
        self.file = file.encode("utf-8")


def get_ldraw_data(part: LdrawObject | Subpart):
    if isinstance(part, LdrawObject):
        data = part.convert_to_dat_file()
    else:
        data = [part.get_ldraw_header("Preview", "Main Part", "", "", True)]
        code = "16"
        if not part.multicolour:
            code = part.main_colour.colour_code
        for line in part.to_ldraw_lines(code):
            data.append(line)
        data = "".join(data)
    return data


def register_scheme():
    scheme = QWebEngineUrlScheme(b"ldraw")
    scheme.setFlags(
        QWebEngineUrlScheme.Flag.LocalScheme |
        QWebEngineUrlScheme.Flag.SecureScheme |
        QWebEngineUrlScheme.Flag.LocalAccessAllowed |
        QWebEngineUrlScheme.Flag.ViewSourceAllowed |
        QWebEngineUrlScheme.Flag.ContentSecurityPolicyIgnored |
        QWebEngineUrlScheme.Flag.CorsEnabled |
        QWebEngineUrlScheme.Flag.FetchApiAllowed
    )
    scheme.setSyntax(QWebEngineUrlScheme.Syntax.Path)
    scheme.setDefaultPort(80)
    QWebEngineUrlScheme.registerScheme(scheme)
