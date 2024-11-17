import trimesh
import os
from brick_data.brickcolour import Brickcolour
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
        _, file_extension = os.path.splitext(filepath)

        scene = trimesh.load_mesh(filepath)

        if not isinstance(scene, trimesh.Scene):
            scene = trimesh.scene.scene.Scene(scene)
        if scene.units not in ["mm", "millimeter", None]:
            scene = scene.convert_units("millimeter")
        for index, geometry in scene.geometry.items():
            if isinstance(geometry.visual, trimesh.visual.texture.TextureVisuals):
                geometry.visual = geometry.visual.to_color()
            try:
                geometry.visual.face_colors
            except Exception:
                #Invalid Color Data -> can occur when loading step files
                geometry.visual.face_colors = np.ones((len(geometry.faces), 4), np.uint8)

        self.scene = scene

    def convert_to_dat_file(self, filepath):
        filename = os.path.basename(filepath)
        bricklinknumberline = ""
        if len(self.bricklinknumber) > 0:
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
