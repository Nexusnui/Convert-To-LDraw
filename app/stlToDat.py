#!/usr/bin/python
"""
Convert a STL to a LDRAW compatible DAT file.
It is assumed that the STL file units are millimeters.
Hazen 12/15
"""

import os
import sys
# install "numpy-stl" not "stl"
from stl import mesh


def stlToDat(input_filename: str, output_filename: str, colour: str = "16"):
    mm_to_ldu = 1.0 / 0.4
    inputMesh = mesh.Mesh.from_file(input_filename)

    inputMesh.x *= mm_to_ldu
    inputMesh.y *= mm_to_ldu
    inputMesh.z *= mm_to_ldu

    with open(output_filename, "w", encoding="utf-8") as fp_out:
        # 0: Comment or META command the first 0 line is alway the filename
        fp_out.write(f"0 FILE {os.path.basename(output_filename)}\n")
        fp_out.write("0 !LDRAW_ORG Unofficial_part\n")
        # Todo: Add License Meta command to file
        fp_out.write("0 BFC CERTIFY CCW\n")

        for index, triangle in enumerate(inputMesh):
            # 3:filled triangle, 16:Default color
            fp_out.write(f"3 {colour} {' '.join(map(lambda a: str(a), triangle))}\n")

    # return number of triangles
    return len(inputMesh)


if __name__ == '__main__':

    print(sys.argv)

    arg_len = len(sys.argv)
    if arg_len < 2 or arg_len in [3, 5]:
        print("usage: <stl file> [optional]-o <output .dat file> [optional]-c <colour>")
        exit()

    input_filename = sys.argv[1]
    output_filename = os.path.splitext(sys.argv[1])[0] + ".dat"
    colour = "16"

    if arg_len > 2:
        if sys.argv[2] == "-o":
            output_filename = sys.argv[3]
        elif sys.argv[2] == "-c":
            colour = sys.argv[3]

    if arg_len > 4:
        if sys.argv[4] == "-o":
            output_filename = sys.argv[5]
        elif sys.argv[4] == "-c":
            colour = sys.argv[5]

    print(f"Part contains {stlToDat(input_filename, output_filename, colour)} triangles.")
