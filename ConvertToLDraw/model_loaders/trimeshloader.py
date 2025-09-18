from trimesh.scene.scene import Scene
from trimesh import load_scene
from ConvertToLDraw.model_loaders.modelloader import Modelloader


class Trimeshloader(Modelloader):
    @staticmethod
    def load_model(filepath) -> Scene:
        return load_scene(filepath)
