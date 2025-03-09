import math
import numpy as np
import tkinter as tk

from PIL import Image, ImageTk
from .colors import EUColors
from .map_eventhandler import MapEventHandler
from .models import EUArea, EUProvince, MapMode, ProvinceType, ProvinceTypeColor, EURegion
from .utils import MapUtils
from .world import EUWorldData



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

        self.canvas: tk.Canvas = None
        self.canvas_id: int = None
        self.handler: MapEventHandler = None
        self.hover_label: tk.Label = None
        self.quit_button: tk.Button = None
        self.root: tk.Tk = None
        self.tk_image: ImageTk.PhotoImage = None
        self.world_image: Image.Image = None

    def set_map_mode(self, map_mode: MapMode):
        self.map_mode = map_mode
        self.draw_map()

    def draw_map(self):
        print("Drawing map....")

        self.world_image = self.world_data.world_image
        draw_method = self.map_modes.get(self.map_mode, self.draw_map_political)
        map_pixels = draw_method()

        self.world_image = Image.fromarray(map_pixels)
        if not self.root:
            self.root = tk.Tk()     
            self.root.title("Map Viewer")

            self.tk_image = ImageTk.PhotoImage(self.world_image)

            button_frame = tk.Frame(self.root)
            button_frame.pack(side=tk.TOP, fill=tk.X)
            for map_mode in self.map_modes.keys():
                button = tk.Button(
                    button_frame, 
                    text=map_mode.name, 
                    command=lambda m=map_mode: self.set_map_mode(m))
                button.pack(fill=tk.X, padx=5, pady=5)
            
            self.canvas = tk.Canvas(self.root, width=1200, height=600)
            self.canvas.pack(fill=tk.BOTH, expand=True)

            self.quit_button = tk.Button(self.root, text="Quit", command=self.root.destroy)
            self.quit_button.pack()

            self.hover_label = tk.Label(self.root, text="Choose a Province", bg="white")
            self.hover_label.pack()

            self.handler = MapEventHandler(
                canvas=self.canvas,
                map_mode=self.map_mode,
                world_image=self.world_image,
                hover_label=self.hover_label, 
                provinces=self.world_data.provinces)
            self.canvas.bind("<Motion>", self.handler.on_map_hover)

            self.root.mainloop()
        else:
            self.tk_image = ImageTk.PhotoImage(self.world_image)
            if self.canvas_id:
                self.canvas.itemconfig(self.canvas_id, image=self.tk_image)
            else:
                x_center = (self.canvas.winfo_width() - self.world_image.width) // 2
                y_center = (self.canvas.winfo_height() - self.world_image.height) // 2
                self.canvas_id = self.canvas.create_image(x_center, y_center, anchor=tk.CENTER, image=self.tk_image)

            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            self.handler = MapEventHandler(
                canvas=self.canvas,
                map_mode=self.map_mode,
                world_image=self.world_image,
                hover_label=self.hover_label, 
                provinces=self.world_data.provinces)
            self.canvas.bind("<Motion>", self.handler.on_map_hover)

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

        return None

    def development_to_color(self, development: float, max_development: float=200.000):
        normalized = math.log(max(1, development)) / math.log(max(1, max_development))
        intensity = int(255 * normalized)
        return (0, intensity, 0)

    def draw_map_development(self):
        world_provinces = self.world_data.provinces
        map_pixels = np.array(self.world_image)

        max_development = max(p.development for p in world_provinces.values())

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
