import math
import numpy as np

from PIL import Image, ImageTk
from typing import Optional
from .colors import EUColors
from .models import EUArea, EUProvince, MapMode, ProvinceType, ProvinceTypeColor, EURegion
from .utils import MapUtils
from .world import EUWorldData



CANVAS_WIDTH = 700
CANVAS_HEIGHT = 400


class MapPainter:
    def __init__(self, colors: EUColors, world_data: EUWorldData):
        self.colors = colors
        self.world_data = world_data
        self.map_mode = MapMode.POLITICAL
        self.map_modes = {
            MapMode.POLITICAL: self.draw_map_political,
            MapMode.AREA: self.draw_map_area,
            MapMode.REGION: self.draw_map_region,
            MapMode.DEVELOPMENT: self.draw_map_development,
            MapMode.RELIGION: self.draw_map_religion
        }

    def draw_map_political(self):
        world_provinces = self.world_data.provinces
        map_pixels = np.array(self.world_image)

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
            map_pixels[y_coords, x_coords] = province_color

        return map_pixels

    def draw_map_area(self):
        world_areas = self.world_data.areas
        map_pixels = np.array(self.world_image)

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
        world_regions = self.world_data.regions
        map_pixels = np.array(self.world_image)

        for region in world_regions.values():
            region_pixels = region.pixel_locations
            if region_pixels:
                if region.is_land_region:
                    region_color = MapUtils.seed_color(region.region_id)
                elif region.is_sea_region:
                    region_color = ProvinceTypeColor.SEA.value

                x_coords, y_coords = zip(*region_pixels)
                map_pixels[y_coords, x_coords] = region_color

        wasteland_pixels = set()
        for province in self.world_data.areas.get("wasteland_area"):
            wasteland_pixels.update(province.pixel_locations)

        x_wasteland_coords, y_wasteland_coords = zip(*wasteland_pixels)
        map_pixels[y_wasteland_coords, x_wasteland_coords] = ProvinceTypeColor.WASTELAND.value
        
        lake_pixels = set()
        for province in self.world_data.areas.get("lake_area"):
            lake_pixels.update(province.pixel_locations)

        x_lake_coords, y_lake_coords = zip(*lake_pixels)
        map_pixels[y_lake_coords, x_lake_coords] = ProvinceTypeColor.SEA.value

        return map_pixels

    def development_to_color(self, development: float, max_development: float=200.000):
        normalized = math.log(max(1, development)) / math.log(max(1, max_development))
        intensity = int(255 * normalized)
        return (0, intensity, 0)

    def draw_map_development(self):
        world_provinces = self.world_data.provinces
        map_pixels = np.array(self.world_image)

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
            map_pixels[y_coords, x_coords] = province_color

        return map_pixels

    def draw_map_religion(self):
        pass
