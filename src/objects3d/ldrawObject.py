import trimesh
import os
class ldraw_object():
    def __init__(self, scene: trimesh.scene.Scene, name="", bricklinknumber="", author=""):
        self.scene = scene
        self.scene.apply_scale(2.5)
        self.name = name
        self.bricklinknumber = bricklinknumber
        self.author = author

    def save_dat_file(self, filepath):
        filename = os.path.basename(filepath)
        fileheader = (f"0 FILE {filename}\n"
                      f"0 {self.name}\n"
                      f"0 Name:  {filename}\n"
                      f"0 Author:  {self.author}\n"
                      f"0 BL_Item_No {self.bricklinknumber}\n"
                      f"0 BFC CERTIFY CCW\n")
        part = self.scene.to_geometry()
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(fileheader)
            for face in part.faces: #faces vertices
                coordinate_a = ' '.join(map(str, part.vertices[face[0]]))
                coordinate_b = ' '.join(map(str, part.vertices[face[1]]))
                coordinate_c = ' '.join(map(str, part.vertices[face[2]]))
                file.write(f"3 16 {coordinate_a} {coordinate_b} {coordinate_c}\n")
