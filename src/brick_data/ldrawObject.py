import trimesh
import trimesh.visual.material
import os
from src.brick_data.brickcolour import Brickcolour
import numpy as np
from collections import OrderedDict


class LdrawObject:
    def __init__(self, filepath: str, name="", bricklinknumber="", author=""):
        self.__load_scene(filepath)
        self.scene.apply_scale(2.5)
        self.name = name
        self.bricklinknumber = bricklinknumber
        self.author = author

    def __load_scene(self, filepath):
        _, file_extension = os.path.splitext(filepath)

        scene = trimesh.load_mesh(filepath)

        if not isinstance(scene, trimesh.Scene):
            scene = trimesh.scene.scene.Scene(scene)

        elif len(scene.geometry) == 1:
            scene = trimesh.scene.scene.Scene(scene.to_mesh())
        if scene.units not in ["mm", "millimeter", None]:
            scene = scene.convert_units("millimeter")
        self.subparts = OrderedDict()

        scene_graph = scene.graph.transforms
        for node in scene_graph.nodes:
            key = None
            if node != "world":
                if "geometry" in scene_graph.node_data[node]:
                    key = scene_graph.node_data[node]["geometry"]
            if key is not None:
                geometry = scene.geometry[key]
                main_colour = None
                if isinstance(geometry.visual, trimesh.visual.texture.TextureVisuals):
                    main_colour = geometry.visual.material.main_color
                    geometry.visual = geometry.visual.to_color()
                try:
                    geometry.visual.face_colors
                except Exception:
                    # Invalid Color Data -> can occur when loading step files
                    geometry.visual.face_colors = np.ones((len(geometry.faces), 4), np.uint8)
                transformation_matrix = scene_graph.edge_data[("world", node)]["matrix"]
                self.subparts[key] = Subpart(geometry, transformation_matrix, key, main_colour)
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
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(header)
            if len(self.subparts) == 1:
                for line in list(self.subparts.values())[0].to_ldraw_lines():
                    file.write(line)
            else:
                pass
                # Todo: Save Subparts

    def set_main_colour(self, colour: Brickcolour):
        self.main_colour = colour
        for part in self.subparts.values():
            part.apply_color(colour, None)


class Subpart:
    def __init__(self, mesh: trimesh.base.Trimesh, transformation_matrix, name, main_colour=None):
        self.mesh = mesh
        self.name = name
        self.transformation_matrix = transformation_matrix
        self.multicolour = False
        print(main_colour, rgba_to_hex(main_colour))
        if not self.mesh.visual.defined:
            if main_colour is not None:
                self.main_colour = Brickcolour(rgba_to_hex(main_colour)[: 7])
            else:
                self.main_colour = Brickcolour("16")
            self.apply_color()
        else:
            self.colours = OrderedDict()
            is_invisible = True
            has_transparency = False
            for index, colour in enumerate(self.mesh.visual.face_colors):
                hex_colour = rgba_to_hex(colour)
                if hex_colour in self.colours:
                    self.colours[hex_colour][1].append(index)
                else:
                    brickcolour = Brickcolour(hex_colour[:7])
                    brickcolour.alpha = str(colour[3])
                    self.colours[hex_colour] = (brickcolour, [index])
                    if not has_transparency and colour[3] > 0 and colour[3] > 255:
                        has_transparency = True
                    if is_invisible and colour[3] > 0:
                        is_invisible = False
            if len(self.colours) > 1:
                self.multicolour = True
            else:
                self.main_colour = self.colours.popitem()[1][0]
            if is_invisible:
                # Todo: Make visible
                pass

    def apply_color(self, colour: Brickcolour = None, key=None):
        if not self.multicolour or key is None:
            if colour is None:
                colour = self.main_colour
            self.mesh.visual.face_colors[0:] = np.array(colour.get_int_rgba())
            self.main_colour = colour
            if self.multicolour:
                for value in self.colours:
                    value[0] = colour
                    # Todo: Test
        elif key is not None:
            if colour is None:
                colour = self.colours[key][0]
            rgba_values = colour.get_int_rgba()
            for face in self.colours[key][1]:
                self.mesh.visual.face_colors[face] = rgba_values
            self.colours[key][0] = colour

    def convert_to_dat_file(self, filepath, main_file_name, author):
        # f"{main_file_name}s{filenumber:04d}.dat"
        file_name = os.path.basename(filepath)
        header = (f"0 ~{self.name}: Subpart of {main_file_name}\n"
                  f"Name: {file_name}"
                  f"0 Author:  {author}\n"
                  f"0 BFC CERTIFY CCW\n")
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(header)
            for line in self.to_ldraw_lines():
                file.write(line)

    def to_ldraw_lines(self):
        if self.multicolour:
            for colour, faces in self.colours.values():
                code = colour.colour_code
                for index in faces:
                    face = self.mesh.faces[index]
                    coordinate_a = ' '.join(map(str, self.mesh.vertices[face[0]]))
                    coordinate_b = ' '.join(map(str, self.mesh.vertices[face[1]]))
                    coordinate_c = ' '.join(map(str, self.mesh.vertices[face[2]]))
                    yield f"3 {code} {coordinate_a} {coordinate_b} {coordinate_c}\n"
        else:
            for face in self.mesh.faces:  # faces vertices
                coordinate_a = ' '.join(map(str, self.mesh.vertices[face[0]]))
                coordinate_b = ' '.join(map(str, self.mesh.vertices[face[1]]))
                coordinate_c = ' '.join(map(str, self.mesh.vertices[face[2]]))
                yield f"3 {self.main_colour.colour_code} {coordinate_a} {coordinate_b} {coordinate_c}\n"


def rgba_to_hex(color):
    def __color_to_hex(number: int):
        hex_number = hex(number).lstrip("0x")
        if len(hex_number) < 2:
            hex_number = "0" + hex_number
        return hex_number

    r = __color_to_hex(color[0])
    g = __color_to_hex(color[1])
    b = __color_to_hex(color[2])
    a = __color_to_hex(color[3])
    return f"#{r}{g}{b}{a}"
