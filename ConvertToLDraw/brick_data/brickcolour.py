import os
import numpy as np

basedir = os.path.dirname(__file__)


def is_brickcolour(colour_code: str):
    if len(colour_code) < 1 or colour_code is None:
        return False, "No Colour Code", "Empty colour code was provided"
    elif not colour_code.startswith("0x2") and not colour_code.startswith("#"):
        if not colour_code.isdigit():
            return (False, "Invalid Colour Code",
                    f"The provided colour code '{colour_code}' is not a number.\n "
                    f"Use a code from the LDraw Colour Definition Reference.\n"
                    f"If you wanted to use a Direct/HTML colour the format is 0x2RRGGBB or #RRGGBB"
                    f"(R,B and G are hexadecimal).")
    elif colour_code.startswith("0x2"):
        if len(colour_code) > 9:
            return (False, "Invalid Colour Code",
                    f"The provided colour '{colour_code}' seems to be a Direct/HTML colour but is to long.")
        elif len(colour_code) < 9:
            return (False, "Invalid Colour Code",
                    f"The provided colour '{colour_code}' seems to be a Direct/HTML colour but is to short.")
        for i in range(2, 9):
            if colour_code[i] not in ["A", "B", "C", "D", "E", "F"] and not colour_code[i].isdigit():
                return (False, "Invalid Colour Code",
                        f"The provided colour '{colour_code}' seems to be a Direct/HTML colour, "
                        f"but contains a invalid character at position: {i - 2} - '{colour_code[i]}'.\n"
                        f"Valid characters are 0-9 and A-F(uppercase)")
    elif colour_code.startswith("#"):
        colour_code = colour_code.upper()
        if len(colour_code) > 7:
            return (False, "Invalid Colour Code",
                    f"The provided colour '{colour_code}' seems to be a Direct/HTML colour but is to long.")
        elif len(colour_code) < 7:
            return (False, "Invalid Colour Code",
                    f"The provided colour '{colour_code}' seems to be a Direct/HTML colour but is to short.")
        for i in range(1, 7):
            if colour_code[i] not in ["A", "B", "C", "D", "E", "F"] and not colour_code[i].isdigit():
                return (False, "Invalid Colour Code",
                        f"The provided colour '{colour_code}' seems to be a Direct/HTML colour, "
                        f"but contains a invalid charcter at position: {i - 2} - '{colour_code[i]}'.\n"
                        f"Valid characters are 0-9 and A-F(uppercase)")
    return True,


class Brickcolour:
    def __new__(cls, colour_code: str = "16", values=None):
        if not is_brickcolour(colour_code)[0] and values is None:
            return None
        instance = super().__new__(cls)
        return instance

    def __init__(self, colour_code: str = "16", values=None):
        if values is None:
            self.colour_code = colour_code
            if colour_code.startswith("0x2"):
                self.colour_type = "Direct"
                self.rgb_values = f"#{self.colour_code[3:]}"
                self.rgb_edge = get_contrast_colour(self.rgb_values)
                self.alpha = "255"
                self.ldrawname = self.colour_code
            elif colour_code.startswith("#"):
                colour_code = colour_code.upper()
                self.colour_type = "Direct"
                self.rgb_values = colour_code
                self.colour_code = f"0x2{colour_code[1:]}"
                self.rgb_edge = get_contrast_colour(self.rgb_values)
                self.alpha = "255"
                self.ldrawname = self.colour_code
            else:
                self.colour_type = "LDraw"
                self.ldrawname, _, \
                    self.rgb_values, \
                    self.rgb_edge, \
                    self.alpha, \
                    self.luminance, \
                    self.material, \
                    self.legoids, \
                    self.legoname, \
                    self.category = get_colour_info_by_colour_code(self.colour_code)
        else:
            self.colour_type = "LDraw"
            self.ldrawname, \
                self.colour_code, \
                self.rgb_values, \
                self.rgb_edge, \
                self.alpha, \
                self.luminance, \
                self.material, \
                self.legoids, \
                self.legoname, \
                self.category = values

    def __getitem__(self, key):
        if key == 0:
            return self.ldrawname
        elif key == 1:
            return self.colour_code
        elif key == 2:
            return self.rgb_values
        elif key == 3:
            return self.rgb_edge
        elif key == 4:
            return self.alpha
        elif key == 5:
            return self.luminance
        elif key == 6:
            return self.material
        elif key == 7:
            return self.legoids
        elif key == 8:
            return self.legoname
        elif key == 9:
            return self.category

    def __str__(self):
        if self.colour_type == "Direct":
            return f"Direct Colour: {self.colour_code}"
        else:
            if self.ldrawname is not None:
                return f"LDraw Colour {self.colour_code}: {self.ldrawname}, {self.rgb_values}"
            else:
                return f"Unknown LDraw Colour {self.colour_code}"

    def __repr__(self):
        return f"brickcolour({self.colour_code})"

    def get_hex_rgba(self) -> str:
        if not hasattr(self, "hex_rgba"):
            self.hex_rgba = self.rgb_values + hex(int(self.alpha)).lstrip("0x")
        return self.hex_rgba

    def __eq__(self, other):
        if isinstance(other, Brickcolour):
            return self.colour_code == other.colour_code
        return False

    def get_int_rgba(self):
        r = int(self.rgb_values[1:3], 16)
        g = int(self.rgb_values[3:5], 16)
        b = int(self.rgb_values[5:7], 16)
        return r, g, b, int(self.alpha)

    def get_ldraw_line(self) -> str:
        line = f"0 !COLOUR {self.ldrawname} CODE {self.colour_code} VALUE {self.rgb_values} EDGE {self.rgb_edge}"
        if int(self.alpha) < 255:
            line += f" ALPHA {self.alpha}"
        if self.luminance != "" and self.luminance is not None:
            line += f" LUMINANCE {self.luminance}"
        if self.material != "" and self.material is not None:
            line += f" {self.material}"
        line += "\n"
        return line


