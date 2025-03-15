from __future__ import annotations

import FreeSimpleGUI as sg
import tkinter as tk

from PIL import Image, ImageTk
from . import MapHandler
from . import MapPainter
from .models import MapMode


CANVAS_WIDTH_MAX = 1400



class MapDisplayer:
    def __init__(self, painter: MapPainter):
        self.painter = painter

        self.canvas_size = ()
        self.handler: MapHandler = None
        self.image_id = None
        self.map_image = None
        self.tk_image = None
        self.window = None

        self.max_scale = 5.0
        self.map_scale = 1.0
        self.min_scale = 1.0

        self.offset_x = 0
        self.offset_y = 0

    def image_to_tkimage(self, image: Image.Image):
        return ImageTk.PhotoImage(image)

    def scale_image_to_fit(self, image: Image.Image):
        width, height = image.size
        canvas_width, canvas_height = self.canvas_size

        self.map_scale = min(canvas_width / width, canvas_height / height)
        self.max_scale = 10 * self.map_scale
        self.min_scale = self.map_scale

        return image.resize((self.canvas_size), Image.Resampling.LANCZOS)

    def update_display(self, tk_canvas: tk.Canvas):
        self.tk_image = self.image_to_tkimage(self.map_image)
        tk_canvas.itemconfig(self.image_id, image=self.tk_image)
        tk_canvas.coords(self.image_id, self.offset_x, self.offset_y)

    def update_map_mode(self, map_mode: MapMode, tk_canvas: tk.Canvas):
        if map_mode == self.painter.map_mode:
            return

        self.painter.map_mode = map_mode
        self.original_map = self.painter.draw_map()

        self.map_image = self.original_map.resize(self.map_image.size, Image.Resampling.LANCZOS)
        self.tk_image = self.image_to_tkimage(self.map_image)
        tk_canvas.itemconfig(self.image_id, image=self.tk_image)
        tk_canvas.coords(self.image_id, self.offset_x, self.offset_y)

    def display_map(self):
        sg.theme("DarkBlue")

        self.original_map = self.painter.draw_map()
        map_width, map_height = self.original_map.size

        canvas_height = int(CANVAS_WIDTH_MAX * (map_height / map_width))
        self.canvas_size = (CANVAS_WIDTH_MAX, canvas_height)
        self.map_image = self.scale_image_to_fit(self.original_map)

        layout = [
            [sg.Canvas(background_color="black", size=self.canvas_size, key="-CANVAS-")],
            [sg.Multiline(
                default_text="Hover over an area to get more information!", 
                disabled=True, 
                justification="center",
                size=(120, 3),
                write_only=True, 
                key="-MULTILINE-")
            ],
            [sg.HorizontalSeparator(key="-HSEP-")],
            [sg.Button(mode.name, key=mode.value) for mode in self.painter.map_modes],
            ]
        window = sg.Window("EU4 Map Viewer", layout, finalize=True, return_keyboard_events=True)
        window.move_to_center()
        self.window = window

        canvas = window["-CANVAS-"]
        tk_canvas: tk.Canvas = canvas.TKCanvas

        self.tk_image = self.image_to_tkimage(self.map_image)
        self.image_id = tk_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.handler = MapHandler(self, tk_canvas)
        self.handler.bind_events()

        mode_names = {mode.value: mode for mode in self.painter.map_modes}
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, "Exit"):
                break

            if event in mode_names:
                self.update_map_mode(mode_names[event], tk_canvas)

        window.close()