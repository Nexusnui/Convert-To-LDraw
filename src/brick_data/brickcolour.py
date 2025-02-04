import os
from colormath2.color_objects import sRGBColor, LabColor
from colormath2.color_conversions import convert_color
from colormath2.color_diff import delta_e_cmc
basedir = os.path.dirname(__file__)


def is_brickcolour(colour_code: str):
    if len(colour_code) < 1:
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
    def __new__(cls, colour_code: str):
        if not is_brickcolour(colour_code)[0]:
            return None
        instance = super().__new__(cls)
        return instance

    def __init__(self, colour_code: str):
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

    def get_hex_rgba(self):
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
                # remove line break character from colour category
                found_colour[9] = found_colour[9][:-1]
                break

    return found_colour


def get_all_brickcolours(included_color_categories=None):
    colour_list = []
    with open(os.path.join(basedir, "colour_definitions.csv"), "r", encoding="utf-8") as source:
        # skip row with column names
        source.readline()
        for line in source:
            values = line.split(";")
            colour = Brickcolour(values[1])
            if included_color_categories is None or colour.category in included_color_categories:
                colour_list.append(colour)
    return colour_list


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


def get_hex_colour_distance(colour_1: str, colour_2: str) -> float:
    if colour_1 == colour_2:
        return 0
    r_1 = int(colour_1[1:3], 16)
    g_1 = int(colour_1[3:5], 16)
    b_1 = int(colour_1[5:7], 16)
    rgb_1 = sRGBColor(r_1, g_1, b_1, True)
    lab_1 = convert_color(rgb_1, LabColor)
    r_2 = int(colour_2[1:3], 16)
    g_2 = int(colour_2[3:5], 16)
    b_2 = int(colour_2[5:7], 16)
    rgb_2 = sRGBColor(r_2, g_2, b_2, True)
    lab_2 = convert_color(rgb_2, LabColor)
    distance = delta_e_cmc(lab_1, lab_2)
    return distance
