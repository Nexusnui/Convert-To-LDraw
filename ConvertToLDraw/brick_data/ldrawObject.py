import trimesh
import trimesh.visual.material
import os
from ConvertToLDraw.brick_data.brickcolour import Brickcolour, get_closest_brickcolour_by_rgb_colour, \
    get_all_brickcolours
import numpy as np
from collections import OrderedDict


# Todo: Change np print settings?


class LdrawObject:
    def __init__(self, filepath: str,
                 name="", bricklinknumber="", author="", category="", keywords=None,
                 part_license=None,
                 scale=1, multi_object=True, multicolour=True,
                 use_ldraw_scale=True, use_ldraw_rotation=True):
        self.cached_colour_definitions = OrderedDict()
        self.__load_scene(filepath, scale, multi_object, multicolour, use_ldraw_scale, use_ldraw_rotation)

        self.name = name
        self.bricklinknumber = bricklinknumber
        self.author = author
        self.category = category
        self.keywords = keywords
        self.part_license = part_license

    def __load_scene(self, filepath, scale=1, multi_object=True, multicolour=True,
                     use_ldraw_scale=True, use_ldraw_rotation=True):
        _, file_extension = os.path.splitext(filepath)

        scene = trimesh.load_scene(filepath)

        if len(scene.geometry) == 1 or not multi_object:
            if len(scene.geometry) > 1 and multicolour:
                recolour = True
                if len(scene.geometry) == 1:
                    recolour = False
                for geometry in scene.geometry.values():
                    if not recolour:
                        break
                    if isinstance(geometry.visual, trimesh.visual.texture.TextureVisuals):
                        recolour = False
                        break
                    try:
                        geometry.visual.face_colors
                        has_multiple_colours = False
                        first_colour = geometry.visual.face_colors[0]
                        for colour in geometry.visual.face_colors:
                            c_check = first_colour == colour
                            if not (c_check[0] and c_check[1] and c_check[2] and c_check[3]):
                                has_multiple_colours = True
                                break

                        c_check = geometry.visual.main_color == [102, 102, 102, 255]
                        default_colour = c_check[0] and c_check[1] and c_check[2] and c_check[3]
                        if has_multiple_colours and not default_colour:
                            recolour = False
                            break
                    except Exception:
                        # Invalid or no color data (is fixed at a later point)
                        pass
                if recolour:
                    colorrange = [0, 63, 127, 191, 255]
                    for index, geometry in enumerate(scene.geometry.values()):
                        # only 125 different colors possible
                        g = colorrange[index % 5]
                        r = colorrange[int(index / 5 % 5)]
                        b = colorrange[int(index / 25 % 5)]
                        geometry.visual.face_colors = np.ones((len(geometry.faces), 4), np.uint8) * [r, g, b, 255]

            scene = trimesh.scene.scene.Scene(scene.to_mesh())

        if use_ldraw_rotation:
            # LDraw co-ordinate system is right-handed where -Y is "up"
            # For this reason the entire scene is rotated by 90° around the X-axis
            scene.apply_transform([
                [1, 0, 0, 0],
                [0, 0, -1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1]
            ])

        if scene.units not in ["mm", "millimeter", None]:
            scene = scene.convert_units("millimeter")

        if scale != 1:
            scene = scene.scaled(scale)
        self.size = scene.extents

        if use_ldraw_scale:
            # Convert to LDraw Units
            scene = scene.scaled(2.5)

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
                    hexcolour = rgba_to_hex(geometry.visual.material.main_color)[:7]
                    main_colour = Brickcolour(hexcolour)
                    geometry.visual = geometry.visual.to_color()
                if multicolour:
                    try:
                        geometry.visual.face_colors
                    except Exception:
                        # Invalid Color Data -> can occur when loading step files
                        geometry.visual.face_colors = np.ones((len(geometry.faces), 4), np.uint8) * 255
                        main_colour = Brickcolour("16")
                else:
                    geometry.visual.face_colors = np.ones((len(geometry.faces), 4), np.uint8) * 255
                    main_colour = Brickcolour("16")
                transformation_matrix = scene_graph.edge_data[("world", node)]["matrix"]
                self.subparts[key] = Subpart(geometry, transformation_matrix, key, main_colour, self.cached_colour_definitions)
        self.scene = scene

    def convert_to_dat_file(self, filepath=None, one_file=False):
        if filepath is None:
            one_file = True
            filename = self.name.replace(" ", "_")
        else:
            filename = os.path.basename(filepath)
        bricklinknumberline = ""
        if len(self.bricklinknumber) > 0:
            bricklinknumberline = f"0 BL_Item_No {self.bricklinknumber}\n\n"
        categoryline = ""
        if len(self.category) > 0:
            categoryline = f"\n0 !CATEGORY {self.category}\n"
        keyword_lines = ""
        if self.keywords is not None and len(self.keywords) > 0:
            keyword_lines = []
            current_line = f"0 !KEYWORDS {self.keywords[0]}"
            for kw in self.keywords[1:]:
                if len(current_line + kw) > 80:
                    keyword_lines.append(current_line)
                    current_line = f"0 !KEYWORDS {kw}"
                else:
                    current_line = f"{current_line}, {kw}"
            keyword_lines.append(f"{current_line}\n")
            keyword_lines = "\n".join(keyword_lines)
        license_line = ""
        if self.part_license is not None and len(self.part_license) > 0:
            license_line = f"0 !LICENSE {self.part_license}\n"
        colour_definitions = ""
        if one_file:
            for definition_line in self.cached_colour_definitions.values():
                colour_definitions += definition_line
            if len(colour_definitions) > 0:
                colour_definitions += "\n"
        header = (f"0 FILE {filename}\n"
                  f"0 {self.name}\n"
                  f"0 Name:  {filename}\n"
                  f"0 Author:  {self.author}\n"
                  f"0 !LDRAW_ORG Unofficial_Part\n"
                  f"{license_line}\n"
                  f"{bricklinknumberline}"
                  f"{colour_definitions}"
                  f"0 BFC CERTIFY CCW\n"
                  f"{categoryline}"
                  f"{keyword_lines}\n")

        with ResultWriter(filepath) as file:
            file.write(header)
            if len(self.subparts) == 1:
                subpart = list(self.subparts.values())[0]
                color_code = "16"
                if not subpart.multicolour:
                    color_code = subpart.main_colour.colour_code
                for line in subpart.to_ldraw_lines(color_code):
                    file.write(line)
            else:
                if one_file:
                    subparts_lines = []
                else:
                    sub_dir = f"{os.path.dirname(filepath)}/s/"
                    os.makedirs(sub_dir, exist_ok=True)
                basename = filename.split(".dat")[0]
                for count, part in enumerate(self.subparts.values()):
                    subfilename = f"{basename}s{count:03d}.dat"
                    if not one_file:
                        # Todo: Case filepath = None
                        subfilepath = f"{sub_dir}{subfilename}"
                        part.convert_to_dat_file(subfilepath, filename, self.author, license_line)
                    tm_a = f"{part.transformation_matrix[0][0]:f}"
                    tm_b = f"{part.transformation_matrix[0][1]:f}"
                    tm_c = f"{part.transformation_matrix[0][2]:f}"
                    tm_d = f"{part.transformation_matrix[1][0]:f}"
                    tm_e = f"{part.transformation_matrix[1][1]:f}"
                    tm_f = f"{part.transformation_matrix[1][2]:f}"
                    tm_g = f"{part.transformation_matrix[2][0]:f}"
                    tm_h = f"{part.transformation_matrix[2][1]:f}"
                    tm_i = f"{part.transformation_matrix[2][2]:f}"
                    tm_x = f"{part.transformation_matrix[0][3]:f}"
                    tm_y = f"{part.transformation_matrix[1][3]:f}"
                    tm_z = f"{part.transformation_matrix[2][3]:f}"
                    # Todo: Improve precision of floats to string conversion (np.float64(1))
                    code = part.main_colour.colour_code
                    if not one_file:
                        subfilename = f"s/{subfilename}"
                    file.write(f"0 //~{part.name}\n"
                               f"1 {code} {tm_x} {tm_y} {tm_z}"
                               f" {tm_a} {tm_b} {tm_c}"
                               f" {tm_d} {tm_e} {tm_f}"
                               f" {tm_g} {tm_h} {tm_i}"
                               f" {subfilename}\n")
                    if one_file:
                        subparts_lines.append(
                            f"\n{part.get_ldraw_header(subfilename, filename, self.author, license_line)}")
                        for line in part.to_ldraw_lines():
                            subparts_lines.append(line)
                if one_file:
                    file.write_list(subparts_lines)
            if filepath is None:
                return file.get_result()

    def set_main_colour(self, colour: Brickcolour):
        self.main_colour = colour
        for part in self.subparts.values():
            part.apply_color(colour, None)


