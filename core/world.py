"""
World Data storage for Europa Universalis IV (EU4) savegame viewing.

This module contains the implementation for loading and parsing EU4's world definition files.
These files break the world up into regions, areas, and provinces. The world data 
is then stored in the EUWorldData class and accessed for drawing the map.
"""



import numpy as np
import os
import re

from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from typing import Callable, Optional, Union

from .colors import EUColors
from .models import (
    EUArea, 
    EUCountry, 
    EUProvince, 
    ProvinceType,
    EURegion, 
    EUTradeNode,
    EUTradeNodeParticipant,
    TerrainType)

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
        regions (dict[str, EURegion]): A mapping of region names to the `EURegion` that they represent.
        trade_nodes (dict[str, EUTradeNode]): A mapping of region names to the `EUTradeNode` that they represent.

        province_to_area (dict[int, EUArea]): A mapping of province IDs to the area that they reside in.
        province_to_region (dict[int, EURegion]): A mapping of province IDs to the region that they reside in.
        province_to_trade_node (dict[int, EUTradeNode]): A mapping of province IDs to the trade node that they reside in.

        world_image (Image.Image | None): The world map image, loaded from a definition file.

        default_province_data (dict[int, dict[str, str]]): Default attributes for each province before modifications are loaded from a save file.
        current_province_data (dict[int, dict[str, str]]): Stores current province data, which updates as the game progresses.
        province_locations (dict[int, set[tuple[int]]]): A mapping of province IDs to a set of pixel coordinates in the world image.
        default_area_data (dict[str, dict[str, str | set[int]]]): Default attributes for areas, including associated province IDs.
        default_region_data (dict[str, dict[str, str | set[str]]]): Default attributes for regions, including associated area names.

        trade_goods: dict[str, float]: Trade goods and their respective prices loaded from a savefile.
    """
    def __init__(self):
        ## Current entity data.
        self.areas: dict[str, EUArea] = {}
        self.countries: dict[str, EUCountry] = {}
        self.provinces: dict[int, EUProvince] = {}
        self.regions: dict[str, EURegion] = {}
        self.trade_nodes: dict[str, EUTradeNode] = {}

        ## Mappings.
        self.province_to_area: dict[int, EUArea] = {}
        self.province_to_region: dict[int, EURegion] = {}
        self.province_to_trade_node: dict[int, EUTradeNode] = {}

        self.world_image: Image.Image = None 

        ## Default entity data.
        self.default_province_data: dict[int, dict[str, str]] = {}
        self.province_locations: dict[int, set[tuple[int]]] = {}
        self.current_province_data: dict[int, dict[str, str]] = {}
        self.default_area_data: dict[str, dict[str, str|set[int]]] = {}
        self.default_region_data: dict[str, dict[str, str|set[str]]] = {}

        self.current_save_date: str = None
        self.trade_goods: dict[str, float] = {}

        ## Callback method for displaying messages to the GUI.
        self.update_status_callback: Optional[Callable[[str], None]] = None

    @classmethod
    def load_world_data(cls, maps_folder: str, colors: EUColors):
        """Driver class method that handles loading the default world data.
        
        Args:
            maps_folder (str): The folder that contains the world definition files.
            colors (EUColors): Stores default province and country (tag) colors.
        """
        world = cls()

        world.countries = world.load_countries(colors)

        default_province_data_lines = FileUtils.run_external_reader(folder=maps_folder, filename="province.txt")
        world.default_province_data = world.load_world_provinces(savefile_lines=default_province_data_lines)

        world.world_image = world.load_world_image(maps_folder)
        world.province_locations = world.get_province_pixel_locations(colors.default_province_colors)

        world.default_area_data = world.load_world_areas(maps_folder)

        world.default_region_data = world.load_world_regions(maps_folder)

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

    def load_world_provinces(self, savefile_lines: list[str]):
        """Loads the default **provinces** dictionary from read game data.
        
        Reads over the **savefile_lines** and matches the province definition blocks to extract
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
            savefile_lines (list[str]): The read savefile lines. Is from either default or a loaded savegame.
        
        Returns:
            provinces (dict[int, dict[str, str]]): A mapping of province IDs to that province's data.
        """
        province_id_pattern = re.compile(r'^-(\d+)={')
        patterns = {
            "name": r'name="([^"]+)"',
            "owner": r'owner="([^"]+)"',
            "capital": r'capital="([^"]+)"',
            "hre": r'hre=(yes)',
            "culture": r'culture=([\w]+)',
            "religion": r'religion=([\w]+)',
            "base_tax": r'base_tax=([\d.]+)',
            "base_production": r'base_production=([\d.]+)',
            "base_manpower": r'base_manpower=([\d.]+)',
            "trade_goods": r'trade_goods=([\w]+)',
            "trade_power": r'trade_power=([\d.]+)',
            "center_of_trade": r'center_of_trade=([\d]+)',
            "trade": r'^trade="([\w]+)"',
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

        # Store patterns so we don't have to compile constantly.
        compiled_patterns = {key: re.compile(value) for key, value in patterns.items()}
        important_province_keys = tuple(patterns.keys()) + tuple(fort_buildings.keys())

        provinces: dict[int, dict[str, str]] = {}
        current_province: dict[str, str] = None
        current_province_keys = set()

        line_iter = iter(savefile_lines)
        try:
            while True:
                line = next(line_iter).strip()

                ## "PROV" represents unused provinces.
                if "PROV" in line:
                    continue

                # 'Only' this many acutal provinces exist. The rest are filler.
                # if len(provinces) >= 6414:
                #     raise StopIteration

                ## Check if this line starts a province definition block.
                prov_id = self._try_extract_prov_id(province_id_pattern, line)
                if prov_id is not None:
                    if current_province and "name" in current_province_keys:
                        current_province["province_type"] = self.set_province_type(current_province)
                        provinces[current_province["province_id"]] = current_province

                    current_province = {"province_id": prov_id, "fort_level": 0}
                    current_province_keys = set()
                    continue

                if not current_province:
                    continue

                if current_province_keys and not any(line.startswith(key) for key in important_province_keys):
                    continue

                if "fort=" in line:
                    for fort, level in fort_buildings.items():
                        current_province["fort_level"] = max(current_province["fort_level"], level)

                for key, pattern in compiled_patterns.items():
                    match = pattern.search(line)
                    if match and not key in current_province_keys:
                        current_province_keys.add(key)
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
                        elif key == "hre":
                            current_province[key] = True
                        elif key == "fort_level":
                            continue
                        else:
                            current_province[key] = match.group(1)

        except StopIteration:
            return provinces

    def _try_extract_prov_id(self, pattern: re.Pattern, line: str):
        """Checks if the line contains a province definition.
        
        Lines that start a province definition block start with a '-' followed by an integer:
        
            '-1={
            ......
            ......
            ......
            }'
            
            'For a province with `ID` of 1'
        
        Args:
            pattern (Pattern): The pattern to use for searching.
            line (str): The line to search through.
        
        Returns:
            int: The province id.
        """
        match = pattern.search(line)
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
        pixel_data = map_pixels[:, :, :3] # Only need the RGB channels.
        flat = pixel_data.reshape((-1, 3)) # Flatten pixels for linear iteration.

        for i, pixel in enumerate(flat):
            pixel_tuple = tuple(pixel)

            if pixel_tuple in default_province_colors:
                province_id = default_province_colors[pixel_tuple]
                # Convert flat array index back to 2D image coordinates for province mapping.
                x = i % width
                y = i // width
                province_locations[province_id].add((x, y))

        return dict(province_locations)

    def load_world_areas(self, map_folder: str):
        """Builds the default **areas** dictionary from read game data.
        
        The area data consists of the area's internal ID, display name, and a set of province IDs
        that belong to it.
        
        Example of an area definition:
        
            'ile_de_france_area = {
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

            # Need the province IDs to be ints as that is how they are stored in `self.provinces` dict.
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

        self._build_provinces()

        if self.update_status_callback:
            self.update_status_callback("Building areas....")
        else:
            print("Building areas....")

        self._build_areas()

        if self.update_status_callback:
            self.update_status_callback("Building regions....")
        else:
            print("Building regions....")

        self._build_regions()

        if self.update_status_callback:
            self.update_status_callback("Building trade nodes....")
        else:
            print("Building trade nodes....")

        trade_nodes_data = self._load_trade_nodes(savefile_lines)
        self._build_trade_nodes(trade_nodes_data)

        self.trade_goods = self._load_trade_goods(savefile_lines)

    def _build_provinces(self):
        """Builds the world provinces from the `current_province_data` dict."""
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

    def _process_province(self, province_data: dict):
        """Helper method to process a single province.

        Returns:
            province (EUProvince): The province processed from a `dict`.
        """
        province_id = province_data["province_id"]
        if province_id in self.provinces:
            return self.provinces[province_id].update_from_dict(province_data)

        return EUProvince.from_dict(province_data)

    def _build_areas(self):
        """Builds the world areas from the `default_area_data` dict."""
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

    def _process_area(self, area_data: dict):
        """Helper method to process a single area from a `dict`.
        
        Returns:
            area (EUArea): The area processed from a `dict`.
        """
        area_provinces = {
            province_id: self.provinces[province_id]
            for province_id in area_data["provinces"]
                if province_id in self.provinces
            }

        area_data["provinces"] = area_provinces
        return EUArea.from_dict(area_data)

    def _build_regions(self):
        """Builds the world regions from the `default_region_data` dict."""
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

    def _process_region(self, region_data: dict):
        """Helper method to process a single region.

        Returns:
            region (EURegion): The region processed from a `dict`."""
        region_areas = {
            area_id: self.areas[area_id]
            for area_id in region_data["areas"]
                if area_id in self.areas
        }

        region_data["areas"] = region_areas
        return EURegion.from_dict(region_data)

    def _load_trade_nodes(self, savefile_lines: list[str]):
        """Reads over the **savefile_lines** and matches the lines trade node definition blocks to extract
        each variable's value, and assigns it to each trade node dict.
        
        Example of part of the definition for a trade node:
        
            'node={
                definitions="northwest_territories"
                current=1.900
                local_value=2.398
                outgoing=0.498
                value_added_outgoing=0.498
                retention=0.792
                steer_power=0.500
                ....
                ....
                ....
            }'
        
        Args:
            savefile_lines (list[str]): The read savefile lines. Is from either default or a loaded savegame.
        
        Returns:
            trade_nodes (dict[int, dict[str, str]]): A mapping of trade node IDs to that trade node's data.
        """
        trade_node_id_pattern = re.compile(r'definitions="([^"]+)"')
        node_patterns = {
            "current": r'current=([\d.]+)',
            "local_value": r'local_value=([\d.]+)',
            "outgoing": r'outgoing=([\d.]+)',
            "value_added_outgoing": r'value_added_outgoing=([\d.]+)',
            "retention": r'retention=([\d.]+)',
            "steer_power": r'steer_power=([\d.]+)',
            "num_collectors": r'num_collectors=([\d+])',
            "num_collectors_including_pirates": r'num_collectors_including_pirates=([\d+])',
            "total": r'total=([\d.]+)',
            "p_pow": r'p_pow=([\d.]+)',
            "collector_power": r'collector_power=([\d.]+)',
            "collector_power_including_pirates": r'collector_power_including_pirates=([\d.]+)',
            "pull_power": r'pull_power=([\d.]+)',
            "retain_power": r'retain_power=([\d.]+)',
            "highest_power": r'highest_power=([\d.]+)',
        }

        participant_patterns = {
            "val": r'val=([\d.]+)',
            "already_sent": r'alread_sent=([\d.]+)',
            "power_fraction": r'power_fraction=([\d.]+)',
            "province_power": r'province_power=([\d.]+)',
            "light_ship": r'light_ship=([\d+])',
            "ship_power": r'ship_power=([\d.]+)',
            "money": r'money=([\d.]+)',
            "privateer_mission": r'privateer_mission=([\d.]+)',
            "privateer_money": r'privateer_money=([\d.]+)'
        }

        # Store patterns so we don't have to compile constantly.
        compiled_node_patterns = {key: re.compile(value) for key, value in node_patterns.items()}
        compiled_participant_patterns = {key: re.compile(value) for key, value in participant_patterns.items()}
        country_tag_pattern = re.compile(r'^([A-Z]{3})=\{$')
        top_values_pattern = re.compile(r'\d+\.\d+')
        important_patterns_keys = tuple(node_patterns.keys())

        inside_trade_nodes_block = False
        # Track bracket depth to find where the "trade" block ends.
        bracket_depth = 0

        trade_nodes: dict[str, dict] = {}

        current_origin_number = 0
        current_node: dict[str, str] = None
        current_node_keys = set()

        current_incoming_nodes: list[dict] = []
        current_node_top_countries: list[str] = []
        current_node_top_countries_dict = {}
        current_node_participants: list[EUTradeNodeParticipant] = []

        line_iter = iter(savefile_lines)
        try:
            while True:
                line = next(line_iter).strip()

                # Begin reading the trade block and track depth to figure out where it ends.
                if line == "trade={":
                    inside_trade_nodes_block = True
                    bracket_depth += 1
                    continue

                if inside_trade_nodes_block:
                    if "{" in line:
                        bracket_depth += 1

                    if "}" in line:
                        bracket_depth -= 1
                        if bracket_depth == 0:
                            raise StopIteration

                    if line == "incoming={":
                        # Expects three consecutive lines: 'added_power=', 'added_value=', 'from_node='
                        # Shows the incoming trade nodes that go to the current node.
                        added_power = next(line_iter).strip()
                        added_value = next(line_iter).strip()
                        from_node = next(line_iter).strip()

                        current_incoming_nodes.append({
                            "added_power": float(added_power.split("=")[1]),
                            "added_value": float(added_value.split("=")[1]),
                            "from_node": int(from_node.split("=")[1])
                        })
                        continue

                    if line == "top_power={":
                        # Collect country tags for the most prominent countries in the node until reaching closing brace.
                        # Example:
                        #
                        # top_power={
                        #     "ENG"
                        #     "FLA"
                        #     "BRB"
                        #     ...
                        #     "HAI"
                        # }
                        while True:
                            line = next(line_iter).strip()
                            if line == "}":
                                break

                            current_node_top_countries.append(line)

                        bracket_depth -= 1
                        continue

                    if line == "top_power_values={":
                        # Collect the trade power for each top country in the node, expected in one line.
                        # Example:
                        #
                        # top_power_values={
                        #     128.194 111.503 45.181 ... 2.246 
                        # }
                        line = next(line_iter).strip()

                        values = list(map(float, top_values_pattern.findall(line)))
                        current_node_top_countries_dict = OrderedDict(zip(current_node_top_countries, values))
                        continue

                    if line.startswith("node={"):
                        # Start of a new trade node. If a previous node exists, finalize and store it.
                        if current_node:
                            current_node["incoming_nodes"] = current_incoming_nodes
                            current_node["top_countries"]  = current_node_top_countries_dict
                            current_node["node_participants"] = current_node_participants
                            trade_nodes[current_node["trade_node_id"]] = current_node

                        current_node = {}
                        current_node_keys = set()
                        current_incoming_nodes = []

                        current_node_top_countries = []
                        current_node_top_countries_dict = {}
                        current_node_participants = []
                        continue

                    trade_node_id = self._try_extract_trade_node_id(trade_node_id_pattern, line)
                    if trade_node_id is not None:
                        current_origin_number += 1
                        current_node = {"trade_node_id": trade_node_id, "origin_number": current_origin_number}
                        current_node_keys = set()
                        continue

                    # Check if the line starts the definition for a trade node participant block.
                    # Need to find a possible country tag (three-letter combination).
                    # Example:
                    #
                    # HAI={
                    #     val=41.570
                    #     max_pow=26.924
                    #     max_demand=1.544
                    #     province_power=21.924
                    #     power_fraction=0.025
                    #     money=2.784
                    #     total=1.947
                    #     ...
                    #     ...
                    #     already_sent=30.688
                    # }
                    tag_match = country_tag_pattern.match(line)
                    if tag_match and tag_match.group(1) in self.countries:
                        tag = tag_match.group(1)
                        current_participant = {"tag": tag}
                        inner_bracket_depth = 1

                        while True:
                            line = next(line_iter).strip()
                            if "{" in line:
                                inner_bracket_depth += 1

                            if "}" in line:
                                inner_bracket_depth -= 1
                                # End of the inner participant block.
                                if inner_bracket_depth == 0:
                                    bracket_depth -= 1
                                    break

                            for key, pattern in compiled_participant_patterns.items():
                                match = pattern.search(line)
                                if match:
                                    current_participant[key] = match.group(1)

                        # Must have one of the two keys to be a valid participant, otherwise there would be **way** too many objects.
                        if ("val" in current_participant or "privateer_mission" in current_participant):
                            current_node_participants.append(EUTradeNodeParticipant.from_dict(current_participant))

                        continue

                    if current_node_keys and not any(line.startswith(key) for key in important_patterns_keys):
                        continue

                    for key, pattern in compiled_node_patterns.items():
                        match = pattern.search(line)
                        if match and not key in current_node_keys:
                            current_node_keys.add(key)
                            current_node[key] = match.group(1)

        except StopIteration:
            # Make sure to finalize and store the last node (is always the English Channel)
            if current_node:
                current_node["incoming_nodes"] = current_incoming_nodes
                current_node["top_countries"]  = current_node_top_countries_dict
                current_node["node_participants"] = current_node_participants
                trade_nodes[current_node["trade_node_id"]] = current_node

        return trade_nodes

    def _try_extract_trade_node_id(self, pattern: re.Pattern, line: str):
        """Checks if the line contains a trade node definition.

        Returns:
            trade_node_id (str|None): The ID of the current trade node, if it exists.
        """
        match = pattern.search(line)
        return match.group(1) if match else None

    def _build_trade_nodes(self, trade_nodes_data: dict[str, dict]):
        """Builds the world trade nodes from `trade_nodes_data`."""
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._process_trade_node, trade_node_data)
                for trade_node_id, trade_node_data in trade_nodes_data.items()
            ]

            for future in as_completed(futures):
                trade_node = future.result()
                self.trade_nodes[trade_node.trade_node_id] = trade_node

            for trade_node in self.trade_nodes.values():
                for province_id in trade_node.provinces:
                    self.province_to_trade_node[province_id] = trade_node

    def _process_trade_node(self, trade_node_data: dict):
        """Helper method to process a single trade node.

        Returns:
            trade_node (EUTradeNode): The trade node processed from a `dict`.
        """
        trade_node_id = trade_node_data["trade_node_id"]
        node_provinces = {
            province_id: province
            for province_id, province in self.provinces.items()
                if province.trade == trade_node_id and
                province.province_type != ProvinceType.SEA
        }

        trade_node_data["provinces"] = node_provinces
        return EUTradeNode.from_dict(trade_node_data)

    def _load_trade_goods(self, savefile_lines: list[str]):
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
