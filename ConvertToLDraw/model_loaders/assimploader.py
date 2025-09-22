from trimesh.scene.scene import Scene
from trimesh.base import Trimesh
from ConvertToLDraw.model_loaders.modelloader import Modelloader
from pyassimp import load


class Assimploader(Modelloader):
    @staticmethod
    def load_model(filepath) -> tuple[Scene, dict]:
        model = Scene()
        with load(filepath) as loadedmodel:
            #Todo: Update this when multimaterial objects can be processed
            #Todo: Traverse through nodes alternativly?
            #Todo: Get Object Name and Transformation matrix

            for node in loadedmodel.rootnode.children:
                print(node)
            for mesh in loadedmodel.meshes:
                geometry = Trimesh(vertices=mesh.vertices, faces=mesh.faces)
                if len(mesh.colors) > 0:
                    pass  # Todo: Model has colors
                else:
                    pass  # Todo: Color from Material
                model.add_geometry(geometry)

            geometry.apply_transform()
        return model, {}
