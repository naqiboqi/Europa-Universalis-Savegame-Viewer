import os
import re

from PIL import Image

from . import EUArea, EUProvince, ProvinceType, EURegion



class EUWorldData:
    def __init__(
        self, 
        regions: dict[str, EURegion], 
        areas: dict[str, EUArea], 
        provinces: dict[int, EUProvince]):
        self.regions = regions
        self.areas = areas
        self.provinces = provinces
        self.world_image: Image.Image = None 

    @classmethod
    def load_world_data(cls, map_folder: str):
        print("Loading EU4 world data....")
        world = cls({}, {}, {})
        print("Loading provinces....")
        world.provinces = world.load_world_provinces(map_folder)

        print("Loading areas....")
        world.areas = world.load_world_areas(map_folder, world.provinces)

        print("Loading regions....")
        world.regions = world.load_world_regions(map_folder, world.areas)

        return world

    def try_extract_prov_id(self, line: str):
        match = re.match(r"^-(\d+)={", line)
        return int(match.group(1)) if match else None

    def load_world_provinces(self, map_folder: str, province_data: list[str] = None):
        provinces: dict[int, EUProvince] = {}
        patterns = {
            "name": r'name="([^"]+)"',
            "owner": r'owner="([^"]+)"',
            "capital": r'capital="([^"]+)"',
            "culture": r'culture=([\w]+)',
            "religion": r'religion=([\w]+)',
            "base_tax": r'base_tax=([\d.]+)',
            "base_production": r'base_production=([\d.]+)',
            "base_manpower": r'base_manpower=([\d.]+)',
            "native_size": r"native_size=(\d+)",
            "patrol": r"patrol=(\d+)"
        }

        if province_data is None:
            province_data_path = os.path.join(map_folder, "province.txt")
            with open(province_data_path, "r", encoding="latin-1") as file:
                province_data = file.readlines()

        line_iter = iter(province_data)
        current_province = None

        try:
            while True:
                line = next(line_iter).strip()

                prov_id = self.try_extract_prov_id(line)
                if prov_id is not None:
                    if current_province:
                        current_province["province_type"] = self.determine_province_type(current_province)
                        provinces[current_province["province_id"]] = EUProvince.from_dict(current_province)

                    current_province = {"province_id": prov_id}
                    continue

                if current_province is None:
                    continue

                for key, pattern in patterns.items():
                    match = re.search(pattern, line)
                    if match:
                        current_province[key] = match.group(1)

        except StopIteration:
            pass

        return provinces

    def determine_province_type(self, prov_data: dict) -> ProvinceType:
        if not any(dev in prov_data for dev in ["base_tax", "base_production", "base_manpower"]):
            if "patrol" in prov_data:
                return ProvinceType.SEA
            return ProvinceType.WASTELAND
        if "owner" in prov_data:
            return ProvinceType.OWNED
        if "native_size" in prov_data:
            return ProvinceType.NATIVE
        return None

    def load_world_areas(self, map_folder: str, world_provinces: dict[int, EUProvince]):
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

    def load_world_regions(self, map_folder: str, areas: dict[str, EUArea]):
        region_path = os.path.join(map_folder, "region.txt")
        regions = {}

        with open(region_path, "r", encoding="latin-1") as file:
            region_pattern = r"(\w+_region)\s*=\s*\{.*?areas\s*=\s*\{([^}]+)\}\s*\}"
            region_data = file.read()

            matches = re.findall(region_pattern, region_data, flags=re.DOTALL)
            for region_id, areas_str in matches:
                area_names = [area.strip() for area in areas_str.splitlines() if area.strip()]
                regions[region_id] = area_names

        return regions

    def load_savefile_provinces(self, map_folder: str, savefile: str):
        province_data: list[str] = []
        with open(savefile, "r", encoding="utf-8") as file:
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
                        province_data.extend([line + "\n", next_line + "\n"])
                        continue

                if inside:
                    province_data.append(line + "\n")
                    depth += line.count("{") - line.count("}")
                    if depth == 0:
                        break

        return self.load_world_provinces(map_folder="", province_data=province_data)
