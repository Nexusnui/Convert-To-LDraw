from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from PyQt6.QtWebEngineWidgets import QWebEngineView
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
        if self.main_model is not None:
            self.load_main_model()

        self.main_layout.addWidget(self.web_view)

        self.setLayout(self.main_layout)
        print("panel: ", __file__)

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
            print(len(html_code))
            self.web_view.setHtml(html_code)

    def load_main_model(self):
        self.current_model = self.main_model
        self.refresh_model()

# Todo: Improve scene lighting
