import matplotlib.pyplot as plt
import numpy as np

from enum import Enum
from PIL import Image
from matplotlib import axes, backend_bases, figure
from .colors import EUColors
from .models import EUArea, EUProvince, ProvinceType, ProvinceTypeColor, EURegion, EUWorldData



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



class MapInteractor:
    def __init__(
        self, 
        ax: axes.Axes, 
        province_colors: dict[tuple[int], int], 
        world_provinces: dict[int, EUProvince]):
        self.ax = ax
        self.fig = ax.figure
        self.province_colors = province_colors
        self.world_provinces = world_provinces

        self.fig.canvas.mpl_connect("motion_notify_event", self.on_cursor_move)

    def on_cursor_move(self, event: backend_bases.Event):
        if not (event.xdata or event.ydata):
            return

        x, y = int(event.xdata), int(event.ydata)

        map_pixels = np.array(self.ax.images[0].get_array())
        pixel_color = tuple(map_pixels[y, x][:3])

        province_id = self.province_colors[pixel_color]
        province = self.world_provinces[province_id]

        province_name = province.name if province else "Unknown"
        self.ax.set_title(f"Province: {province_name}")
        self.fig.canvas.draw_idle()



class WorldPainter:
    def __init__(self, colors: EUColors, world_data: EUWorldData):
        self.colors = colors
        self.world_data = world_data
        self.world_image: Image.Image = None
        self.interactor: MapInteractor = None
        self.selector = MapModeSelector()
        self.map_modes = {
            MapMode.POLITICAL: self.draw_map_political,
            MapMode.AREA: self.draw_map_area,
            MapMode.REGION: self.draw_map_region,
            MapMode.DEVELOPMENT: self.draw_map_development,
            MapMode.RELIGION: self.draw_map_religion
        }

    def set_province_pixel_locations(self):
        if not self.world_image:
            self.world_image = self.world_data.world_image

        province_colors = self.colors.default_province_colors
        provinces = self.world_data.provinces
        
        map_pixels = np.array(self.world_image)
        height, width = map_pixels.shape[:2]
        
        for x in range(width):
            for y in range(height):
                pixel_color = tuple(map_pixels[y, x][:3])
                if pixel_color in province_colors:
                    province_id = province_colors[pixel_color]
                    province = provinces[province_id]
                    province.pixel_locations.append((x, y))

    def draw_map(self):
        map_pixels = self.draw_map_area()
        
        world_image = Image.fromarray(map_pixels)
        self.world_image = world_image

        fig, ax = plt.subplots()
        ax.imshow(world_image, interpolation="nearest")
        ax.axis("off")

        plt.show()

    def draw_map_political(self):
        tag_colors = self.colors.tag_colors
        world_provinces = self.world_data.provinces
        map_pixels = np.array(self.world_image)

        for province in world_provinces.values():
            province_type = province.province_type
            if province_type == ProvinceType.OWNED:
                owner_tag = province.owner
                if owner_tag in tag_colors:
                    province_color = tag_colors[owner_tag]
                else:
                    province_color = self.colors.default_province_colors[province.province_id]
                    print(f"DID NOT FIND TAG: {owner_tag} in TAG COLORS!!!")
            elif province_type == ProvinceType.NATIVE:
                province_color = ProvinceTypeColor.NATIVE.value
            elif province_type == ProvinceType.SEA:
                province_color = ProvinceTypeColor.SEA.value
            else:
                province_color = ProvinceTypeColor.WASTELAND.value

            for x, y in province.pixel_locations:
                map_pixels[y, x] = province_color

        return map_pixels
    
    def draw_map_area(self):
        # world_areas = self.world_data.areas
        # map_pixels = np.array(self.world_image)

        # for area in world_areas.values():
        #     provinces = list(area.provinces.values())
        #     first = provinces[0].province_id
        #     province_color = self.colors.default_province_colors[first]
        #     for province in area.provinces.values():
        #         for x, y in province.pixel_locations:
        #             map_pixels[y, x] = province_color
        
        # return map_pixels
        pass

    def draw_map_region(self):
        pass

    def draw_map_development(self):
        pass

    def draw_map_religion(self):
        pass