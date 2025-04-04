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
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from typing import Union

from .colors import EUColors
from .models import EUArea, EUCountry, EUProvince, ProvinceType, EURegion, TerrainType
from .utils import FileUtils, MapUtils



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
        areas (dict[str, EUArea]): A mapping of area names to the `EUArea` that they reperesent.
        countries (dict[str, EUCountry]): A mapping of country tags (in game identifiers) to `EUCountry` .
        provinces (dict[int, EUProvince]): A mapping of province IDs to the that `EUProvince` they represent.
        terrain (int, TerrainType): A mapping of province Ids to their terrain type.
        regions (dict[str, EURegion]): A mapping of region names to the `EURegion` that they represent.

        province_to_area (dict[int, EUArea]): A mapping of province IDs to the `EUArea` that they reside in.
        province_to_region (dict[int, EURegion]): A mapping of province IDs to the `EURegion` that they reside.
        world_image (Image.Image | None): The world map image, loaded from a definition file.

        default_province_data (dict[int, dict[str, str]]): Default attributes for each province before modifications are loaded from a save file.
        current_province_data (dict[int, dict[str, str]]): Stores current province data, which updates as the game progresses.
        province_locations (dict[int, set[tuple[int]]]): A mapping of province IDs to a set of pixel coordinates in the world image.
        default_area_data (dict[str, dict[str, str | set[int]]]): Default attributes for areas, including associated province IDs.
        default_region_data (dict[str, dict[str, str | set[str]]]): Default attributes for regions, including associated area names.

        trade_goods: dict[str, float]: Trade goods and their respective prices loaded from a savefile.
    """
    def __init__(self):
        self.areas: dict[str, EUArea] = {}
        self.countries: dict[str, EUCountry] = {}
        self.provinces: dict[int, EUProvince] = {}
        self.terrain: dict[int, TerrainType] = {}
        self.regions: dict[str, EURegion] = {}

        self.province_to_area: dict[int, EUArea] = {}
        self.province_to_region: dict[int, EURegion] = {}
        self.world_image: Image.Image = None 

        self.default_province_data: dict[int, dict[str, str]] = {}
        self.province_locations: dict[int, set[tuple[int]]] = {}
        self.current_province_data: dict[int, dict[str, str]] = {}
        self.default_area_data: dict[str, dict[str, str|set[int]]] = {}
        self.default_region_data: dict[str, dict[str, str|set[str]]] = {}

        self.current_save_date: str = None
        self.trade_goods: dict[str, float] = {}

        self.update_status_callback = None

    @classmethod
    def load_world_data(cls, map_folder: str, colors: EUColors):
        """Driver class method that handles loading the default world data.
        
        Args:
            map_folder (str): The folder that contains the world definition files.
            colors (EUColors): Stores default province and country (tag) colors.
        """
        print("Loading EU4 world data....")
        world = cls()

        print("Loading countries....")
        world.countries = world.load_countries(colors)

        print("Loading provinces....")
        default_province_data_lines = FileUtils.run_external_reader(folder=map_folder, filename="province.txt")
        world.default_province_data = world.load_world_provinces(province_data=default_province_data_lines)

        world.world_image = world.load_world_image(map_folder)
        world.province_locations = world.get_province_pixel_locations(colors.default_province_colors)

        print("Loading areas....")
        world.default_area_data = world.load_world_areas(map_folder)

        print("Loading regions....")
        world.default_region_data = world.load_world_regions(map_folder)

        return world

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
            "trade_goods": r'trade_goods=([\w]+)',
            "trade_power": r'trade_power=([\d.]+)',
            "center_of_trade": r'center_of_trade=([\d]+)',
            "trade_node": r'^trade="([\w]+)"',
            "garrison": r'garrison=([\d.]+)',
            "fort_level": r'fort_15th=yes',
            "local_autonomy": r'local_autonomy=([\d.]+)',
            "devastation": r'devastation=([\d.]+)',
            "native_size": r'native_size=(\d+)',
            "native_ferocity": r'native_ferocity=([\d.]+)',
            "native_hostileness": r'native_hostileness=(\d+)',
            "patrol": r'patrol=(\d+)',
            "unrest": r'unrest=([\d.]+)'
        }

        fort_buildings = {
            "fort_15th": 1,
            "fort_16th": 2,
            "fort_17th": 3,
            "fort_18th": 4,
            "fort_19th": 5
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

                    current_province = {"province_id": prov_id, "fort_level": 0}
                    continue

                if current_province is None:
                    continue

                for fort, level in fort_buildings.items():
                    if fort in line:
                        current_province["fort_level"] = max(current_province["fort_level"], level)

                for key, pattern in patterns.items():
                    match = re.search(pattern, line)
                    if match and not key in current_province:
                        if key == "owner":
                            country_tag = match.group(1)
                            ## Check if that tag exists, if not we build a country.
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

    def try_extract_prov_id(self, line: str):
        """Checks if the line contains a province definition.
        
        Lines that start a province definition block start with a '-' followed by an integer:
        
            '-1={
            ......
            ......
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
            province_data (dict): The data for the province to check.
            
        Returns:
            ProvinceType: An enum that represents the province's type.
        """
        is_developed = any(province_data.get(dev) for dev in ["base_tax", "base_production", "base_manpower"])

        ## Only land provinces can have developent.
        if is_developed:
            if province_data.get("owner"):
                return ProvinceType.OWNED

            return ProvinceType.NATIVE

        ## Can only patrol a ship on the sea.
        if province_data.get("patrol"):
            return ProvinceType.SEA

        ## Otherwise it has to be wasteland.
        return ProvinceType.WASTELAND

    def load_world_image(self, map_folder: str):
        """Loads the provinces.bmp file that contains the definitions for each province.
        
        Args:
            map_folder (str): The folder that contains the world definition files.
            
        Returns:
            province_color_map (PIL.Image): The map image.
        """
        provinces_bmp_path = os.path.join(map_folder, "provinces.bmp")
        province_colors_map = Image.open(provinces_bmp_path).convert("RGB")
        return province_colors_map

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
        areas: dict[str, dict[str, str|set[int]]] = {}
        pattern = re.compile(r'(\w+)\s*=\s*\{')

        area_id = None
        area_provinces = set()

        area_data = FileUtils.run_external_reader(map_folder, "area.txt")
        for line in area_data:
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
        regions: dict[str, dict[str, set[str]]] = {}
        region_data = FileUtils.run_external_reader(map_folder, "region.txt", split_lines=False)

        region_pattern = r"(\w+_region)\s*=\s*\{[^}]*?areas\s*=\s*\{([^}]+)\}"
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

    def load_trade_goods(self, savefile_lines: list[str]):
        """Loads the trade good prices from the savefile.
        
        Args:
            savefile_lines (list[str]): The lines from the savefile.
        
        Returns:
            trade_goods (dict[str, float]): The trade good and its associated price.
        """
        trade_goods: dict[str, float] = {}

        inside_goods_block = False
        current_good = None
        bracket_depth = 0

        for line in savefile_lines:
            line = line.strip()

            if line == "change_price={":
                inside_goods_block = True
                bracket_depth += 1
                continue

            if inside_goods_block:
                if line.endswith("={"):
                    current_good = line.split("=")[0]
                    bracket_depth += 1
                    continue

                elif line.startswith("current_price=") and current_good:
                    current_price = float(line.split("=")[1])
                    trade_goods[current_good] = current_price

                elif line == "}":
                    bracket_depth -= 1
                    if bracket_depth == 1:
                        current_good = None
                    elif bracket_depth == 0:
                        break  

        return trade_goods

    def build_world(self, save_folder: str, savefile: str):
        """Builds the **EUProvince**, **EUArea**, **EURegion**, and Country objects by
        updating the default data with the savefile's data.
        
        Populates the **provinces**, **areas**, and **regions** dictionaries to provide
        easier access.
        
        Args:
            save_folder (str): The folder containing the user save file.
            save_file (str): The savefile to read.
        """
        savefile_lines = FileUtils.run_external_reader(save_folder, savefile)
        self.current_save_date = savefile_lines[1].split("=")[1].strip()
        self.current_province_data = self.load_world_provinces(savefile_lines)

        if self.update_status_callback:
            self.update_status_callback("Building provinces....")
        else:
            print("Building provinces....")

        with ThreadPoolExecutor() as executor:
            futures = []
            for province_id, province_data in self.current_province_data.items():
                pixel_locations = self.province_locations.get(province_id)
                if pixel_locations:
                    province_data["pixel_locations"] = pixel_locations
                    futures.append(executor.submit(self._process_province, province_data))

            for future in as_completed(futures):
                province = future.result()
                self.provinces[province.province_id] = province

        if self.update_status_callback:
            self.update_status_callback("Building areas....")
        else:
            print("Building areas....")

        if not self.areas:
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(self._process_area, area_data)
                    for area_id, area_data in self.default_area_data.items()
                ]

            for future in as_completed(futures):
                area = future.result()
                self.areas[area.area_id] = area

            for area in self.areas.values():
                for province_id in area.provinces:
                    self.province_to_area[province_id] = area

        if self.update_status_callback:
            self.update_status_callback("Building regions....")
        else:
            print("Building regions....")

        if not self.regions:
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(self._process_region, region_data)
                    for region_id, region_data in self.default_region_data.items()
                ]

            for future in as_completed(futures):
                region = future.result()
                self.regions[region.region_id] = region

            for region in self.regions.values():
                for area in region:
                    for province_id in area.provinces:
                        self.province_to_region[province_id] = region

        self.trade_goods = self.load_trade_goods(savefile_lines)

    def _process_province(self, province_data: dict):
        """Helper method to process a single province."""
        province_id = province_data["province_id"]
        if province_id in self.provinces:
            return self.provinces[province_id].update_from_dict(province_data)

        return EUProvince.from_dict(province_data)

    def _process_area(self, area_data: dict):
        """Helper method to process a single area."""
        area_provinces = {
            province_id: self.provinces[province_id]
            for province_id in area_data["provinces"]
                if province_id in self.provinces
            }

        area_data["provinces"] = area_provinces
        return EUArea.from_dict(area_data)

    def _process_region(self, region_data: dict):
        """Helper method to process a single region."""
        region_areas = {
            area_id: self.areas[area_id]
            for area_id in region_data["areas"]
                if area_id in self.areas
        }

        region_data["areas"] = region_areas
        return EURegion.from_dict(region_data)

    def search(self, exact_matches_only: bool, search_param: str) -> list[Union[EUProvince, EUArea, EURegion]]:
        """Searches for a location given a name. Can optionally return only exact matches.
        
        Args:
            exact_matches_only (bool): Whether to only return exact matches.
            search_param (str): The name to search for.
        
        Returns:
            matches (list[EUProvince]): The provinces that match the search param."""
        search_param = search_param.strip().lower()
        if not search_param:
            return []

        all_items = []
        all_items.extend(self.provinces.values())
        all_items.extend(self.areas.values())
        all_items.extend(self.regions.values())

        if exact_matches_only:
            matches = (item for item in all_items if item.name.lower() == search_param)
        else:
            matches = (item for item in all_items if search_param in item.name.lower())

        matches = sorted(matches, key=lambda x: x.name)
        return matches
