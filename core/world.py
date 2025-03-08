import numpy as np
import os
import re

from collections import defaultdict
from PIL import Image

from .colors import EUColors
from .models import EUArea, EUCountry, EUProvince, ProvinceType, EURegion
from .utils import MapUtils


class EUWorldData:
    def __init__(self):
        self.areas: dict[str, EUArea] = {}
        self.countries: dict[str, EUCountry] = {}
        self.provinces: dict[int, EUProvince] = {}
        self.regions: dict[str, EURegion] = {}
        self.world_image: Image.Image = None 

        self.default_province_data: dict[int, dict[str, str]] = {}
        self.current_province_data: dict[int, dict[str, str]] = {}
        self.province_locations: dict[int, set[tuple[int]]] = {}
        self.default_area_data: dict[str, dict[str, str|set[int]]] = {}
        self.default_region_data: dict[str, dict[str, str|set[str]]] = {}

    @classmethod
    def load_world_data(cls, map_folder: str, colors: EUColors):
        print("Loading EU4 world data....")
        world = cls()

        print("Loading countries....")
        world.countries = world.load_countries(colors)

        print("Loading provinces....")
        world.default_province_data = world.load_world_provinces(world.read_province_file(map_folder))
        world.world_image = world.load_world_image(map_folder)
        world.province_locations = world.get_province_pixel_locations(colors.default_province_colors)

        print("Loading areas....")
        world.default_area_data = world.load_world_areas(map_folder)

        print("Loading regions....")
        world.default_region_data = world.load_world_regions(map_folder)

        return world

    def build_world(self, save_folder: str, savefile: str):
        print("Building provinces....")
        province_file_lines = self.read_save_file(save_folder, savefile)
        self.current_province_data = self.load_world_provinces(province_file_lines)

        for province_id, province_data in self.current_province_data.items():
            pixel_locations = self.province_locations.get(province_id)
            if not pixel_locations:
                continue

            province_data["pixel_locations"] = pixel_locations
            self.provinces[province_id] = EUProvince.from_dict({**province_data})

        print("Building areas....")
        for area_id, area_data in self.default_area_data.items():
            area_province_ids = area_data["provinces"]
            area_provinces = {
                province_id: self.provinces[province_id] for province_id in self.provinces
                if province_id in area_province_ids
            }

            area_data["provinces"] = area_provinces
            self.areas[area_id] = EUArea.from_dict(area_data)

        print("Building regions....")
        for region_id, region_data in self.default_region_data.items():
            region_area_ids = region_data["areas"]
            region_areas = {
                area_id: self.areas[area_id] for area_id in self.areas
                if area_id in region_area_ids
            }

            region_data["areas"] = region_areas
            self.regions[region_id] = EURegion.from_dict(region_data)

    def load_countries(self, colors: EUColors):
        countries: dict[str, EUCountry] = {}
        for country_tag, country_name in colors.tag_names.items():

            tag_color = colors.tag_colors.get(country_tag)
            if not tag_color:
                tag_color = MapUtils.seed_color(country_tag)

            countries[country_tag] = EUCountry(
                tag=country_tag, 
                tag_color=tag_color, 
                name=EUCountry.fix_name(country_name))

        return countries

    def load_world_image(self, map_folder: str):
        province_bmp_path = os.path.join(map_folder, "provinces.bmp")
        province_color_map = Image.open(province_bmp_path).convert("RGB")
        return province_color_map

    def read_province_file(self, map_folder: str):
        province_data_path = os.path.join(map_folder, "province.txt")
        with open(province_data_path, "r", encoding="latin-1") as file:
            return file.readlines()

    def read_save_file(self, save_folder: str, savefile: str):
        save_data_path = os.path.join(save_folder, savefile)
        with open(save_data_path, "r", encoding="latin-1") as file:
            return file.readlines()

    def try_extract_prov_id(self, line: str):
        match = re.match(r"^-(\d+)={", line)
        return int(match.group(1)) if match else None

    def load_world_provinces(self, province_data: list[str]):
        provinces: dict[int, dict[str, str]] = {}
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

        line_iter = iter(province_data)
        current_province: dict[str, str|EUCountry] = None

        try:
            while True:
                line = next(line_iter).strip()

                if "PROV" in line:
                    continue

                prov_id = self.try_extract_prov_id(line)
                if prov_id is not None:
                    if current_province and "name" in current_province:
                        current_province["province_type"] = self.set_province_type(current_province)
                        provinces[current_province["province_id"]] = current_province

                    current_province = {"province_id": prov_id}
                    continue

                if current_province is None:
                    continue

                for key, pattern in patterns.items():
                    match = re.search(pattern, line)
                    if match and not key in current_province:
                        if key == "owner":
                            country_tag = match.group(1)
                            if not country_tag in self.countries:
                                country = EUCountry(tag=country_tag, tag_color=MapUtils.seed_color(country_tag))
                                self.countries[country_tag] = country
                            else:
                                country = self.countries[country_tag]

                            current_province[key] = self.countries[country_tag]
                        else:
                            current_province[key] = match.group(1)

        except StopIteration:
            pass

        return provinces

    def set_province_type(self, province_data: dict):
        is_developed = any(province_data.get(dev) for dev in ["base_tax", "base_production", "base_manpower"])

        if is_developed:
            if province_data.get("owner"):
                return ProvinceType.OWNED

            return ProvinceType.NATIVE

        if province_data.get("patrol"):
            return ProvinceType.SEA

        return ProvinceType.WASTELAND

    def get_province_pixel_locations(self, default_province_colors: dict[tuple[int], int]):
        map_pixels = np.array(self.world_image)
        height, width = map_pixels.shape[:2]

        province_locations = defaultdict(set)
        for x in range(width):
            for y in range(height):
                pixel_color = tuple(map_pixels[y, x][:3])
                if pixel_color in default_province_colors:
                    province_id = default_province_colors[pixel_color]
                    province_locations[province_id].add((x, y))

        return dict(province_locations)

    def load_world_areas(self, map_folder: str):
        area_path = os.path.join(map_folder, "area.txt")
        areas: dict[str, dict[str, str|set[int]]] = {}

        pattern = re.compile(r'(\w+_area)\s*=\s*\{')
        area_id = None
        area_provinces: list[int] = []

        with open(area_path, "r", encoding="latin-1") as file:
            for line in file:
                line = line.strip()

                if "color" in line:
                    continue

                match = pattern.match(line)
                if match:
                    if area_id and area_provinces:
                        areas[area_id] = {
                            "area_id" : area_id,
                            "name" : EUArea.name_from_id(area_id),
                            "provinces": set(province_id for province_id in area_provinces
                                if province_id in self.default_province_data)}

                    area_id = match.group(1)
                    area_provinces = []
                    continue

                if line == "}":
                    if area_id and area_provinces:
                        areas[area_id] = {
                            "area_id" : area_id,
                            "name" : EUArea.name_from_id(area_id),
                            "provinces": set(province_id for province_id in area_provinces
                                if province_id in self.default_province_data)}

                    area_id = None
                    continue

                area_provinces.extend(map(int, re.findall(r"\b\d+\b", line)))

        return areas

    def load_world_regions(self, map_folder: str):
        region_path = os.path.join(map_folder, "region.txt")
        regions: dict[str, dict[str, str|set[int]]] = {}

        with open(region_path, "r", encoding="latin-1") as file:
            region_pattern = r"(\w+_region)\s*=\s*\{.*?areas\s*=\s*\{([^}]+)\}\s*\}"
            region_data = file.read()

            matches = re.findall(region_pattern, region_data, flags=re.DOTALL)
            for region_id, areas_str in matches:
                area_ids = [area.strip() for area in areas_str.splitlines() if area.strip()]

                region_areas = set(area_id for area_id in area_ids if area_id in self.default_area_data)

                regions[region_id] = {
                    "region_id" : region_id,
                    "name" : EURegion.name_from_id(region_id),
                    "areas" : region_areas
                }

        return regions