def get_colour_info_by_colour_code(colour_code: str):
    found_colour = ["Undefined", colour_code, "#FFFFFF", "000000", "255", "", "", "", "", ""]
    with open(os.path.join(basedir, "colour_definitions.csv"), "r", encoding="utf-8") as source:
        # skip row with column names
        source.readline()
        for line in source:
            values = line.split(";")
            if values[1] == colour_code:
                for i in range(len(values)):
                    # replace empty values with None
                    if len(values[i]) == 0:
                        values[i] = None
                found_colour = values
                # remove line break character from last value
                found_colour[-1] = found_colour[-1][:-1]
                break

    return found_colour


def get_all_brickcolours(included_color_categories=None):
    colour_list = []
    with open(os.path.join(basedir, "colour_definitions.csv"), "r", encoding="utf-8") as source:
        # skip row with column names
        source.readline()
        for line in source:
            values = line.split(";")
            # remove line break character from last value
            values[-1] = values[-1][:-1]
            if included_color_categories is None or values[9] in included_color_categories:
                colour_list.append(Brickcolour(values=values))
    return colour_list


def search_brickcolour_by_rgb_colour(rgb_colour: str, colourlist: list):
    colourlist.sort(key=lambda c: get_hex_colour_weight(rgb_colour, c.rgb_values))
    return colourlist


def search_by_color_name(name: str, colourlist: list):
    name = "".join(name.upper().split(" "))

    def matchname(colour: Brickcolour):
        if name in "".join(colour.ldrawname.upper().split(" ")) or name in "".join(colour.legoname.upper().split(" ")):
            return True
        else:
            return False

    search_results = [colour for colour in colourlist if matchname(colour)]
    return search_results


def get_closest_brickcolour_by_rgb_colour(rgb_colour: str, colourlist: list):
    r_1 = int(rgb_colour[1:3], 16)
    g_1 = int(rgb_colour[3:5], 16)
    b_1 = int(rgb_colour[5:7], 16)
    return min(colourlist, key=lambda c: _get_hex_colour_weight(r_1, g_1, b_1, c.rgb_values))


def get_contrast_colour(rgb_values: str):
    r = 0 if int(rgb_values[1:3], 16) < 128 else 1
    g = 0 if int(rgb_values[3:5], 16) < 128 else 1
    b = 0 if int(rgb_values[5:7], 16) < 128 else 1
    if r + g + b < 2:
        return "#FFFFFF"
    else:
        return "#000000"


def get_complementary_colour(rgb_values: str):
    red = '%02X' % (255 - int(rgb_values[1:3], 16))
    green = '%02X' % (255 - int(rgb_values[3:5], 16))
    blue = '%02X' % (255 - int(rgb_values[5:7], 16))

    return f"#{''.join([red, green, blue])}"


def get_hex_colour_weight(colour_1: str, colour_2: str) -> int:
    if colour_1 == colour_2:
        return 0
    r_1 = int(colour_1[1:3], 16)
    g_1 = int(colour_1[3:5], 16)
    b_1 = int(colour_1[5:7], 16)

    return _get_hex_colour_weight(r_1, g_1, b_1, colour_2)


def _get_hex_colour_weight(r_1: int, g_1: int, b_1: int, colour_2: str) -> int:
    r_2 = int(colour_2[1:3], 16)
    g_2 = int(colour_2[3:5], 16)
    b_2 = int(colour_2[5:7], 16)
    return (r_1 - r_2) ** 2 + (g_1 - g_2) ** 2 + (b_1 - b_2) ** 2
