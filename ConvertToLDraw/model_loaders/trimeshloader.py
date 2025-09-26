from trimesh.scene.scene import Scene
from trimesh import load_scene
from ConvertToLDraw.model_loaders.modelloader import Modelloader


class Trimeshloader(Modelloader):

    def load_model(self, file) -> tuple[Scene, dict]:
        return load_scene(file), {}
