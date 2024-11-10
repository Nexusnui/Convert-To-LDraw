import trimesh
import os
from src.brick_data.brickcolour import Brickcolour
import numpy as np

class LdrawObject:
    def __init__(self, filepath: str, name="", bricklinknumber="", author=""):
        self.__load_scene(filepath)
        self.scene.apply_scale(2.5)
        self.name = name
        self.bricklinknumber = bricklinknumber
        self.author = author
        self.set_main_colour(Brickcolour("16"))

    def __load_scene(self, filepath):
        scene = trimesh.load_mesh(filepath)
        if not isinstance(scene, trimesh.Scene):
            scene = trimesh.scene.scene.Scene(scene)
        self.scene = scene

    def convert_to_dat_file(self, filepath):
        filename = os.path.basename(filepath)
        bricklinknumberline = ""
        if len(self.bricklinknumber>0):
            bricklinknumberline = f"0 BL_Item_No {self.bricklinknumber}\n"
        header = (f"0 FILE {filename}\n"
                  f"0 {self.name}\n"
                  f"0 Name:  {filename}\n"
                  f"0 Author:  {self.author}\n"
                  f"{bricklinknumberline}"
                  f"0 BFC CERTIFY CCW\n")
        part = self.scene.to_geometry()
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(header)
            for face in part.faces:  # faces vertices
                coordinate_a = ' '.join(map(str, part.vertices[face[0]]))
                coordinate_b = ' '.join(map(str, part.vertices[face[1]]))
                coordinate_c = ' '.join(map(str, part.vertices[face[2]]))
                file.write(f"3 {self.main_colour.colour_code} {coordinate_a} {coordinate_b} {coordinate_c}\n")

    def set_main_colour(self, colour: Brickcolour):
        self.main_colour = colour
        for id, geometry in self.scene.geometry.items():
            geometry.visual.face_colors[0:] = np.array(self.main_colour.get_int_rgba())
