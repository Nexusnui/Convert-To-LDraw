from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlRequestJob
from PyQt6.QtCore import QBuffer, QIODevice, QUrl
from trimesh import viewer
from trimesh.scene.scene import Scene


class PreviewPanel(QWidget):

    def __init__(self, main_name: str = None, main_model: Scene = None, background_color: str = "ffffff"):
        super().__init__()
        self.main_model = main_model
        self.current_model = main_model
        self.background_color = background_color
        self.main_name = main_name
        self.main_layout = QVBoxLayout()

        self.web_view = QWebEngineView()
        self.html_handler = HtmlHandler()
        self.web_view.page().profile().installUrlSchemeHandler(b"model", self.html_handler)
        if self.main_model is not None:
            self.load_main_model()

        self.main_layout.addWidget(self.web_view)

        self.setLayout(self.main_layout)

    def load_model(self, name: str, model: Scene):
        self.current_model = model
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

# Todo: Improve scene lighting
