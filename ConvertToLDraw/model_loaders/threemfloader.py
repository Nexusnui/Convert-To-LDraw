from trimesh.scene.scene import Scene
from trimesh.base import Trimesh
from trimesh.transformations import is_same_transform
from trimesh.transformations import identity_matrix
from zipfile import ZipFile
from lxml import etree
import numpy as np
import re
from ConvertToLDraw.appexcetions import Missing3mfElementError
from ConvertToLDraw.model_loaders.modelloader import Modelloader


def _get_tag_type(element) -> str:
    return element.tag.split("}")[-1]


def _transform_to_matrix(transform: str | list) -> list:
    if not isinstance(transform, str):
        return transform
    values = transform.split(" ")
    # This is how the 3mf spec describes the matrix
    """matrix = [[float(values[0]), float(values[1]), float(values[2]), 0.0],
              [float(values[3]), float(values[4]), float(values[5]), 0.0],
              [float(values[6]), float(values[7]), float(values[8]), 0.0],
              [float(values[9]), float(values[10]), float(values[11]), 1.0]]"""
    # This is how trimesh requires it (could be a bug I will create an issue upstream)
    matrix = [[float(values[0]), float(values[3]), float(values[6]), float(values[9])],
              [float(values[1]), float(values[4]), float(values[7]), float(values[10])],
              [float(values[2]), float(values[5]), float(values[8]), float(values[11])],
              [0.0, 0.0, 0.0, 1.0]]
    return matrix


def _is_identity_matrix(transform: str | list) -> bool:
    if transform is None:
        return True
    matrix = _transform_to_matrix(transform)
    result = is_same_transform(identity_matrix(), matrix)
    return result


def _combine_transforms(transform_a: str | list, transform_b: str | list) -> str | list:
    if _is_identity_matrix(transform_a):
        return transform_b
    elif _is_identity_matrix(transform_b):
        return transform_a
    matrix_a = _transform_to_matrix(transform_a)
    matrix_b = _transform_to_matrix(transform_b)
    result = np.matmul(matrix_a, matrix_b)
    return result


def _hex_to_rgba_colour(hexcolour: str):
    hexcolour = "".join(re.findall("[a-f,A-F,0-9]", hexcolour))
    r = int(hexcolour[0:2], 16)
    g = int(hexcolour[2:4], 16)
    b = int(hexcolour[4:6], 16)
    if len(hexcolour) >= 8:
        a = int(hexcolour[6:8], 16)
    else:
        a = 255
    return r, g, b, a


