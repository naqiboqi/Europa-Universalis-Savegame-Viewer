import os
import re

from core.colors import extract_province_colors
from core.models import EUArea, EUProvince, ProvinceType, EURegion



def load_provinces_from_save(savefile: str):
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


def try_extract_prov_id(line: str):
    match = re.match(r"^-(\d+)={", line)
    return int(match.group(1)) if match else None

def load_world_provinces(map_folder: str):
    province_data_path = os.path.join(map_folder, "province.txt")
    provinces: dict[int, EUProvince] = {}

    with open(province_data_path, "r", encoding="latin-1") as file:
        patterns = {
            "name": r'name="([^"]+)"',
            "owner": r'owner="([^"]+)"',
            "capital": r'capital="([^"]+)"',
            "culture": r'culture=([\w]+)',
            "religion": r'religion=([\w]+)',
            "base_tax": r'base_tax=([\d.]+)',
            "base_production": r'base_production=([\d.]+)',
            "base_manpower": r'base_manpower=([\d.]+)',
            "native_size" : r"native_size=(\d+)",
            "patrol" : r"patrol=(\d+)"
        }

        line = file.readline().strip()
        while line:
            prov_id = try_extract_prov_id(line)
            if prov_id:
                prov_data = {"province_id" : prov_id}
                prov_type = None

                while True:
                    line = file.readline()
                    if not line:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    if try_extract_prov_id(line):
                        break

                    for key, pattern in patterns.items():
                        match = re.search(pattern, line)
                        if match:
                            prov_data[key] = match.group(1)

                if not any(dev in prov_data for dev in ["base_tax", "base_production", "base_manpower"]):
                    if "patrol" in prov_data:
                        prov_type = ProvinceType.SEA
                    else:
                        prov_type = ProvinceType.WASTELAND

                elif "owner" in prov_data:
                    prov_type = ProvinceType.OWNED

                elif "native_size" in prov_data:
                    prov_type = ProvinceType.NATIVE

                prov_data["province_type"] = prov_type
                new_prov = EUProvince.from_dict(prov_data)
                provinces[prov_id] = new_prov

            line = file.readline()

    return provinces


def load_world_areas(map_folder: str, world_provinces: dict[int, EUProvince]):
    area_path = os.path.join(map_folder, "area.txt")
    areas: dict[str, EUArea] = {}

    pattern = re.compile(r'(\w+)_area\s*=\s*\{')
    area_id = None
    area_provinces: list[int] = []

    with open(area_path, "r", encoding="latin-1") as file:
        for line in file:
            line = line.strip()

            match = pattern.match(line)
            if match:
                if area_id:
                    areas[area_id] = EUArea(
                        area_id=area_id,
                        name=area_id.replace("_", " ").capitalize(),
                        provinces={pid: world_provinces[pid] for pid in area_provinces
                            if pid in world_provinces})

                area_id = match.group(1)
                area_provinces = []
                continue

            if line == "}":
                if area_id:
                    areas[area_id] = EUArea(
                        area_id=area_id,
                        name=area_id.replace("_", " ").capitalize(),
                        provinces={pid: world_provinces[pid] for pid in area_provinces 
                            if pid in world_provinces})

                    area_id = None
                continue

            area_provinces.extend(map(int, re.findall(r"\b\d+\b", line)))

    return areas

def load_world_regions(map_folder: str, areas: dict[str, EUArea]):
    region_path = os.path.join(map_folder, "region.txt")
    regions = {}

    with open(region_path, "r", encoding="latin-1") as file:
        region_pattern = r"(\w+_region)\s*=\s*\{.*?areas\s*=\s*\{([^}]+)\}\s*\}"  # Capture the region and its areas
        region_data = file.read()  # Read the entire content to search for matches

        matches = re.findall(region_pattern, region_data, flags=re.DOTALL)
        for region_name, areas_str in matches:
            area_names = [area.strip() for area in areas_str.splitlines() if area.strip()]  # Get area names
            regions[region_name] = area_names

    return regions

def load_world_data(map_folder: str):
    print("Loading EU4 world data....")
    print("Loading provinces....")
    provinces = load_world_provinces(map_folder)

    print("Loading areas....")
    areas = load_world_areas(map_folder, provinces)

    print("Loading regions....")
    regions = load_world_regions(map_folder, areas)
    print(regions)



def extract_save_data(
    savefile: str,
    map_folder: str,
    save_folder: str):

    block_data = load_provinces_from_save(os.path.join(save_folder, savefile))
    print("Getting provinces....")
    #country_provinces = map_provinces_to_countries(block_data)

    print("Getting province bmp colors....")
    def_path = os.path.join(map_folder, "definition.csv")
    province_colors = extract_province_colors(defpath=def_path)
    #return country_provinces, province_colors
