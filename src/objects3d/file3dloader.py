import trimesh
from src.objects3d.ldrawObject import ldraw_object
#Todo:Add function load 3D files

def load_3D_file(filepath, **kwargs) -> ldraw_object:
    scene = trimesh.load_mesh(filepath)
    if type(scene) != trimesh.Scene:
        scene = trimesh.scene.scene.Scene(scene)
    return ldraw_object(scene, **kwargs)