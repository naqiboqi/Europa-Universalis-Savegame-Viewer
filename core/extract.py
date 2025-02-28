import os
import re

from core.colors import extract_province_colors



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
    pattern = r"discovered_by\s*=\s*\{\s*\}"
    return re.search(pattern, line) is not None

def map_provinces_to_countries(block_data: list[str]):
    provinces: dict[int, list[int]] = {}

    prov_id = None
    owner_tag = None
    is_native = False
    is_water = False
    is_wasteland = False

    for line in block_data:
        line = line.strip()

        new_prov_id = get_prov_id(line)
        if new_prov_id:
            if prov_id is not None:
                if is_water:
                    provinces[prov_id] = "WATER"
                elif is_native:
                    provinces[prov_id] = "NAT"
                elif is_wasteland:
                    provinces[prov_id] = "WASTE"
                else:
                    provinces[prov_id] = owner_tag

            prov_id = new_prov_id
            owner_tag = None
            is_native = False
            is_water = False
            is_wasteland = False
            continue

        if owner_tag is None:
            tag = get_country_tag(line)
            if tag:
                owner_tag = tag

        if is_native_province(line):
            is_native = True
            is_water = False
            is_wasteland = False

        elif is_water_province(line):
            is_water = True
            is_native = False
            is_wasteland = False

        elif is_wasteland_province(line) and not is_water:
            is_wasteland = True
            is_native = False
            is_water = False

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

def extract_save_data(
    savefile: str,
    map_folder: str,
    save_folder: str):

    block_data = extract_provinces_block(os.path.join(save_folder, savefile))
    print("Getting provinces....")
    country_provinces = map_provinces_to_countries(block_data)

    print("Getting province bmp colors....")
    def_path = os.path.join(map_folder, "definition.csv")
    province_colors = extract_province_colors(defpath=def_path)
    return country_provinces, province_colors