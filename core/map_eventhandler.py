import tkinter as tk

from PIL import Image, ImageTk
from .models import EUArea, EUProvince, MapMode, ProvinceType, ProvinceTypeColor, EURegion
from .utils import MapUtils
from .world import EUWorldData



class MapEventHandler:
    def __init__(
        self,
        canvas: tk.Canvas,
        canvas_id: int,
        hover_label: tk.Label, 
        map_mode: MapMode,
        world_data: EUWorldData,
        world_image: Image.Image,
        offset_x: int=0,
        offset_y: int=0):
        self.canvas = canvas
        self.canvas_id = canvas_id
        self.hover_label = hover_label
        self.map_mode = map_mode
        self.world_data = world_data
        self.world_image = world_image
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.scale_x = 1
        self.scale_y = 1
        self.dragging = False
        self.start_drag_x = 0
        self.start_drag_y = 0

        self.scaled_image = self.world_image
        self.tk_image = ImageTk.PhotoImage(self.scaled_image)

        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_pan_end)
        self.canvas.bind("<MouseWheel>", self.on_zoom)

    def update(self, data: dict):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_image_in_bounds(self):
        image_width = self.scaled_image.width
        image_height = self.scaled_image.height

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        self.offset_x = MapUtils.get_bounded_offset(
            offset=self.offset_x, 
            image_dim=image_width, 
            canvas_dim=canvas_width)
        self.offset_y = MapUtils.get_bounded_offset(
            offset=self.offset_y,
            image_dim=image_height,
            canvas_dim=canvas_height)

    def on_pan_start(self, event: tk.Event):
        self.dragging = True
        self.start_drag_x = event.x
        self.start_drag_y = event.y

    def on_pan_drag(self, event: tk.Event):
        if self.dragging:
            dx = event.x - self.start_drag_x
            dy = event.y - self.start_drag_y

            self.offset_x += dx
            self.offset_y += dy

            self.set_image_in_bounds()
            self.canvas.coords(self.canvas_id, self.offset_x, self.offset_y)

            self.start_drag_x = event.x
            self.start_drag_y = event.y

    def on_pan_end(self, event: tk.Event):
        self.dragging = False

    def on_zoom(self, event: tk.Event):
        ...

    def update_on_zoom(self):
        ...

    def get_hovered_province(self, x: int, y: int):
        for province in self.world_data.provinces.values():
            if (x, y) in province.pixel_locations:
                return province

        return None

    def on_map_hover(self, event: tk.Event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        adjusted_x = (canvas_x - self.offset_x) / self.scale_x
        adjusted_y = (canvas_y - self.offset_y) / self.scale_y

        province = self.get_hovered_province(int(adjusted_x), int(adjusted_y))
        if not province:
            self.hover_label.config(text=f"Coords: ({adjusted_x:.2f}, {adjusted_y:.2f}) No province found.")
            return

        if self.map_mode in {MapMode.POLITICAL, MapMode.DEVELOPMENT, MapMode.RELIGION}:
            province_type = province.province_type

            if province_type == ProvinceType.OWNED:
                label = f"Coords ({adjusted_x:.2f} {adjusted_y:.2f}, The province of {province.name} with ID {province.province_id}. Owned by {province.owner})"
            elif province_type == ProvinceType.NATIVE:
                label = f"Coords ({adjusted_x:.2f} {adjusted_y:.2f}, The native lands of {province.name} with ID {province.province_id})"
            elif province_type == ProvinceType.SEA:
                label = f"Coords ({adjusted_x:.2f} {adjusted_y:.2f}, The waters of {province.name} with ID {province.province_id})"
            elif province_type == ProvinceType.WASTELAND:
                label = f"Coords ({adjusted_x:.2f} {adjusted_y:.2f}, The wasteland of {province.name} with ID {province.province_id})"

        elif self.map_mode == MapMode.AREA:
            area = self.world_data.province_to_area.get(province.province_id)
            if area:
                if area.area_id == "wasteland_area":
                    label = f"Coords ({adjusted_x:.2f} {adjusted_y:.2f}, The wasteland of {province.name} with ID {province.province_id})"
                elif area.area_id == "lakes_area":
                    label = f"Coords ({adjusted_x:.2f} {adjusted_y:.2f}, The waters of {province.name} with ID {province.province_id})"
                else:
                    label = f"Coords ({adjusted_x:.2f} {adjusted_y:.2f}, The area of {area.name} with ID {area.area_id})"
            else:
                label = f"Coords ({adjusted_x:.2f} {adjusted_y:.2f} Unknown area...."

        elif self.map_mode == MapMode.REGION:
            region = self.world_data.province_to_region.get(province.province_id)
            if region:
                label = f"Coords ({adjusted_x:.2f} {adjusted_y:.2f} The region of {region.name} with ID {region.region_id}"
            else:
                label = f"Coords ({adjusted_x:.2f} {adjusted_y:.2f} Unknown region...."

        self.hover_label.config(text=label)