class Threemfloader(Modelloader):

    def __init__(self):
        self.was_reset = True
        self.model: Scene = Scene()
        self.metadata: dict = {}
        self.vendor: str = ""
        self.app_version: str = None
        self.resources = None
        self.build = None
        self.model_config = None
        self.config_name: str = None
        self.model_config_name: str = None
        self.unit: str = None
        self.is_slic3r_derivat: bool = False
        self.colour_groups = {}
        self.sub_models = {}
        self.meshes = []

    def load_model(self, filepath) -> tuple[Scene, dict]:
        if not self.was_reset:
            self.__init__()
        self.was_reset = False

        # Collect Data from 3mf file
        with ZipFile(filepath) as file_3mf:
            with file_3mf.open("3D/3dmodel.model", "r") as model_file:
                model_3mf = etree.parse(model_file).getroot()
            if model_3mf.attrib.has_key("unit"):
                self.unit = model_3mf.attrib["unit"]
            for element in model_3mf.getchildren():
                element_tag = _get_tag_type(element)
                if element_tag == "metadata":
                    if element.attrib["name"] == "Title":
                        if element.text is not None:
                            self.metadata["name"] = element.text
                    elif element.attrib["name"] == "Designer":
                        if element.text is not None:
                            self.metadata["author"] = element.text
                    elif element.attrib["name"] == "LicenseTerms":
                        if element.text is not None:
                            self.metadata["license"] = element.text
                    elif element.attrib["name"] == "Application":
                        if element.text is not None:
                            self.vendor: str = element.text
                    elif element.attrib["name"].startswith("slic3rpe"):
                        self.is_slic3r_derivat = True
                        self.model_config_name = "Metadata/Slic3r_PE_model.config"
                        self.config_name = "Metadata/Slic3r_PE.config"
                elif element_tag == "resources":
                    self.resources = element
                elif element_tag == "build":
                    self.build = element
            if self.vendor.startswith("PrusaSlicer"):
                self.model_config_name = "Metadata/Slic3r_PE_model.config"
                self.config_name = "Metadata/Slic3r_PE.config"
                self.is_slic3r_derivat = True
                self.vendor, self.app_version = self.vendor.split("-")
            elif self.vendor.startswith("BambuStudio"):
                self.model_config_name = "Metadata/model_settings.config"
                self.config_name = "Metadata/project_settings.config"
                self.is_slic3r_derivat = True
                self.vendor, self.app_version = self.vendor.split("-")

            # Get colours definitions from slicer configs
            if self.config_name is not None:
                # Add colour group for slicer defined colours sc=slicer colour
                self.colour_groups["sc"] = []
                if self.vendor == "BambuStudio":
                    with file_3mf.open(self.config_name) as config_file:
                        in_colour_section = False
                        for line in config_file.readlines():
                            if in_colour_section and b'],' in line:
                                break
                            elif in_colour_section:
                                self.colour_groups["sc"].append(_hex_to_rgba_colour(str(line).split('"')[1]))
                            if b'"filament_colour":' in line:
                                in_colour_section = True
                elif self.is_slic3r_derivat:
                    if self.config_name in file_3mf.namelist():
                        with file_3mf.open(self.config_name) as config_file:
                            for line in config_file.readlines():
                                if b'extruder_colour' in line:
                                    colours = str(line).split("= ")[1].split(";")
                                    self.colour_groups["sc"] = str(line).split("= ")[1].split(";")
                                    for colour in colours:
                                        self.colour_groups["sc"].append(_hex_to_rgba_colour(colour))
                                    break
            if self.model_config_name is not None:
                with file_3mf.open(self.model_config_name) as model_config_file:
                    self.model_config = etree.parse(model_config_file).getroot()
        if self.resources is None and self.build is None:
            # Todo: Raise correct exception
            raise Missing3mfElementError("No build and resources elements in 3mf file")
        if self.resources is None:
            raise Missing3mfElementError("No resources element in 3mf file")
        if self.build is None:
            raise Missing3mfElementError("No build element in 3mf file")

        # Collect colour definitions from color and material groups
        for resource in self.resources.getchildren():
            resource_tag = _get_tag_type(resource)
            resource_id = resource.attrib["id"]
            if resource_tag in ["m:colorgroup", "basematerials", "colorgroup"]:
                self.colour_groups[resource_id] = []
                colour_key = "color"
                if resource_tag == "basematerials":
                    colour_key = "displaycolor"
                for colour in resource.getchildren():
                    self.colour_groups[resource_id].append(_hex_to_rgba_colour(colour.attrib[colour_key]))
            elif resource_tag == "object":
                if resource.attrib["type"] != "model":
                    continue
                self.sub_models[resource_id] = resource
        

        #Collect mesh data with combined transformation matrices
        for item in self.build:
            if _get_tag_type(item) == "item":
                transform = None
                if item.attrib.has_key("transform"):
                    transform = item.attrib["transform"]
                object_id = item.attrib["objectid"]
                self.collect_object_meshes(object_id, transform, 0)

        if self.is_slic3r_derivat:
            # Todo: Split and Color Meshes according to slicer data and model_config
            # Edit Mesh to use colorgroup
            pass

        # Create Trimesh geometries from mesh data
        for mesh_data in self.meshes:
            # Default trimesh colour
            mesh_base_colour = (102, 102, 102, 255)
            mesh_vertices = []
            mesh_triangles = []
            mesh_colours = []
            parent_object = mesh_data[0]
            mesh_id = parent_object.attrib["id"]
            mesh = parent_object.getchildren()[mesh_data[2]]
            mesh_name = f"object_{mesh_id}"

            if parent_object.attrib.has_key("name"):
                mesh_name = parent_object.attrib["name"]

            if parent_object.attrib.has_key("pid"):
                mesh_base_colour = self.colour_groups[parent_object.attrib["pid"]][int(parent_object.attrib["pindex"])]

            for data in mesh.getchildren():
                data_tag = _get_tag_type(data)
                if data_tag == "vertices":
                    for vertex in data.getchildren():
                        if _get_tag_type(vertex) == "vertex":
                            mesh_vertices.append((
                                float(vertex.attrib["x"]),
                                float(vertex.attrib["y"]),
                                float(vertex.attrib["z"])
                            ))
                elif data_tag == "triangles":
                    for triangle in data.getchildren():
                        if _get_tag_type(triangle) == "triangle":
                            mesh_triangles.append((
                                int(triangle.attrib["v1"]),
                                int(triangle.attrib["v2"]),
                                int(triangle.attrib["v3"])
                            ))
                            if triangle.attrib.has_key("pid"):
                                mesh_colours.append(self.colour_groups
                                                    [triangle.attrib["pid"]]
                                                    [int(triangle.attrib["p1"])]
                                                    )
                            else:
                                mesh_colours.append(mesh_base_colour)
            geometry = Trimesh(vertices=mesh_vertices, faces=mesh_triangles, face_colors=mesh_colours)
            transform = _transform_to_matrix(mesh_data[1])
            if _is_identity_matrix(transform):
                self.model.add_geometry(geometry, geom_name=mesh_name)
            else:
                self.model.add_geometry(geometry, transform=transform, geom_name=mesh_name)

        self.model.units = self.unit
        return self.model, self.metadata

    def collect_object_meshes(self, object_id: str, transform: str, depth: int):
        if object_id not in self.sub_models:
            # Not a model
            return
        build_object = self.sub_models[object_id]
        if _get_tag_type(build_object) != "object":
            return
        for index, content in enumerate(build_object.getchildren()):
            content_tag = _get_tag_type(content)
            if content_tag == "components":
                if depth >= 32:
                    raise RecursionError("3mf component depth exceeds 32.")
                for component in content.getchildren():
                    component_transform = transform
                    if component.attrib.has_key("transform"):
                        component_transform = _combine_transforms(transform, component.attrib["transform"])
                    component_id = component.attrib["objectid"]
                    self.collect_object_meshes(component_id, component_transform, depth+1)
            elif content_tag == "mesh":
                self.meshes.append((build_object, transform, index))
