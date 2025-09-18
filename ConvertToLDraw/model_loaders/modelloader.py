from trimesh.scene.scene import Scene
from abc import ABC, abstractmethod


class Modelloader(ABC):
    @staticmethod
    @abstractmethod
    def load_model(filepath) -> Scene:
        pass
