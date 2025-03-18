"""
World Data storage for Europa Universalis IV (EU4) savegame viewing.

This module contains the implementation for loading and parsing EU4's world definition files.
These files break the world up into regions, areas, and provinces. The world data 
is then stored in the EUWorldData class and accessed for drawing the map.
"""



import numpy as np
import os
import re

from collections import defaultdict
from PIL import Image

from .colors import EUColors
from .models import EUArea, EUCountry, EUProvince, ProvinceType, EURegion
from .utils import MapUtils


class EUWorldData:
    """Represents the world data, and stores information for how the EU4 world and user
    savegames.
    
    This class handles the loading and parsing of world definition files and user savefiles.
    Breaks the world into chunks for easier access for the MapPainter and MapDisplayer when it comes
    time to draw the map.
    
    The breakdown occurs when loading only the definition files, since their definitions do not change
    throughout a savegame's progress, only provinces. It is structured as follows:
    
    Structure:
        - **Regions** consist of multiple **areas**.
        - **Areas consist of multiple **provinces**.
        - **Countries can own **provinces** but are not restricted by **regions** or **areas**
    
    Attributes:
        areas (dict[str, EUArea]): A mapping of area names to their corresponding `EUArea` objects.
        countries (dict[str, EUCountry]): A mapping of country **tags** (in game identifiers) to `EUCountry` objects.
        provinces (dict[int, EUProvince]): A mapping of province IDs to `EUProvince` objects.
        regions (dict[str, EURegion]): A mapping of region names to `EURegion` objects.
        province_to_area (dict[int, EUArea]): A mapping of province IDs to their respective `EUArea`.
        province_to_region (dict[int, EURegion]): A mapping of province IDs to their respective `EURegion`.
        world_image (Image.Image | None): The world map image, loaded from a definition file.
        default_province_data (dict[int, dict[str, str]]): Default properties for each province before modifications.
        current_province_data (dict[int, dict[str, str]]): Stores current province data, which updates as the game progresses.
        province_locations (dict[int, set[tuple[int]]]): A mapping of province IDs to a set of pixel coordinates in the world image.
        default_area_data (dict[str, dict[str, str | set[int]]]): Default attributes for areas, including associated province IDs.
        default_region_data (dict[str, dict[str, str | set[str]]]): Default attributes for regions, including associated area names.
    """
    def __init__(self):
        self.areas: dict[str, EUArea] = {}
        self.countries: dict[str, EUCountry] = {}
        self.provinces: dict[int, EUProvince] = {}
        self.regions: dict[str, EURegion] = {}
        self.province_to_area: dict[int, EUArea] = {}
        self.province_to_region: dict[int, EURegion] = {}
        self.world_image: Image.Image = None 

        self.default_province_data: dict[int, dict[str, str]] = {}
        self.current_province_data: dict[int, dict[str, str]] = {}
        self.province_locations: dict[int, set[tuple[int]]] = {}
        self.default_area_data: dict[str, dict[str, str|set[int]]] = {}
        self.default_region_data: dict[str, dict[str, str|set[str]]] = {}

    @classmethod
    def load_world_data(cls, map_folder: str, colors: EUColors):
        """Driver class method that handles loading the default world data.
        
        Args:
            map_folder (str): The folder that contains the world definition files.
            colors (EUColors): Stores default province and country (tag) colors.
            
        Returns:
            world: (EUWorldData): The world data containting the default data.
        """
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
        """Builds the **EUProvince**, **EUArea**, **EURegion**, and Country objects by
        applying the savegame data to the default world data.
        
        Populates the **provinces**, **areas**, and **regions** dictionaries to provide
        easier access.
        
        Args:
            save_folder (str): The folder containing the user save file.
            save_file (str): The savefile to read.
        """
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

        for area_id, area in self.areas.items():
            for province_id in area.provinces:
                self.province_to_area[province_id] = area

        print("Building regions....")
        for region_id, region_data in self.default_region_data.items():
            region_area_ids = region_data["areas"]
            region_areas = {
                area_id: self.areas[area_id] for area_id in self.areas
                if area_id in region_area_ids
            }

            region_data["areas"] = region_areas
            self.regions[region_id] = EURegion.from_dict(region_data)

        for region_id, region in self.regions.items():
            for area in region:
                for province_id in area.provinces:
                    self.province_to_region[province_id] = region

    def load_countries(self, colors: EUColors):
        """Builds the **countries** dictionary with game countries.
        
        Each country has a unique three letter **tag** that will be used to identify which
        provinces it owns and an RGB color that will show which provinces it owns on the map.
        
        If a country definition is not found (common for user custom nations or native federations)
        then a color will be seeded at random.
        
        Args:
            colors (EUColors): The EUColors object that stores the default province and country (tag) colors.
        
        Returns:
            countries (dict[str, EUCountry]): A mapping of tags to a country.
        """
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

    def get_tag_pixel_locations(self, tag: str):
        """Builds the pixel locations that are occupied by a particular country.
        
        Checks the owner of each province (if it has one) and adds its pixel locations to the set.
        
        Args:
            tag (str): The three-letter identifier for the country.
            
        Returns:
            locations (set[tuple[int, int]]): A set of x, y coordinates that are occupied by the country.
        """
        if not tag in self.countries:
            return

        locations: set[tuple[int, int]] = set()
        for province in self.provinces.values():
            if province.owner and province.owner.tag == tag:
                locations.update(province.pixel_locations)

        return locations

    def load_world_image(self, map_folder: str):
        """Loads the provinces.bmp file that contains the definitions for each province.
        
        Args:
            map_folder (str): The folder that contains the world definition files.
            
        Returns:
            province_color_map (PIL.Image): The map image.
        """
        province_bmp_path = os.path.join(map_folder, "provinces.bmp")
        province_color_map = Image.open(province_bmp_path).convert("RGB")
        return province_color_map

    def read_province_file(self, map_folder: str):
        """Loads and reads the provinces.txt file that contains the default province information
        present at game start.
        
        Args:
            map_folder (str): The folder that contains the world definition files.
        
        Returns:
            list[str]: The lines from the file.
        """
        province_data_path = os.path.join(map_folder, "province.txt")
        with open(province_data_path, "r", encoding="latin-1") as file:
            return file.readlines()

    def read_save_file(self, save_folder: str, savefile: str):
        """Loads and reads the user savefile that contains the current province and country information.
        Args:
            save_folder (str): The folder that contains the world definition files.
            save_file (str): The savefile to read.
        Returns:
            list[str]: The lines from the file.
        """
        save_data_path = os.path.join(save_folder, savefile)
        with open(save_data_path, "r", encoding="latin-1") as file:
            return file.readlines()

    def try_extract_prov_id(self, line: str):
        """Checks if the line contains a province definition.
        
        Lines that start a province definition block start with a '-' followed by an integer:
        
            '-1={
            ......
            }'
        
        Args:
            line (str): The line to check.
        
        Returns:
            int: The province id.
        """
        match = re.match(r"^-(\d+)={", line)
        return int(match.group(1)) if match else None

    def set_province_type(self, province_data: dict):
        """Sets the type of province based on its key-values.
        
        Possible province types:
            - **owned**: Land province with a country owner.
            - **native**: Land province with no owner.
            - **sea**: Catch-all for coastal waters, oceans, and inland seas.
            - **wasteland**: Inhospital and intraversable.
        
        Args:
            province_data [dict]: The data for the province to check.
            
        Returns:
            ProvinceType: An enum that represents the province's type.
        """
        is_developed = any(province_data.get(dev) for dev in ["base_tax", "base_production", "base_manpower"])

        ## Only land provinces can have developent.
        if is_developed:
            if province_data.get("owner"):
                return ProvinceType.OWNED

            return ProvinceType.NATIVE

        ## EU4 assigns a patrol varaible for all sea provinces, that is used for ship patrols.
        ## Of course, you can't patrol a ship on land.
        if province_data.get("patrol"):
            return ProvinceType.SEA

        ## Otherwise it has to be wasteland.
        return ProvinceType.WASTELAND

    def load_world_provinces(self, province_data: list[str]):
        """Builds the default **provinces** dictionary from read game data.
        
        Reads over the **province_data** and matches the province definition blocks to extract
        each variable's value, and assigns it to each province.
        
        Example of part of the definition for a **land** province. Note that a lot
        of these fields will be unused (as of now):
        
            '-15={
                variables={
                precalc_monthly_dev_points=0.022
                provincial_dev_points_modifier=1.100
                shown_development_cost=26.000
                shown_precalc_monthly_dev_points=0.020
                }
                name="Ribe"
                owner="DAN"
                controller="DAN"
                previous_controller="DAN"
                cores={
                DAN
                }
                trade="lubeck"
                original_culture=danish
                native_culture=danish
                culture=danish
                religion=catholic
                original_religion=catholic
                capital="Ribe"
                is_city=yes
                base_tax=5.000
                original_tax=13.000
                base_production=5.000
                base_manpower=3.000
            ....
            ....
            }'

        A **sea** province:
        
            '-1483={
                name="Labrador Sea"
                institutions={
                0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000
                }
                likely_rebels="parliamentarians_rebels"
                trade_goods=unknown
                ub=no
                patrol=90
                discovered_by={}
                trade_power=0.000
            }'

        Args:
            province_data (list[str]): The read province data. Is from either default or a savegame.
        
        Returns:
            provinces (dict[int, dict[str, str]]): A mapping of province IDs to that province's data.
        """
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
        current_province: dict[str, str] = None

        try:
            while True:
                line = next(line_iter).strip()

                ## "PROV" represents unused provinces.
                if "PROV" in line:
                    continue

                ## Check if this line starts a province definition block.
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
                            ## Check if that tag exists, if not we build a new country.
                            ## Commonly happens for user created countries or native federations.
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

    def get_province_pixel_locations(self, default_province_colors: dict[tuple[int, int, int], int]):
        """Builds the pixel locations that are occupied by each province in the world.
        
        Each province has a unique color in the image, and by reading over the pixels, can get exactly
        which pixels each province occupies.

        Args:
            default_province_colors (dict[tuple[int, int, int], int]): A mapping of colors to the owning province ID.
            
        Returns:
            dict[int, set[tuple[int, int]]]: A mapping of province IDs to a set of x, coords occupied by the province.
        """
        map_pixels = np.array(self.world_image)
        height, width = map_pixels.shape[:2]

        province_locations = defaultdict(set)
        pixel_data = map_pixels[:, :, :3]
        flat = pixel_data.reshape((-1, 3))

        for i, pixel in enumerate(flat):
            pixel_tuple = tuple(pixel)
            if pixel_tuple in default_province_colors:
                province_id = default_province_colors[pixel_tuple]
                x = i % width
                y = i // width
                province_locations[province_id].add((x, y))

        return dict(province_locations)

    def load_world_areas(self, map_folder: str):
        """Builds the default **areas** dictionary from read game data.
        
        The area data consists of the area's internal ID, display name, and a set of province IDs
        that belong to it.
        
        Example of an area definition:
        
            'ile_de_france_area = { #Champagne and Ile de France
                182 183 185 3070 7960 7961 7962 7963 
            }`
        
        Args:
            map_folder (str): The folder that contains the world definition files.
        
        Returns:
            areas: dict[str, dict[str, str|set[int]]]: A mapping of area ID's to that area's data.
        """
        area_path = os.path.join(map_folder, "area.txt")
        areas: dict[str, dict[str, str|set[int]]] = {}

        pattern = re.compile(r'(\w+)\s*=\s*\{')

        area_id = None
        area_provinces = set()

        with open(area_path, "r", encoding="latin-1") as file:
            for line in file:
                line = line.strip()

                ## Check if this line starts an area definition block.
                if re.match(r"^\s*#?color\s*=", line):
                    continue

                match = pattern.match(line)
                if match:
                    if area_id and area_provinces:
                        areas[area_id] = {
                            "area_id": area_id,
                            "name": EUArea.name_from_id(area_id),
                            "provinces": {p for p in area_provinces if p in self.default_province_data}
                        }

                    area_id = match.group(1)
                    area_provinces = set()
                    continue

                ## End of definition.
                if line == "}":
                    if area_id and area_provinces:
                        areas[area_id] = {
                            "area_id": area_id,
                            "name": EUArea.name_from_id(area_id),
                            "provinces": {p for p in area_provinces if p in self.default_province_data},  # Dict key check
                        }

                    area_id = None
                    continue

                area_provinces.update(map(int, re.findall(r"\b\d+\b", line)))

        return areas

    def load_world_regions(self, map_folder: str):
        """Builds the default **regions** dictionary from read game data.
        
        The region data consists of the regions's internal ID, display name, and a set of string area IDs
        that belong to it.
        
        Example definition for a region:
        
            'poland_region = { # 9 areas
                areas = {
                    wielkopolska_area
                    malopolska_area
                    mazovia_area
                    central_poland_area
                    sandomierz_area
                    kuyavia_area
                    silesia_area
                    lower_silesia_area
                    middle_silesia_area
                }
            }'
        
        Args:
            map_folder (str): The folder that contains the world definition files.
        
        Returns:
            regions: dict[str, dict[str, set[str]]]: A mapping of region ID's to that region's data.
        """
        region_path = os.path.join(map_folder, "region.txt")
        regions: dict[str, dict[str, set[str]]] = {}

        with open(region_path, "r", encoding="latin-1") as file:
            region_pattern = r"(\w+_region)\s*=\s*\{[^}]*?areas\s*=\s*\{([^}]+)\}"
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

    def search(self, exact_matches_only: bool, search_param: str):
        """Searches for a province given a name. Can optionally return only exact matches.
        
        Args:
            exact_matches_only (bool): Whether to only return exact matches.
            search_param (str): The name to search for.
        
        Returns:
            matches (list[EUProvince]): The provinces that match the search param."""
        search_param = search_param.strip()
        if not search_param:
            return []

        if exact_matches_only:
            matches = (p for p in self.provinces.values() if search_param == p.name.lower())
        else:
            matches = (p for p in self.provinces.values() if search_param in p.name.lower())

        matches = sorted(matches, key=lambda p: (p.name, p.province_id))
        return matches
