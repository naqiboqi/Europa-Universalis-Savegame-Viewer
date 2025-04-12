"""
World Map Drawing and Visualization for Europa Universalis IV (EU4) Savegame Viewing.

This module contains the implementation for rendering and coloring the world map based on 
a loaded savegame stored in **EUWorldData**. The map can be displayed in various modes, 
each highlighting different aspects of the game world, such as political boundaries, 
area classifications, and province development.

Map Modes:
    - **Political**: Displays provinces colored by their owning country (tag)'s color.
    - **Area**: Groups provinces by area with a single color for each area.
    - **Region**: Groups provinces and areas by region with a single color for each region.
    - **Development**: Colors provinces based on development level, with higher intensities of green 
        representing higher total development.
    - **Religion**: Shows provinces colored according to their dominant religion.
"""



import math
import numpy as np

from PIL import Image
from typing import Callable, Optional
from .colors import EUColors
from .models import MapMode, ProvinceType, ProvinceTypeColor
from .utils import MapUtils
from .world import EUWorldData



class MapPainter:
    """Handles rendering and coloring of the world map based on `EUWorldData` and `EUColors`.

    This class processes map data from an `EUWorldData` object and applies appropriate colors 
    using an `EUColors` object. It supports multiple map modes, each represented by a specific 
    drawing function.

    Attributes:
        colors (EUColors): Stores default province and country (tag) colors.
        world_data (EUWorldData): Stores the save game state, including definitions for 
            provinces, areas, regions, and countries.
        
        _world_image (Image): The base world map image, loaded from `EUWorldData`.
        _world_image_borderless (Image): A reference to `_world_image`, used for drawing maps 
            without borders.
        
        _image_cache (dict[MapMode, dict]): A cache storing previously rendered map images 
            for each map mode. Each mode stores a bordered and borderless version.
            
            ex: {
                MapMode.POLITICAL: {
                    "border": Image (with borders),
                    "no_border": Image (without borders)
                }
            }
        
        map_mode (MapMode): The currently active map mode (e.g., Political, Area). Set to `MapMode.POLITICAL` by default.
        map_modes (dict[MapMode, Callable]): Mapping `MapMode` values to their respective 
            drawing methods for rendering different map visualizations.
    """
    def __init__(self, colors: EUColors=None, world_data: EUWorldData=None):
        self.colors = colors
        self.world_data = world_data

        self._world_image = self.world_data.world_image if world_data else None
        self._world_image_borderless = self._world_image if world_data else None

        self._image_cache: dict[MapMode, dict] = {}

        self.map_mode = MapMode.POLITICAL
        self.map_modes = {
            MapMode.POLITICAL: self._draw_map_political,
            MapMode.AREA: self._draw_map_area,
            MapMode.REGION: self._draw_map_region,
            MapMode.DEVELOPMENT: self._draw_map_development,
            MapMode.TRADE: self._draw_map_trade,
            MapMode.CULTURE: self._draw_map_culture,
            MapMode.RELIGION: self._draw_map_religion
        }

        self.update_status_callback: Optional[Callable[[str], None]] = None

    def set_base_world_image(self, image: Image.Image):
        self._world_image = image

    def get_cached_map_image(self, borders: bool=True) -> Image.Image:
        """Retrieves the cached map image for the current map mode.
        
        If the requested map image is not in the cache, draws it and then adds it to the cache for future use.

        Args:
            borders (bool, optional): Whether to retrieve the bordered version of the map.
                Defaults to True.

        Returns:
            Image: The cached map image.
        """
        cache_border_key = "border" if borders else "no_border"

        if self.map_mode not in self._image_cache:
            self.draw_map()

        return self._image_cache[self.map_mode].get(cache_border_key)

    def clear_cache(self, mode: MapMode=None):
        """Clears the cache for the image of a specific map mode or all modes."""
        if mode:
            self._image_cache.pop(mode, None)
        else:
            self._image_cache.clear()

    def draw_map(self):
        """Driver that calls the draw method for the current map mode and updates the **map image**.
        
        Returns:
            PIL.Image: The current map image.
        """
        draw_method = self.map_modes.get(self.map_mode, self._draw_map_political)
        map_pixels, map_pixels_borderless = draw_method()

        self._world_image = Image.fromarray(map_pixels)
        self._world_image_borderless = Image.fromarray(map_pixels_borderless)

        self._image_cache[self.map_mode] = {
            "border": Image.fromarray(map_pixels),
            "no_border": Image.fromarray(map_pixels_borderless)
        }

        return self._world_image

    def _draw_map_political(self):
        """Draws the map in the **Political** map mode.
        
        In this mode, each province is colored based on its owning country.  
        - **Owned** provinces are assigned their country's tag color.  
        - **Uncolonized/native** provinces are assigned a default color.  

        Returns:
            tuple (tuple[NDArray, NDArray]): Contains
                - map_pixels_bordered: A NumPy array representing the political map with province borders.
                - map_pixels_borderless: A NumPy array of the same map without borders.
        """
        world_provinces = self.world_data.provinces

        map_pixels_bordered = np.array(self._world_image)
        map_pixels_borderless = map_pixels_bordered.copy()

        # Default colors for unowned province types.
        province_type_colors = {
            ProvinceType.NATIVE: ProvinceTypeColor.NATIVE.value,
            ProvinceType.SEA: ProvinceTypeColor.SEA.value,
            ProvinceType.WASTELAND: ProvinceTypeColor.WASTELAND.value,
        }

        # Precompute pixel locations.
        all_province_pixels = {
            province.province_id: np.array(list(province.pixel_locations))
            for province in world_provinces.values()}

        all_province_border_pixels = {
            province.province_id: np.array(list(province.border_pixels))
            for province in world_provinces.values()}

        for province in world_provinces.values():
            province_pixels = all_province_pixels.get(province.province_id)
            if province_pixels.size == 0:
                continue

            province_type = province.province_type
            if province_type == ProvinceType.OWNED:
                owner_country = province.owner
                province_color = owner_country.tag_color
            else:
                province_color = province_type_colors.get(province_type, None)

            # Transpose (N, 2) array into `x` and `y` arrays for vectorized indexing.
            x_coords, y_coords = province_pixels.T

            map_pixels_bordered[y_coords, x_coords] = province_color
            map_pixels_borderless[y_coords, x_coords] = province_color

            border_pixels = all_province_border_pixels.get(province.province_id)
            if border_pixels.size > 0:
                x_border_coords, y_border_coords = border_pixels.T
                map_pixels_bordered[y_border_coords, x_border_coords] = MapUtils.get_border_color(province_color)

        return map_pixels_bordered, map_pixels_borderless

    def _draw_map_area(self):
        """Draws the map in the **Areas** map mode.
        
        In this mode, each province is colored based on its owning area.  
        - **Areas** are assigned a seeded color.  
        - **Sea** provinces remain blue.  
        - **Wasteland** provinces remain grey.  

        Returns:
            tuple (tuple[NDArray, NDArray]): Contains
                - map_pixels_bordered: A NumPy array representing the area map with area borders.
                - map_pixels_borderless: A NumPy array of the same map without borders.
        """
        world_areas = self.world_data.areas

        map_pixels_bordered = np.array(self._world_image)
        map_pixels_borderless = map_pixels_bordered.copy()

        # Precompute pixel locations.
        all_area_pixels = {
            area.area_id: np.array(list(area.pixel_locations))
            for area in world_areas.values()}

        all_area_border_pixels = {
            area.area_id: np.array(list(area.border_pixels))
            for area in world_areas.values()}

        for area_id, area_pixels in all_area_pixels.items():
            area = world_areas[area_id]
            if area_pixels.size == 0:
                continue

            if area.is_land_area:
                area_color = MapUtils.seed_color(area_id)
            elif area.is_sea_area:
                area_color = ProvinceTypeColor.SEA.value
            elif area.is_wasteland_area:
                area_color = ProvinceTypeColor.WASTELAND.value

            # Transpose (N, 2) array into `x` and `y` arrays for vectorized indexing.
            x_coords, y_coords = area_pixels.T

            map_pixels_bordered[y_coords, x_coords] = area_color
            map_pixels_borderless[y_coords, x_coords] = area_color

            border_pixels = all_area_border_pixels.get(area_id)
            if border_pixels.size > 0:
                x_border_coords, y_border_coords = border_pixels.T
                map_pixels_bordered[y_border_coords, x_border_coords] = MapUtils.get_border_color(area_color)

        return map_pixels_bordered, map_pixels_borderless

    def _draw_map_region(self):
        """Draws the map in the **Regions** map mode.
        
        In this mode, each province/area is colored based on its owning region.  
        - **Regions** are assigned a seeded color.  
        - **Sea** provinces remain blue.  
        - **Wasteland** provinces remain grey.  

        Returns:
            tuple (tuple[NDArray, NDArray]): Contains
                - map_pixels_bordered: A NumPy array representing the region map with region borders.
                - map_pixels_borderless: A NumPy array of the same map without borders.
        """
        world_regions = self.world_data.regions

        map_pixels_bordered = np.array(self._world_image)
        map_pixels_borderless = map_pixels_bordered.copy()

        # Precompute pixel locations.
        all_region_pixels = {
            region.region_id: np.array(list(region.pixel_locations)) 
            for region in world_regions.values()}

        all_region_border_pixels = {
            region.region_id: np.array(list(region.border_pixels)) 
            for region in world_regions.values()}

        for region_id, region_pixels in all_region_pixels.items():
            region = world_regions[region_id]
            if region_pixels.size == 0:
                continue

            if region.is_land_region:
                region_color = MapUtils.seed_color(region_id)
            elif region.is_sea_region:
                region_color = ProvinceTypeColor.SEA.value

            # Transpose (N, 2) array into `x` and `y` arrays for vectorized indexing.
            x_coords, y_coords = region_pixels.T

            map_pixels_bordered[y_coords, x_coords] = region_color
            map_pixels_borderless[y_coords, x_coords] = region_color

            border_pixels = all_region_border_pixels.get(region_id)
            if border_pixels.size > 0:
                x_border_coords, y_border_coords = border_pixels.T
                map_pixels_bordered[y_border_coords, x_border_coords] = MapUtils.get_border_color(region_color)

        wasteland_pixels = set()
        for province in self.world_data.areas.get("wasteland_area"):
            if province.pixel_locations:
                wasteland_pixels.update(province.pixel_locations)

        x_wasteland_coords, y_wasteland_coords = zip(*wasteland_pixels)

        map_pixels_bordered[y_wasteland_coords, x_wasteland_coords] = ProvinceTypeColor.WASTELAND.value
        map_pixels_borderless[y_wasteland_coords, x_wasteland_coords] = ProvinceTypeColor.WASTELAND.value

        lake_pixels = set()
        for province in self.world_data.areas.get("lake_area"):
            if province.pixel_locations:
                lake_pixels.update(province.pixel_locations)

        x_lake_coords, y_lake_coords = zip(*lake_pixels)

        map_pixels_bordered[y_lake_coords, x_lake_coords] = ProvinceTypeColor.SEA.value
        map_pixels_borderless[y_lake_coords, x_lake_coords] = ProvinceTypeColor.SEA.value

        return map_pixels_bordered, map_pixels_borderless

    def _development_to_color(self, development: int, max_development: float=150):
        """Gets the green color for province given its development.
        
        Args:
            development (int): The development of the province.
            max_development (int): The max development in the world or a default value for comparisons.
        
        Returns:
            tuple[int]: The computed province color.
        """
        normalized = math.log(max(1, development)) / math.log(max(1, max_development))
        intensity = int(255 * normalized)
        return (0, intensity, 0)

    def _draw_map_development(self):
        """Draws the map in the **Development** map mode.
        
        In this mode, each province is colored based on its total development.  
        - **Provinces** are colored green, with higher intensities at higher development.  
        - **Sea** provinces remain blue.
        - **Wasteland** provinces remain grey.

        Returns:
            tuple (tuple[NDArray, NDArray]): Contains
                - map_pixels_bordered: A NumPy array representing the development map with province borders.
                - map_pixels_borderless: A NumPy array of the same map without borders.
        """
        world_provinces = self.world_data.provinces

        map_pixels_bordered = np.array(self._world_image)
        map_pixels_borderless = map_pixels_bordered.copy()        

        province_type_colors = {
            ProvinceType.SEA: ProvinceTypeColor.SEA.value,
            ProvinceType.WASTELAND: ProvinceTypeColor.WASTELAND.value,
        }

        max_development = max(province.development for province in world_provinces.values())
        # Precompute pixel locations.
        all_province_pixels = {
            province.province_id: np.array(list(province.pixel_locations))
            for province in world_provinces.values()}

        all_province_border_pixels = {
            province.province_id: np.array(list(province.border_pixels))
            for province in world_provinces.values()}

        for province in world_provinces.values():
            province_pixels = all_province_pixels.get(province.province_id)
            if province_pixels.size == 0:
                continue

            province_color = province_type_colors.get(province.province_type)
            if province_color is None:
                province_color = self._development_to_color(province.development, max_development)

            # Transpose (N, 2) array into `x` and `y` arrays for vectorized indexing.
            x_coords, y_coords = province_pixels.T

            map_pixels_bordered[y_coords, x_coords] = province_color
            map_pixels_borderless[y_coords, x_coords] = province_color

            border_pixels = all_province_border_pixels.get(province.province_id)
            if border_pixels.size > 0:
                x_border_coords, y_border_coords = border_pixels.T
                map_pixels_bordered[y_border_coords, x_border_coords] = MapUtils.get_border_color(province_color)

        return map_pixels_bordered, map_pixels_borderless

    def _draw_map_trade(self):
        """Draws the map in the **Trade** map mode.
        
        In this mode, each province is colored based on the trade node that it belongs to.  
        - **Regions** are assigned a seeded color.  
        - **Sea** provinces remain blue.  
        - **Wasteland** provinces remain grey.  

        Returns:
            tuple (tuple[NDArray, NDArray]): Contains
                - map_pixels_bordered: A NumPy array representing the trade node map with borders.
                - map_pixels_borderless: A NumPy array of the same map without borders.
        """
        world_nodes = self.world_data.trade_nodes
        
        map_pixels_bordered = np.array(self._world_image)
        map_pixels_borderless = map_pixels_bordered.copy()

        all_node_pixels = {
            node.trade_node_id: np.array(list(node.pixel_locations))
            for node in world_nodes.values()
        }

        all_node_border_pixels = {
            node.trade_node_id: np.array(list(node.border_pixels))
            for node in world_nodes.values()
        }

        for trade_node in world_nodes.values():
            node_pixels = all_node_pixels.get(trade_node.trade_node_id)
            if node_pixels.size == 0:
                continue

            node_color = MapUtils.seed_color(name=trade_node.trade_node_id)

            # Transpose (N, 2) array into `x` and `y` arrays for vectorized indexing.
            x_coords, y_coords = node_pixels.T

            map_pixels_bordered[y_coords, x_coords] = node_color
            map_pixels_borderless[y_coords, x_coords] = node_color

            border_pixels = all_node_border_pixels.get(trade_node.trade_node_id)
            if border_pixels.size > 0:
                x_border_coords, y_border_coords = border_pixels.T
                map_pixels_bordered[y_border_coords, x_border_coords] = MapUtils.get_border_color(node_color)

        wasteland_pixels = set()
        for province in self.world_data.areas.get("wasteland_area"):
            if province.pixel_locations:
                wasteland_pixels.update(province.pixel_locations)

        x_wasteland_coords, y_wasteland_coords = zip(*wasteland_pixels)

        map_pixels_bordered[y_wasteland_coords, x_wasteland_coords] = ProvinceTypeColor.WASTELAND.value
        map_pixels_borderless[y_wasteland_coords, x_wasteland_coords] = ProvinceTypeColor.WASTELAND.value

        lake_pixels = set()
        for province in self.world_data.areas.get("lake_area"):
            if province.pixel_locations:
                lake_pixels.update(province.pixel_locations)

        x_lake_coords, y_lake_coords = zip(*lake_pixels)

        map_pixels_bordered[y_lake_coords, x_lake_coords] = ProvinceTypeColor.SEA.value
        map_pixels_borderless[y_lake_coords, x_lake_coords] = ProvinceTypeColor.SEA.value

        return map_pixels_bordered, map_pixels_borderless

    def _draw_map_culture(self):
        """Draws the map in the **Culture** map mode.
        
        In this mode, each province is colored based on its dominant culture.  
        - **Land** provinces are assigned a seeded color.  
        - **Sea** provinces remain blue.  
        - **Wasteland** provinces remain grey.  

        Returns:
            tuple (tuple[NDArray, NDArray]): Contains
                - map_pixels_bordered: A NumPy array representing the culture map with province borders.
                - map_pixels_borderless: A NumPy array of the same map without borders.
        """
        world_provinces = self.world_data.provinces

        map_pixels_bordered = np.array(self._world_image)
        map_pixels_borderless = map_pixels_bordered.copy()

        province_type_colors = {
            ProvinceType.SEA: ProvinceTypeColor.SEA.value,
            ProvinceType.WASTELAND: ProvinceTypeColor.WASTELAND.value,
        }

        # Precompute pixel locations.
        all_province_pixels = {
            province.province_id: np.array(list(province.pixel_locations))
            for province in world_provinces.values()}

        all_province_border_pixels = {
            province.province_id: np.array(list(province.border_pixels))
            for province in world_provinces.values()}

        for province in world_provinces.values():
            province_pixels = all_province_pixels.get(province.province_id)
            if province_pixels.size == 0:
                continue

            province_type = province.province_type
            if province_type in province_type_colors:
                province_color = province_type_colors.get(province_type, None)
            else:
                province_culture = province.culture
                if province_culture:
                    province_color = MapUtils.seed_color(name=province_culture)
                else:
                    province_color = MapUtils.seed_color(name="No Culture")

            # Transpose (N, 2) array into `x` and `y` arrays for vectorized indexing.
            x_coords, y_coords = province_pixels.T

            map_pixels_bordered[y_coords, x_coords] = province_color
            map_pixels_borderless[y_coords, x_coords] = province_color

            border_pixels = all_province_border_pixels.get(province.province_id)
            if border_pixels.size > 0:
                x_border_coords, y_border_coords = border_pixels.T
                map_pixels_borderless[y_border_coords, x_border_coords] = MapUtils.get_border_color(province_color)

        return map_pixels_bordered, map_pixels_borderless

    def _draw_map_religion(self):
        """Draws the map in the **Religion** map mode.
        
        In this mode, each province is colored based on its dominant religion.  
        - **Land** provinces are assigned a seeded color.  
        - **Sea** provinces remain blue.  
        - **Wasteland** provinces remain grey.  

        Returns:
            tuple (tuple[NDArray, NDArray]): Contains
                - map_pixels_bordered: A NumPy array representing the religion map with province borders.
                - map_pixels_borderless: A NumPy array of the same map without borders.
        """
        world_provinces = self.world_data.provinces

        map_pixels_bordered = np.array(self._world_image)
        map_pixels_borderless = map_pixels_bordered.copy()

        province_type_colors = {
            ProvinceType.SEA: ProvinceTypeColor.SEA.value,
            ProvinceType.WASTELAND: ProvinceTypeColor.WASTELAND.value,
        }

        # Precompute pixel locations.
        all_province_pixels = {
            province.province_id: np.array(list(province.pixel_locations))
            for province in world_provinces.values()}

        all_province_border_pixels = {
            province.province_id: np.array(list(province.border_pixels))
            for province in world_provinces.values()}

        for province in world_provinces.values():
            province_pixels = all_province_pixels.get(province.province_id)
            if province_pixels.size == 0:
                continue

            province_type = province.province_type
            if province_type in province_type_colors:
                province_color = province_type_colors.get(province_type, None)
            else:
                province_religion = province.religion
                if province_religion:
                    province_color = MapUtils.seed_color(name=province_religion)
                else:
                    province_color = MapUtils.seed_color(name="No Religion")

            # Transpose (N, 2) array into `x` and `y` arrays for vectorized indexing.
            x_coords, y_coords = province_pixels.T

            map_pixels_bordered[y_coords, x_coords] = province_color
            map_pixels_borderless[y_coords, x_coords] = province_color

            border_pixels = all_province_border_pixels.get(province.province_id)
            if border_pixels.size > 0:
                x_border_coords, y_border_coords = border_pixels.T
                map_pixels_borderless[y_border_coords, x_border_coords] = MapUtils.get_border_color(province_color)

        return map_pixels_bordered, map_pixels_borderless
