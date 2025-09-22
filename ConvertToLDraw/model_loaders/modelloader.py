from trimesh.scene.scene import Scene
from abc import ABC, abstractmethod


class Modelloader(ABC):
    @staticmethod
    @abstractmethod
    def load_model(file) -> tuple[Scene, dict]:
        """
        Loader used to load a 3D model from file
        :param file:
            file to load 3D model from
            normally a filepath, could also be a file object
        :return Scene, dict:
            returns a Trimesh Scene and a dictionary with metadata values
        """
        pass
