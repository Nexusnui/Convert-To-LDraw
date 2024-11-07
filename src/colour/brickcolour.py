def is_brickcolour(colour_code: str):
    if len(colour_code) < 1:
        return False, "No Colour Code", "Apply Checkbox was toggled, but no colour code provided"
    elif not colour_code.startswith("0x2"):
        if not colour_code.isdigit():
            return (False, "Invalid Colour Code",
                    f"The provided colour code '{colour_code}' is not a number.\n "
                    f"Use a code from the LDraw Colour Definition Reference.\n"
                    f"If you wanted to use a Direct/HTML colour the format is 0x2RRGGBB "
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
            self.category = get_colour_info_by_id(self.colour_code)

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


def get_colour_info_by_id(id: str):
    found_colour = [None] * 10
    with open("colour_definitions.csv", "r", encoding="utf-8") as source:
        # skip row with column names
        source.readline()
        for line in source:
            values = line.split(";")
            if values[1] == id:
                for i in range(len(values)):
                    # replace empty values with None
                    if len(values[i]) == 0:
                        values[i] = None
                found_colour = values
                break

    return found_colour

def get_contrast_colour(rgb_values: str):
    r = 0 if int(rgb_values[1:3], 16) < 128 else 1
    g = 0 if int(rgb_values[3:5], 16) < 128 else 1
    b = 0 if int(rgb_values[5:7], 16) < 128 else 1
    if r+g+b < 2:
        return "#FFFFFF"
    else:
        return "#000000"


def get_complementary_colour(rgb_values: str):
    red = '%02X' % (255 - int(rgb_values[1:3], 16))
    green = '%02X' % (255 - int(rgb_values[3:5], 16))
    blue = '%02X' % (255 - int(rgb_values[5:7], 16))

    return f"#{''.join([red, green, blue])}"
