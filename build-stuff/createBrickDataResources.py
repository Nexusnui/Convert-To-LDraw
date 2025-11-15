# This File is intended for updating the colour list ThreeDToLD/brick_data/colour_definitions.csv
# (Paths are Windows based)

# Parse the LDraw Colour Config to a List of Colours
def parse_ldraw_colour_config(config_path):
    colours = []
    with open(config_path, "r", encoding="utf-8") as source:
        lego_ids = []
        lego_names = []
        skipped_line = ""
        category = ""
        while skipped_line != "0 // Colour definitions\n":
            skipped_line = source.readline()
        for line in source:
            # After the colour definitons the Avatar definitions follow
            if line == "0 // Avatar definitions":
                break
            if "LEGOID" not in line and "!COLOUR" not in line and "BricksetID" not in line and "LDraw" in line:
                category = f"LDraw:{line.split("0 // ")[1].split("\n")[0]}"
                pass
            if "LEGOID" in line or "BricksetID" in line:
                ids, names = line.split(" - ")
                ids = ids.split(" / ")
                lego_ids = [ids[0].split(" ")[-1]] + ids[1:]
                lego_names = names[:-1].split(" / ")
            if "!COLOUR" in line:
                ldraw_name = line.split(" ")[2]
                code = next(x for x in line.split("CODE")[1].split(" ") if x != "")
                rgb_values = next(x for x in line.split("VALUE")[1].split(" ") if x != "")
                edge_values = next(x for x in line.split("EDGE")[1].split(" ") if x != "").split("\n")[0]
                alpha = "255"
                if "ALPHA" in line:
                    alpha = next(x for x in line.split("ALPHA")[1].split(" ") if x != "").split("\n")[0]
                luminance = ""
                if "LUMINANCE" in line:
                    luminance = next(x for x in line.split("LUMINANCE")[1].split(" ") if x != "").split("\n")[0]
                material = ""
                if "CHROME\n" in line:
                    material = "CHROME"
                if "PEARLESCENT\n" in line:
                    material = "PEARLESCENT"
                if "METAL\n" in line:
                    material = "METAL"
                if "RUBBER\n" in line:
                    material = "RUBBER"
                if "MATERIAL" in line:
                    material = f"MATERIAL{line.split("MATERIAL")[1].split("\n")[0]}"
                if "MATTE_METALLIC" in line:
                    material = "MATTE_METALLIC"
                colours.append((ldraw_name, code, rgb_values, edge_values, alpha, luminance, material, lego_ids,
                                lego_names, category))
                lego_ids = []
                lego_names = []
    return colours


# Parse the custom Bricklink color definition to a list of colours
def parse_bl_studio_color_definition(definition_path):
    colours = []
    with open(definition_path, "r", encoding="utf-8") as source:
        source.readline()
        for line in source:
            values = line.split("\t")
            if values[0] != "":
                name = values[4].replace(" ", "_")
                code = f"100{values[3]}"
                rgb_values = values[8]
                # edge value for all bricklink colors is the one for black.
                # it would be better if it were generated based on the main color.
                edge_values = "#1B2A34"
                alpha = str(round(float(values[9]) * 255))
                category = f"Bricklink:{values[15].split("\n")[0]}"
                colours.append((name, code, rgb_values, edge_values, alpha, "", "", [], [], category))
    return colours


# Get a line for the LDraw Color Config from colour
def get_ldraw_colour_definition_line(colour):
    # (ldraw_name, code, rgb_values, edge_values, alpha, luminance, material, legoIDs, legoNames)
    name = "_".join(colour[0].split(" "))
    line = f"0 !COLOUR {name} CODE {colour[1]} VALUE {colour[2]} EDGE {colour[3]}"
    if int(colour[4]) < 255:
        line += f" ALPHA {colour[4]}"
    if colour[5] != "":
        line += f" LUMINANCE {colour[5]}"
    if colour[6] != "":
        line += f" {colour[6]}"
    if len(colour[7]) > 0:
        line = f"0 // LEGOID {" / ".join(colour[7])} - {" / ".join(colour[8])}\n{line}"
    return line


def save_colourlists_to_csv(colorlists, filename):
    with open(filename, "w", encoding="utf-8") as file_out:
        file_out.write("LDraw Name;Code;RGB Values;Edge Values;Alpha;Luminance;Material;Lego IDs;Lego Names;Category\n")
        for colourlist in colorlists:
            for colour in colourlist:
                file_out.write(";".join(colour[:7] + ("/".join(colour[7]), "/".join(colour[8]), colour[9])) + "\n")


def get_brick_categories_from_config(config_path):
    categories = []
    with open(config_path, "r", encoding="utf-8") as source:
        skipped_line = ""
        while skipped_line != "0 // Avatar definitions\n":
            skipped_line = source.readline()
        for line in source:
            if "!AVATAR" in line:
                categories.append(line.split('CATEGORY "')[1].split('" DESCRIPTION')[0])
    return categories

def get_color_categories_from_lists(colorlists: list):
    categories = []
    for cl in colorlists:
        for colour in cl:
            if colour[9] not in categories:
                categories.append(colour[9])
    return categories

def save_list_to_py(listname, str_list, filename):
    with open(filename, "w", encoding="utf-8") as file_out:
        file_out.write(f"{listname} = [\n")
        for item in str_list:
            file_out.write(f'    "{item}",\n')
        file_out.write("]\n")


if __name__ == "__main__":
    # This file is in your LDraw library folder
    ldraw_config = "Path/To/Your/LDConfig.ldr"
    ldraw_colours = parse_ldraw_colour_config(ldraw_config)

    # Change this to the current version
    bl_studio_custom_color_definition = "C:/Program Files/Studio 2.0/data/CustomColors/CustomColorDefinition_2_1_9.txt"
    bl_studio_colours = parse_bl_studio_color_definition(bl_studio_custom_color_definition)


    color_definitions_csv = f"{__file__.split("build-stuff")[0]}ThreeDToLD\\brick_data\\colour_definitions.csv"
    save_colourlists_to_csv([ldraw_colours, bl_studio_colours], color_definitions_csv)

    colour_category_definitions = f"{__file__.split("build-stuff")[0]}ThreeDToLD\\brick_data\\colour_categories.py"
    colour_categories = get_color_categories_from_lists([ldraw_colours, bl_studio_colours])
    save_list_to_py("colour_categories", colour_categories, colour_category_definitions)

    ldraw_categories = get_brick_categories_from_config(ldraw_config)
    brick_category_definitions = f"{__file__.split("build-stuff")[0]}ThreeDToLD\\brick_data\\brick_categories.py"
    save_list_to_py("brick_categories", ldraw_categories, brick_category_definitions)
