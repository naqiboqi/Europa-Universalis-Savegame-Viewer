import matplotlib.pyplot as plt
import numpy as np

from enum import Enum
from PIL import Image

from .colors import EUColors
from .models import EUArea, EUProvince, ProvinceType, EURegion, EUWorldData



class MapMode(Enum):
    POLITICAL = "political"
    AREA = "area"
    REGION = "region"
    DEVELOPMENT = "development"
    RELIGION = "religion"



class MapModeSelector:
    def __init__(self):
        self.map_mode = None

    def select_map_mode(self):
        modes = [mode.value for mode in MapMode]
        while not self.map_mode:
            print("\n".join([f'{i}. {mode.capitalize()}' for i, mode in enumerate(modes, 1)]) + "\n")

            try:
                map_mode = int(input("Select a map mode to view (enter the number): \n"))
            except ValueError:
                print("Please enter a valid selection.\n")
                continue

            if not 1 <= map_mode <= len(modes):
                print("Please enter a valid selection.\n")
                continue

            self.map_mode = MapMode(modes[map_mode - 1])



class WorldPainter:
    def __init__(self, colors: EUColors, world_data: EUWorldData):
        self.colors = colors
        self.world_data = world_data
        self.world_image: Image.Image = None
        self.selector = MapModeSelector()
        # self.map_modes = {
        #     MapMode.POLITICAL: self.draw_political_map,
        #     MapMode.AREA: self.draw_area_map,
        #     MapMode.REGION: self.draw_region_map,
        #     MapMode.DEVELOPMENT: self.draw_development_map,
        #     MapMode.RELIGION: self.draw_religion_map
        # }

    def draw_map(self):
        if not self.world_image:
            self.world_image = self.world_data.world_image
        #if not self.selector.map_mode:
        #    self.selector.select_map_mode()

        self.draw_map_political()

    def draw_map_political(self):
        default_province_colors = self.colors.default_province_colors
        tag_colors = self.colors.tag_colors
        world_provinces = self.world_data.provinces

        map_pixels = np.array(self.world_image)
        height, width = map_pixels.shape[:2]
        for x in range(width):
            for y in range(height):
                pixel_color = tuple(map_pixels[y, x][:3])
                if pixel_color in default_province_colors:
                    province_id = default_province_colors[pixel_color]
                    province = world_provinces[province_id]

                    province_type = province.province_type
                    if province_type == ProvinceType.OWNED:
                        owner_tag = province.owner
                        if owner_tag and owner_tag in tag_colors:
                            tag_color = tag_colors[owner_tag]
                            map_pixels[y, x] = tag_color

                    elif province_type == ProvinceType.NATIVE:
                        map_pixels[y, x] = (203, 164, 103)
                    elif province_type == ProvinceType.SEA:
                        map_pixels[y, x] = (55, 90, 220)
                    else:
                        map_pixels[y, x] = (128, 128, 128)

        world_map = Image.fromarray(map_pixels)
        
        plt.imshow(world_map, interpolation="nearest")
        plt.axis("off")
        plt.show()