class Subpart:
    def __init__(self, mesh: trimesh.base.Trimesh,
                 transformation_matrix,
                 name,
                 main_colour: Brickcolour = None,
                 cached_colour_definitions: OrderedDict = OrderedDict()):
        self.mesh = mesh
        self.name = name
        self.transformation_matrix = transformation_matrix
        self.cached_colour_definitions = cached_colour_definitions
        self.multicolour = False
        if not self.mesh.visual.defined:
            if main_colour is not None:
                self.main_colour = main_colour
                if self.main_colour.colour_type == "LDraw" and self.main_colour.ldrawname != "Undefined":
                    self.cached_colour_definitions[self.main_colour.colour_code] = self.main_colour.get_ldraw_line()
            else:
                self.main_colour = Brickcolour("16")
                self.cached_colour_definitions["16"] = self.main_colour.get_ldraw_line()
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
                    self.colours[hex_colour] = [brickcolour, [index]]
                    if not has_transparency and colour[3] > 0 and colour[3] > 255:
                        has_transparency = True
                    if is_invisible and colour[3] > 0:
                        is_invisible = False
            if len(self.colours) > 1:
                self.multicolour = True
                if main_colour is None:
                    self.main_colour = Brickcolour("16")
                    self.cached_colour_definitions["16"] = self.main_colour.get_ldraw_line()
                else:
                    self.main_colour = main_colour
                    if self.main_colour:
                        if self.main_colour.colour_type == "LDraw" and self.main_colour.ldrawname != "Undefined":
                            self.cached_colour_definitions[self.main_colour.colour_code] = self.main_colour.get_ldraw_line()
            else:
                if main_colour is not None:
                    self.main_colour = main_colour
                    if self.main_colour.colour_type == "LDraw" and self.main_colour.ldrawname != "Undefined":
                        self.cached_colour_definitions[self.main_colour.colour_code] = self.main_colour.get_ldraw_line()
                    self.apply_color()
                else:
                    self.main_colour = self.colours.popitem()[1][0]
            if is_invisible:
                for key, value in self.colours.items():
                    value[0].alpha = "255"
                    self.apply_color(key=key)

    def apply_color(self, colour: Brickcolour = None, key=None):
        if colour is not None:
            if (colour.colour_code not in self.cached_colour_definitions
                    and colour.colour_type == "LDraw" and colour.ldrawname != "Undefined"):
                self.cached_colour_definitions[colour.colour_code] = colour.get_ldraw_line()

        if not self.multicolour or key is None:
            if colour is None:
                colour = self.main_colour
            # self.mesh.visual.face_colors[0:] = np.array(colour.get_int_rgba())
            self.main_colour = colour
            if self.multicolour:
                self.multicolour = False
                self.colours = None
        elif key is not None:
            if colour is None:
                colour = self.colours[key][0]
                if (colour.colour_code not in self.cached_colour_definitions
                        and colour.colour_type == "LDraw" and colour.ldrawname != "Undefined"):
                    self.cached_colour_definitions[colour.colour_code] = colour.get_ldraw_line()
            self.colours[key][0] = colour

    def merge_duplicate_colours(self, apply_after=False):
        new_colours = OrderedDict()
        for key in self.colours:
            colour = self.colours[key][0]
            if colour.colour_code in new_colours:
                new_colours[colour.colour_code][1].extend(self.colours[key][1])
            else:
                new_colours[colour.colour_code] = [colour, self.colours[key][1]]
        self.colours = new_colours
        if apply_after:
            for key in self.colours:
                self.apply_color(key=key)
        if len(self.colours) == 1:
            self.multicolour = False
            self.main_colour = self.colours.popitem()[1][0]

    def map_to_ldraw_colours(self, included_colour_categories):
        colourlist = get_all_brickcolours(included_colour_categories)
        for key in self.colours:
            if self.colours[key][0].colour_type == "Direct":
                rgb_values = self.colours[key][0].rgb_values
                mappedcolor = get_closest_brickcolour_by_rgb_colour(rgb_values, colourlist)
                self.colours[key][0] = mappedcolor
        self.merge_duplicate_colours(True)

    def convert_to_dat_file(self, filepath, main_file_name, author, license_line):
        filename = f"s/{os.path.basename(filepath)}"
        header = self.get_ldraw_header(filename, main_file_name, author, license_line)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(header)
            for line in self.to_ldraw_lines():
                file.write(line)

    def get_ldraw_header(self, filename, main_file_name, author, license_line, define_colours=False):
        colour_definitions = ""
        if define_colours:
            for definition_line in self.cached_colour_definitions.values():
                colour_definitions += definition_line
            if len(colour_definitions) > 0:
                colour_definitions += "\n"
        header = (f"0 FILE {filename}\n"
                  f"0 ~{self.name}: Subpart of {main_file_name}\n"
                  f"0 Name: {filename}\n"
                  f"0 Author:  {author}\n"
                  f"0 !LDRAW_ORG Unofficial_Subpart\n"
                  f"{license_line}\n"
                  f"{colour_definitions}"
                  f"0 BFC CERTIFY CCW\n")
        return header

    def to_ldraw_lines(self, color_code="16"):
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
                yield f"3 {color_code} {coordinate_a} {coordinate_b} {coordinate_c}\n"


