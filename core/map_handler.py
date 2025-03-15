from __future__ import annotations

import tkinter as tk

from PIL import Image
from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from . import MapDisplayer



class MapHandler:
    def __init__(self, displayer: MapDisplayer, tk_canvas: tk.Canvas):
        self.displayer = displayer
        self.tk_canvas = tk_canvas
        self.world_data = self.displayer.painter.world_data

        self.pan_animation_id = None
        self.cursor_movement = 0
        self.dragging = False
        self.prev_x = 0
        self.prev_y = 0
        self.start_x = 0
        self.start_y = 0

        self.scale_factor = 1.1
        self.zooming = False

    def clamp_offsets(self, target_offset_x: int=None, target_offset_y: int=None):
        displayer = self.displayer
        map_width, map_height = displayer.map_image.size
        canvas_width, canvas_height = displayer.canvas_size

        max_x = 0
        min_x = -(map_width - canvas_width)

        max_y = 0
        min_y = -(map_height - canvas_height)

        if target_offset_x is not None and target_offset_y is not None:
            target_offset_x = max(min_x, min(target_offset_x, max_x))
            target_offset_y = max(min_y, min(target_offset_y, max_y))
            return target_offset_x, target_offset_y
        else:
            displayer.offset_x = max(min_x, min(displayer.offset_x, max_x))
            displayer.offset_y = max(min_y, min(displayer.offset_y, max_y))

    def bind_events(self):
        self.tk_canvas.bind("<Motion>", self.on_hover)
        self.tk_canvas.bind("<ButtonPress-1>", self.on_press)
        self.tk_canvas.bind("<B1-Motion>", self.on_drag)
        self.tk_canvas.bind("<ButtonRelease-1>", self.on_release)

        self.tk_canvas.bind("<MouseWheel>", self.on_zoom)
        self.tk_canvas.bind("<Button-4>", self.on_zoom)
        self.tk_canvas.bind("<Button-5>", self.on_zoom)

    def canvas_to_image_coords(self, canvas_x: int|float, canvas_y: int|float):
        displayer = self.displayer
        image_x = int((canvas_x - displayer.offset_x) / displayer.map_scale)
        image_y = int((canvas_y - displayer.offset_y) / displayer.map_scale)

        return (image_x, image_y)

    def get_province_at(self, image_x: int, image_y: int):
        for province in self.world_data.provinces.values():
            if (image_x, image_y) in province.pixel_locations:
                return province

        return None

    def on_hover(self, event: tk.Event):
        displayer = self.displayer
        canvas_x = event.x
        canvas_y = event.y

        image_x, image_y = self.canvas_to_image_coords(canvas_x, canvas_y)
        if not (0 <= image_x < displayer.original_map.width or
                0 <= image_y < displayer.original_map.height):
            return

        province = self.get_province_at(image_x, image_y)
        if not province:
            return

        displayer.window["-MULTILINE-"].update(province.name)

    def on_click(self, event: tk.Event):
        if self.pan_animation_id:
            self.tk_canvas.after_cancel(self.pan_animation_id)

        displayer = self.displayer
        canvas_x = event.x
        canvas_y = event.y
        image_x, image_y = self.canvas_to_image_coords(canvas_x, canvas_y)

        province = self.get_province_at(image_x, image_y)
        if not province:
            return

        bbox = province.bounding_box
        if not bbox:
            return

        min_x, max_x, min_y, max_y = bbox
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2

        canvas_width, canvas_height = self.displayer.canvas_size

        target_offset_x = (canvas_width // 2) - (center_x * displayer.map_scale)
        target_offset_y = (canvas_height // 2) - (center_y * displayer.map_scale)
        target_offset_x, target_offset_y = self.clamp_offsets(target_offset_x, target_offset_y)

        def animate_pan(step: int=0, pan_speed: int=10):
            dx = target_offset_x - displayer.offset_x
            dy = target_offset_y - displayer.offset_y

            if abs(dx) < 1 and abs(dy) < 1:
                displayer.offset_x = target_offset_x
                displayer.offset_y = target_offset_y
                self.clamp_offsets()
                self.tk_canvas.coords(displayer.image_id, target_offset_x, target_offset_y)
                return

            displayer.offset_x += dx * 0.1
            displayer.offset_y += dy * 0.1

            self.tk_canvas.coords(displayer.image_id, displayer.offset_x, displayer.offset_y)

            self.pan_animation_id = self.tk_canvas.after(pan_speed, animate_pan)

        animate_pan()

    def on_press(self, event: tk.Event):
        self.dragging = True
        self.prev_x = event.x
        self.prev_y = event.y
        self.start_x = event.x
        self.start_y = event.y
        self.cursor_movement = 0

    def on_drag(self, event: tk.Event):
        displayer = self.displayer

        if self.dragging:
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y

            self.cursor_movement += (dx ** 2 + dy ** 2) ** 0.5
            self.displayer.offset_x += dx
            self.displayer.offset_y += dy
            self.clamp_offsets()

            self.tk_canvas.coords(displayer.image_id, displayer.offset_x, displayer.offset_y)

            self.prev_x = event.x
            self.prev_y = event.y

    def on_release(self, event: tk.Event):
        self.dragging = False

        cursor_move_threshold = 1
        if self.cursor_movement < cursor_move_threshold:
            self.on_click(event)

    def zoom_map(self, cursor_x: float, cursor_y: float, zoom_in: bool=True):
        if self.zooming:
            return

        displayer = self.displayer
        canvas_width, canvas_height = displayer.canvas_size

        if zoom_in and displayer.map_scale >= displayer.max_scale:
            self.zooming = False
            return

        if not zoom_in and displayer.map_scale <= displayer.min_scale:
            self.zooming = False
            return

        self.zooming = True
        new_scale = displayer.map_scale * self.scale_factor if zoom_in else displayer.map_scale / self.scale_factor
        new_scale = min(displayer.max_scale, max(displayer.min_scale, new_scale))

        scaled_width = int(displayer.original_map.width * new_scale)
        scaled_height = int(displayer.original_map.height * new_scale)

        map_cursor_x = (cursor_x - displayer.offset_x) / displayer.map_scale
        map_cursor_y = (cursor_y - displayer.offset_y) / displayer.map_scale

        new_offset_x = cursor_x - map_cursor_x * new_scale
        new_offset_y = cursor_y - map_cursor_y * new_scale

        new_offset_x = min(0, max(canvas_width - scaled_width, new_offset_x))
        new_offset_y = min(0, max(canvas_height - scaled_height, new_offset_y))

        displayer.offset_x = new_offset_x
        displayer.offset_y = new_offset_y
        displayer.map_scale = new_scale
        self.clamp_offsets()

        self.displayer.map_image = self.displayer.original_map.resize(
            (scaled_width, scaled_height), Image.Resampling.LANCZOS)
        self.displayer.update_display(self.tk_canvas)

        self.tk_canvas.after(50, lambda: setattr(self, 'zooming', False))

    def on_zoom(self, event: tk.Event):
        cursor_x, cursor_y = event.x, event.y

        if event.delta > 0 or event.num == 4:
            self.zoom_map(cursor_x, cursor_y, zoom_in=True)
        elif event.delta < 0 or event.num == 5:
            self.zoom_map(cursor_x, cursor_y, zoom_in=False)