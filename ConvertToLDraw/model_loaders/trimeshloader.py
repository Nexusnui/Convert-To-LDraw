from trimesh import scene
from trimesh import load_scene
from ConvertToLDraw.model_loaders.modelloader import Modelloader


class Trimeshloader(Modelloader):
    def load_model(self, filepath) -> scene:
        return load_scene(filepath)
