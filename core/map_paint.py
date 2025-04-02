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
    def __init__(self, colors: EUColors, world_data: EUWorldData):
        self.colors = colors
        self.world_data = world_data

        self._world_image = self.world_data.world_image
        self._world_image_borderless = self._world_image

        self._image_cache: dict[MapMode, dict] = {}

        self.map_mode = MapMode.POLITICAL
        self.map_modes = {
            MapMode.POLITICAL: self.draw_map_political,
            MapMode.AREA: self.draw_map_area,
            MapMode.REGION: self.draw_map_region,
            MapMode.DEVELOPMENT: self.draw_map_development,
            MapMode.RELIGION: self.draw_map_religion
        }

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

    def draw_map(self):
        """Driver that calls the draw method for the current map mode and updates the **map image**.
        
        Returns:
            PIL.Image: The current map image.
        """
        draw_method = self.map_modes.get(self.map_mode, self.draw_map_political)
        map_pixels, map_pixels_borderless = draw_method()

        self._world_image = Image.fromarray(map_pixels)
        self._world_image_borderless = Image.fromarray(map_pixels_borderless)

        self._image_cache[self.map_mode] = {
            "border": Image.fromarray(map_pixels),
            "no_border": Image.fromarray(map_pixels_borderless)
        }

        return self._world_image

    def draw_map_political(self):
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

        ## Default colors
        province_type_colors = {
            ProvinceType.NATIVE: ProvinceTypeColor.NATIVE.value,
            ProvinceType.SEA: ProvinceTypeColor.SEA.value,
            ProvinceType.WASTELAND: ProvinceTypeColor.WASTELAND.value,
        }

        for province in world_provinces.values():
            province_type = province.province_type

            if province_type == ProvinceType.OWNED:
                owner_country = province.owner
                province_color = owner_country.tag_color
            else:
                province_color = province_type_colors.get(province_type, None)

            x_coords, y_coords = zip(*province.pixel_locations)

            map_pixels_bordered[y_coords, x_coords] = province_color
            map_pixels_borderless[y_coords, x_coords] = province_color

            x_border_coords, y_border_coords = zip(*province.border_pixels)
            map_pixels_bordered[y_border_coords, x_border_coords] = MapUtils.get_border_color(province_color)

        return map_pixels_bordered, map_pixels_borderless

    def draw_map_area(self):
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
        map_pixels = np.array(self._world_image)

        for area in world_areas.values():
            area_pixels = area.pixel_locations
            if area_pixels:
                if area.is_land_area:
                    area_color = MapUtils.seed_color(area.area_id)
                elif area.is_sea_area:
                    area_color = ProvinceTypeColor.SEA.value
                elif area.is_wasteland_area:
                    area_color = ProvinceTypeColor.WASTELAND.value

                x_coords, y_coords = zip(*area_pixels)
                map_pixels[y_coords, x_coords] = area_color

        return map_pixels

    def draw_map_region(self):
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
        map_pixels = np.array(self._world_image)

        for region in world_regions.values():
            region_pixels = region.pixel_locations
            if region_pixels:
                if region.is_land_region:
                    region_color = MapUtils.seed_color(region.region_id)
                elif region.is_sea_region:
                    region_color = ProvinceTypeColor.SEA.value

                x_coords, y_coords = zip(*region_pixels)
                map_pixels[y_coords, x_coords] = region_color

        ## Separate check because wastelands belong to an area, but are not part of any region.
        wasteland_pixels = set()
        for province in self.world_data.areas.get("wasteland_area"):
            wasteland_pixels.update(province.pixel_locations)

        x_wasteland_coords, y_wasteland_coords = zip(*wasteland_pixels)
        map_pixels[y_wasteland_coords, x_wasteland_coords] = ProvinceTypeColor.WASTELAND.value

        ## Separate check because lakes belong to an area, but are not part of any region.
        lake_pixels = set()
        for province in self.world_data.areas.get("lake_area"):
            lake_pixels.update(province.pixel_locations)

        x_lake_coords, y_lake_coords = zip(*lake_pixels)
        map_pixels[y_lake_coords, x_lake_coords] = ProvinceTypeColor.SEA.value

        return map_pixels

    def development_to_color(self, development: int, max_development: float=150):
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

    def draw_map_development(self):
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

        max_development = max(province.development for province in world_provinces.values())

        province_type_colors = {
            ProvinceType.SEA: ProvinceTypeColor.SEA.value,
            ProvinceType.WASTELAND: ProvinceTypeColor.WASTELAND.value,
        }

        for province in world_provinces.values():
            province_color = province_type_colors.get(province.province_type)

            if province_color is None:
                province_color = self.development_to_color(province.development, max_development)

            x_coords, y_coords = zip(*province.pixel_locations)

            map_pixels_bordered[y_coords, x_coords] = province_color
            map_pixels_borderless[y_coords, x_coords] = province_color

            x_border_coords, y_border_coords = zip(*province.border_pixels)
            map_pixels_bordered[y_border_coords, x_border_coords] = MapUtils.get_border_color(province_color)

        return map_pixels_bordered, map_pixels_borderless

    def draw_map_religion(self):
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

        ## Default colors
        province_type_colors = {
            ProvinceType.SEA: ProvinceTypeColor.SEA.value,
            ProvinceType.WASTELAND: ProvinceTypeColor.WASTELAND.value,
        }

        for province in world_provinces.values():
            province_type = province.province_type

            if province_type in province_type_colors:
                province_color = province_type_colors.get(province_type, None)
            else:
                province_religion = province.religion
                if province_religion:
                    province_color = MapUtils.seed_color(name=province_religion)
                else:
                    province_color = MapUtils.seed_color(name="No Religion")

            x_coords, y_coords = zip(*province.pixel_locations)

            map_pixels_bordered[y_coords, x_coords] = province_color
            map_pixels_borderless[y_coords, x_coords] = province_color

            x_border_coords, y_border_coords = zip(*province.border_pixels)
            map_pixels_borderless[y_border_coords, x_border_coords] = MapUtils.get_border_color(province_color)

        return map_pixels_bordered, map_pixels_borderless
