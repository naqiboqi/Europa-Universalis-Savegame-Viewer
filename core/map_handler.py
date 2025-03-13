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

        self.dragging = False
        self.prev_x = 0
        self.prev_y = 0

        self.scale_factor = 1.1

    def bind_events(self):
        self.tk_canvas.bind("<ButtonPress-1>", self.on_press)
        self.tk_canvas.bind("<B1-Motion>", self.on_drag)
        self.tk_canvas.bind("<ButtonRelease-1>", self.on_release)

        self.tk_canvas.bind("<MouseWheel>", self.on_zoom)
        self.tk_canvas.bind("<Button-4>", self.on_zoom)
        self.tk_canvas.bind("<Button-5>", self.on_zoom)

    def clamp_offsets(self):
        displayer = self.displayer
        map_width, map_height = displayer.map_image.size
        canvas_width, canvas_height = displayer.canvas_size

        max_x = 0
        min_x = -(map_width - canvas_width)

        max_y = 0
        min_y = -(map_height - canvas_height)

        displayer.offset_x = max(min_x, min(displayer.offset_x, max_x))
        displayer.offset_y = max(min_y, min(displayer.offset_y, max_y))

    def on_press(self, event: tk.Event):
        self.dragging = True
        self.prev_x = event.x
        self.prev_y = event.y

    def on_drag(self, event: tk.Event):
        if self.dragging:
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y

            self.displayer.offset_x += dx
            self.displayer.offset_y += dy
            self.clamp_offsets()

            self.displayer.update_display(self.tk_canvas)
            self.prev_x = event.x
            self.prev_y = event.y

    def on_release(self, event: tk.Event):
        self.dragging = False

    def zoom_map(self, cursor_x: float, cursor_y: float, zoom_in: bool=True):
        displayer = self.displayer
        canvas_width, canvas_height = displayer.canvas_size

        if zoom_in and displayer.map_scale >= displayer.max_scale:
            return

        if not zoom_in and displayer.map_scale <= displayer.min_scale:
            return

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
        
        print(new_scale)

    def on_zoom(self, event: tk.Event):
        cursor_x, cursor_y = event.x, event.y

        if event.delta > 0 or event.num == 4:
            self.zoom_map(cursor_x, cursor_y, zoom_in=True)
        elif event.delta < 0 or event.num == 5:
            self.zoom_map(cursor_x, cursor_y, zoom_in=False)