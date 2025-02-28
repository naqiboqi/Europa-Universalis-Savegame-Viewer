import csv  
import os
import re

from PIL import Image


PROVINCE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "province_data"))
MAP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "map"))
SAVES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "saves"))
TAGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "country_tags"))

OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))


def extract_provinces_block(savefile: str):
    with open(savefile, "r", encoding="utf-8") as file:
        data: list[str] = []
        inside = False
        depth = 0

        lines = iter(file)
        for line in file:
            line = line.strip()
            if not inside and line == "provinces={":
                next_line = next(lines, "").strip()
                if next_line == "-1={":
                    inside = True
                    depth = 2
                    data.extend([line + "\n", next_line + "\n"])
                    continue

            if inside:
                data.append(line + "\n")
                depth += line.count("{") - line.count("}")
                if depth == 0:
                    break

    return data

def get_prov_id(line: str):
    pattern = r"^-(\d+)={"
    match = re.match(pattern, line)
    return int(match.group(1)) if match else None

def get_country_tag(line: str):
    pattern = r'^owner="(\w+)"'
    match = re.match(pattern, line)
    return match.group(1) if match else None

def is_native_province(line: str):
    patterns = [
        r"native_size=\d+",
        r"native_ferocity=\d+",
        r"native_hostileness=\d+"
    ]
    return any(re.search(pattern, line) for pattern in patterns)

def is_water_province(line: str):
    pattern = r"patrol=\d+"
    return re.search(pattern, line) is not None

def is_wasteland_province(line: str):
    """Check if the province is wasteland (empty discovered_by)."""
    # Check for discovered_by={} line with optional spaces
    pattern = r"discovered_by\s*=\s*\{\s*\}"
    return re.search(pattern, line) is not None

def map_provinces_to_countries(provfile: str):
    provinces: dict[int, list[int]] = {}
    with open(provfile, "r", encoding="utf-8") as file:
        lines = file.readlines()

    prov_id = None
    owner_tag = None
    is_native = False
    is_water = False
    is_wasteland = False

    for line in lines:
        line = line.strip()

        # Check for new province ID
        new_prov_id = get_prov_id(line)
        if new_prov_id:
            # Store the previous province before moving to the next one
            if prov_id is not None:
                # Ensure to only assign the correct value based on the flags
                if is_water:
                    provinces[prov_id] = "WATER"
                elif is_native:
                    provinces[prov_id] = "NAT"
                elif is_wasteland:
                    provinces[prov_id] = "WASTE"
                else:
                    provinces[prov_id] = owner_tag

            # Start a new province block
            prov_id = new_prov_id
            owner_tag = None
            is_native = False
            is_water = False
            is_wasteland = False
            continue

        # Check for owner tag
        if owner_tag is None:
            tag = get_country_tag(line)
            if tag:
                owner_tag = tag

        # Check if it's a native province
        if is_native_province(line):
            # Mark as native and reset the other flags
            is_native = True
            is_water = False
            is_wasteland = False

        # Check if it's a water province
        elif is_water_province(line):
            # Mark as water and reset the other flags
            is_water = True
            is_native = False
            is_wasteland = False
        
        # Check if it's a wasteland province, but only if it's not already marked as water
        elif is_wasteland_province(line) and not is_water:
            # Mark as wasteland and reset the other flags
            is_wasteland = True
            is_native = False
            is_water = False

    # Store the last province after looping
    if prov_id is not None:
        if is_water:
            provinces[prov_id] = "WATER"
        elif is_native:
            provinces[prov_id] = "NAT"
        elif is_wasteland:
            provinces[prov_id] = "WASTE"
        else:
            provinces[prov_id] = owner_tag

    return provinces



