from trimesh.scene.scene import Scene
from ConvertToLDraw.model_loaders.modelloader import Modelloader
from pyassimp import load

class Assimploader(Modelloader):
    @staticmethod
    def load_model(filepath) -> Scene:
        with load(filepath) as loadedmodel:
            # Todo: create return scene
            for mesh in loadedmodel.meshes:
                # Todo: Add Mesh/Vertices to Scene
                if len(mesh.colors) > 0:
                    pass #Todo: Model has colors
                elif len(mesh.materials) > 1:
                    pass #Todo: Multiple Materials used
                elif len(mesh.materials) > 1:
                    pass #Todo: One Material used
