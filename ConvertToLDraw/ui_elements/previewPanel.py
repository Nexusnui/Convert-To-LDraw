import os
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton
)
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlRequestJob
from PyQt6.QtCore import QBuffer, QIODevice, QUrl, Qt
from trimesh import viewer
from trimesh.scene.scene import Scene

basedir = os.path.dirname(__file__).strip("ui_elements")

empty_html = ('<!DOCTYPE html>'
              '<html lang="en">'
              '<head>'
              '<title>no model</title>'
              '<meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width,user-scalable=no,minimum-scale=1.0,maximum-scale=1.0">'
              '<style>body {margin: 0px;overflow: hidden;background-color: template_color;}</style>'
              '</head>'
              '<body></body>'
              '</html>')


class PreviewPanel(QWidget):

    def __init__(self, main_name: str = None, main_model: Scene = None, background_color: str = "ffffff"):
        super().__init__()
        self.main_model = main_model
        self.current_model = main_model
        self.background_color = background_color
        self.main_name = main_name
        self.main_layout = QVBoxLayout()

        self.controls_layout = QHBoxLayout()
        reload_button = QPushButton()
        reload_button.setIcon(QIcon(os.path.join(basedir, "icons", "reload-icon.svg")))
        reload_button.clicked.connect(self.refresh_model)
        self.controls_layout.addWidget(reload_button)

        self.show_main_model_button = QPushButton("Show Main Model")
        self.show_main_model_button.clicked.connect(self.load_main_model)
        self.show_main_model_button.setDisabled(True)
        self.controls_layout.addWidget(self.show_main_model_button)

        self.main_layout.addLayout(self.controls_layout)

        self.web_view = QWebEngineView()
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.web_view.setStyleSheet(f"color: #{background_color};background-color: #{background_color};")
        self.html_handler = HtmlHandler()
        self.web_view.page().profile().installUrlSchemeHandler(b"model", self.html_handler)
        if self.main_model is not None:
            self.load_main_model()
        else:
            self.web_view.setHtml(empty_html.replace("template_color", f"#{background_color}"))

        self.main_layout.addWidget(self.web_view)

        self.setLayout(self.main_layout)

    def load_model(self, name: str, model: Scene):
        self.current_model = model
        self.show_main_model_button.setDisabled(False)
        self.refresh_model()

    def set_main_model(self, name: str, model: Scene):
        self.main_model = model

    def refresh_model(self):
        if self.current_model is not None:
            html_code = viewer.scene_to_html(self.current_model)
            html_code = html_code.replace('scene.background=new THREE.Color(0xffffff)',
                                          f'scene.background=new THREE.Color(0x{self.background_color})')
            html_code = html_code.replace('tracklight=new THREE.DirectionalLight(0xffffff,1.75)',
                                          f'tracklight=new THREE.DirectionalLight(0xffffff,3)')
            self.html_handler.set_html(html_code)
            self.web_view.load(QUrl("model://init"))

    def load_main_model(self):
        self.current_model = self.main_model
        self.show_main_model_button.setDisabled(True)
        self.refresh_model()


class HtmlHandler(QWebEngineUrlSchemeHandler):
    def __init__(self, parent= None):
        super().__init__(parent)
        self.html = ""

    def requestStarted(self, request: QWebEngineUrlRequestJob):
        buf = QBuffer(parent=self)
        request.destroyed.connect(buf.deleteLater)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        buf.write(self.html)
        buf.seek(0)
        buf.close()
        request.reply(b"text/html", buf)
        return

    def set_html(self, html: str):
        self.html = html.encode("utf-8")
