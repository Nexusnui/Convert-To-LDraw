def isBrickColor(color_code: str):
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
    return (True,)