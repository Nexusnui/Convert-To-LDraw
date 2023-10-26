def is_brickcolor(color_code: str):
    if len(color_code) < 1:
        return False, "No Color Code", "Apply Checkbox was toggled, but no color code provided"
    elif not color_code.startswith("0x2"):
        if not color_code.isdigit():
            return (False, "Invalid Color Code",
                    f"The provided color code '{color_code}' is not a number.\n "
                    f"Use a code from the LDraw Colour Definition Reference.\n"
                    f"If you wanted to use a Direct/HTML color the format is 0x2RRGGBB "
                    f"(R,B and G are hexadecimal).")
    elif color_code.startswith("0x2"):
        if len(color_code) > 9:
            return (False, "Invalid Color Code",
                    f"The provided color '{color_code}' seems to be a Direct/HTML color but is to long.")
        elif len(color_code) < 9:
            return (False, "Invalid Color Code",
                    f"The provided color '{color_code}' seems to be a Direct/HTML color but is to short.")
        for i in range(2, 9):
            if color_code[i] not in ["A", "B", "C", "D", "E", "F"] and not color_code[i].isdigit():
                return (False, "Invalid Color Code",
                        f"The provided color '{color_code}' seems to be a Direct/HTML color, "
                        f"but contains a invalid charcter at position: {i - 2} - '{color_code[i]}'.\n"
                        f"Valid characters are 0-9 and A-F(uppercase)")
    return True,


class brickcolor:
    def __new__(cls, color_code: str):
        if not is_brickcolor(color_code)[0]:
            return None
        instance = super().__new__(cls)
        return instance

    def __init__(self, color_code: str):
        self.color_code = color_code
        if color_code.startswith("0x2"):
            self.color_type = "Direct"
            self.rgb_values = f"#{self.color_code[3:]}"
            self.rgb_edge = get_contrast_color(self.rgb_values)
        else:
            self.color_type = "LDraw"
            self.ldrawname, _, \
            self.rgb_values, \
            self.rgb_edge, \
            self.alpha, \
            self.luminance, \
            self.material, \
            self.legoname, \
            self.legoid, \
            self.category = get_color_info_by_id(self.color_code)

    def __str__(self):
        if self.color_type == "Direct":
            return f"Direct Color: {self.color_code}"
        else:
            if self.ldrawname is not None:
                return f"LDraw Color {self.color_code}: {self.ldrawname}, {self.rgb_values}"
            else:
                return f"Unknown LDraw Color {self.color_code}"

    def __repr__(self):
        return f"brickcolor({self.color_code})"


def get_color_info_by_id(id: str):
    found_color = [None] * 10
    with open("BrickColors.csv", "r", encoding="utf-8") as source:
        # skip row with column names
        source.readline()
        for line in source:
            values = line.split(";")
            if values[1] == id:
                for i in range(len(values)):
                    # replace empty values with None
                    if len(values[i]) == 0:
                        values[i] = None
                found_color = values
                break

    return found_color

def get_contrast_color(rgb_values: str):
    red = hex_switch(rgb_values[1:3])
    green = hex_switch(rgb_values[3:5])
    blue = hex_switch(rgb_values[5:7])

    return f"#{''.join([red, green, blue])}"


def hex_switch(hex_val: str):
    if int(hex_val, 16) < 128:
        return "FF"
    else:
        return "00"


def get_complementary_color(rgb_values: str):
    red = '%02X' % (255 - int(rgb_values[1:3], 16))
    green = '%02X' % (255 - int(rgb_values[3:5], 16))
    blue = '%02X' % (255 - int(rgb_values[5:7], 16))

    return f"#{''.join([red, green, blue])}"
