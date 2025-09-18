from trimesh import scene
from abc import ABC, abstractmethod


class Modelloader(ABC):
    @abstractmethod
    def load_model(self, filepath) -> scene:
        pass