class ResultWriter:
    def __init__(self, filepath: str = None):
        self._is_file_writer = filepath is not None
        self.filepath = filepath

    def __enter__(self):
        if self._is_file_writer:
            self._result = open(self.filepath, "w", encoding="utf-8")
        else:
            self._result = []
        return self

    def __exit__(self, *args):
        if self._is_file_writer:
            self._result.close()

    def write(self, lines: str):
        if self._is_file_writer:
            self._result.write(lines)
        else:
            self._result.append(lines)

    def write_list(self, lines: list):
        if self._is_file_writer:
            for line in lines:
                self._result.write(line)
        else:
            self._result.extend(lines)

    def get_result(self):
        if not self._is_file_writer:
            return "".join(self._result)
        return None


def rgba_to_hex(color):
    def __color_to_hex(number: int):
        if number == 0:
            hex_number = "00"
        else:
            hex_number = hex(number).lstrip("0x")
        if len(hex_number) < 2:
            hex_number = "0" + hex_number
        return hex_number

    r = __color_to_hex(color[0])
    g = __color_to_hex(color[1])
    b = __color_to_hex(color[2])
    a = __color_to_hex(color[3])
    return f"#{r}{g}{b}{a}"


default_part_licenses = [
    "Licensed under CC BY 4.0 : see CAreadme.txt ",
    "Licensed under CC BY 2.0 and CC BY 4.0 : see CAreadme.txt",
    "Redistributable under CCAL version 2.0 : see CAreadme.txt",
    "Not redistributable : see NonCAreadme.txt"
]
