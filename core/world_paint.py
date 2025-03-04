import math
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk

from enum import Enum
from PIL import Image, ImageTk
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



class MapEventHandler:
    def __init__(
        self,
        canvas: tk.Canvas,
        world_image: Image.Image,
        hover_label: tk.Label, 
        provinces: dict[int, EUProvince]):
        self.canvas = canvas
        self.world_image = world_image
        self.hover_label = hover_label
        self.provinces = provinces

    def on_province_hover(self, event: tk.Event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        # Now calculate the province based on the scaled coordinates

        # Display the province name or handle the hover action
        self.hover_label.config(text=f"Hovering over: ({canvas_x}, {canvas_y})")

    def get_hovered_province(self, x: int, y: int):
        for province in self.provinces.values():
            if (x, y) in province.pixel_locations:
                return province

        return None


class WorldPainter:
    def __init__(self, colors: EUColors, world_data: EUWorldData):
        self.colors = colors
        self.world_data = world_data
        self.selector = MapModeSelector()
        self.map_modes = {
            MapMode.POLITICAL: self.draw_map_political,
            MapMode.AREA: self.draw_map_area,
            MapMode.REGION: self.draw_map_region,
            MapMode.DEVELOPMENT: self.draw_map_development,
            MapMode.RELIGION: self.draw_map_religion
        }

        self.handler: MapEventHandler = None
        self.canvas: tk.Canvas = None
        self.hover_label: tk.Label = None
        self.quit_button: tk.Button = None
        self.root: tk.Tk = None
        self.scroll_x: tk.Scrollbar = None
        self.scroll_y: tk.Scrollbar = None
        self.tk_image: ImageTk.PhotoImage = None
        self.world_image: Image.Image = None

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
                    province.pixel_locations.add((x, y))

    def draw_map(self):
        if not self.selector.map_mode:
            self.selector.map_mode = MapMode.DEVELOPMENT

        map_pixels = self.draw_map_development()
        world_image = Image.fromarray(map_pixels)
        self.world_image = world_image

        if not self.root:
            self.root = tk.Tk()
            self.root.title("Map Viewer")

            self.canvas = tk.Canvas(self.root, width=1200, height=900)
            self.canvas.pack(fill=tk.BOTH, expand=True)

            self.scroll_x = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
            self.scroll_y = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
            self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
            self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

            self.canvas.config(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
            
            self.tk_image = ImageTk.PhotoImage(world_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

            self.quit_button = tk.Button(self.root, text="Quit", command=self.root.quit)
            self.quit_button.pack()

            self.hover_label = tk.Label(self.root, text="Choose a province", bg="white")
            self.hover_label.pack()

            self.handler = MapEventHandler(
                canvas=self.canvas,
                world_image=self.world_image,
                hover_label=self.hover_label, 
                provinces=self.world_data.provinces)
            self.canvas.bind("<Motion>", self.handler.on_province_hover)

        self.root.mainloop()

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

    def development_to_color(self, development: float, max_development: float=200.000):
        normalized = math.log(max(1, development)) / math.log(max(1, max_development))
        intensity = int(255 * normalized)
        return (0, intensity, 0)

    def draw_map_development(self):
        world_provinces = self.world_data.provinces
        map_pixels = np.array(self.world_image)

        max_development = max(province.development for province in world_provinces.values())
        for province in world_provinces.values():
            province_type = province.province_type
            if province_type == ProvinceType.SEA:
                province_color = ProvinceTypeColor.SEA.value
            elif province_type == ProvinceType.WASTELAND:
                province_color = ProvinceTypeColor.WASTELAND.value
            else:
                development = province.development
                province_color = self.development_to_color(development, max_development)

            for x, y in province.pixel_locations:
                map_pixels[y, x] = province_color

        return map_pixels

    def draw_map_religion(self):
        pass