def load_tag_colors(tag_files: list[str]):
    missing = 0
    tags: dict[str, str] = {}
    colors: dict[str, tuple[int]] = {}

    tag_pattern = r"(\w{3})\s*=\s*\"([^\"]+)\""
    for tag_file in tag_files:
        with open(os.path.join(TAGS_FOLDER, tag_file), "r", encoding="utf-8") as file:
            for line in file:
                if not line:
                    continue

                match = re.match(tag_pattern, line)
                if match:
                    tag = match.group(1)
                    filename = match.group(2)
                    tags[tag] = filename
                else:
                    print(f"Unable to find file or tag for {line}?")
                    missing += 1

    color_pattern = r"color\s*=\s*\{\s*(\d+)\s*(\d+)\s*(\d+)\s*\}"
    for tag, country_file in tags.items():
        try:
            country_path = os.path.join("data", country_file)
            with open(country_path, "r", encoding="latin-1") as file:
                for line in file:
                    if not line:
                        continue

                    match = re.match(color_pattern, line)
                    if match:
                        r = int(match.group(1))
                        g = int(match.group(2))
                        b = int(match.group(3))
                        colors[tag] = (r, g, b)
                        break
        except FileNotFoundError:
            print(f"Unable to find country file {filename}")

    return colors

def load_province_colors(defpath: str):
    colors: dict[tuple[int], int] = {}
    with open(defpath, "r", encoding="latin-1") as file:
        reader = csv.reader(file, delimiter=";")
        for row in reader:
            try:
                prov_id = int(row[0])
                prov_color = tuple(map(int, row[1:4]))
                colors[prov_color] = prov_id
            except ValueError:
                continue

    return colors

def apply_colors_to_map(
    country_provinces: dict[int, str],
    country_colors: dict[str, tuple[int]], 
    province_colors: dict[tuple[int], int], 
    map_bmp: Image.Image):

    pixels = map_bmp.load()
    width, height = map_bmp.size

    for x in range(width):
        for y in range(height):
            pixel_color = pixels[x, y]
            if pixel_color in province_colors:
                province_id = province_colors[pixel_color]
                country_tag = country_provinces[province_id]

                if country_tag and country_tag in country_colors:
                    pixels[x, y] = country_colors[country_tag]
                elif country_tag == "WASTE":
                    pixels[x, y] = (128, 128, 128)
                elif country_tag == "WATER":
                    pixels[x, y] = (55, 90, 220)

    return map_bmp


def get_savefile_input():
    options = [f"{i}. {filename}" for i, filename in enumerate(os.listdir(SAVES_FOLDER), start=1)]

    option = None
    while not option:
        try:
            print("\n".join(options) + "\n")
            filenum = int(input("Enter savefile number to open: \n"))

            if not 1 <= filenum <= len(options):
                raise IndexError

            option = options[filenum - 1]
        except ValueError:
            print("Please enter a number.\n")
        except IndexError:
            print("Not a valid option.\n")

    return option.split()[1]


def main():
    savefile = get_savefile_input()

    block_data = extract_provinces_block(os.path.join(SAVES_FOLDER, savefile))

    provfile = f"{savefile[:-4]}.prov"
    provfile_path = os.path.join(PROVINCE_FOLDER, provfile)
    with open(provfile_path, "w", encoding="utf-8") as file:
        file.writelines(block_data)

    print("Getting provinces....")
    provinces = map_provinces_to_countries(provfile=provfile_path)

    print("Getting colors for country....")
    tag_files = os.listdir(TAGS_FOLDER)
    country_colors = load_tag_colors(tag_files=tag_files)

    print("Getting province bmp colors....")
    def_path = os.path.join(MAP_FOLDER, "definition.csv")
    province_colors = load_province_colors(defpath=def_path)

    print("Filling in map....")
    bmp_path = os.path.join(MAP_FOLDER, "provinces.bmp")
    map_bmp = Image.open(bmp_path).convert("RGB")
    colored_map = apply_colors_to_map(provinces, country_colors, province_colors, map_bmp)
    colored_map.save(os.path.join(OUTPUT_FOLDER, "new_map.png"))

if __name__ == "__main__":
    main()
