from __future__ import annotations

import FreeSimpleGUI as sg
import tkinter as tk

from PIL import Image, ImageTk
from . import MapHandler
from . import MapPainter
from .models import MapMode


CANVAS_WIDTH_MAX = 1400

LIGHT_TEXT = "#d2d2d2"
WHITE_TEXT = "#ffffff"
GOLD_ACCENT = "#ffcc00"
TEAL_ACCENT = "#0e6f74"
FRAME_BG = "#2c2f36"
FRAME_TITLE_COLOR = GOLD_ACCENT
RED_BANNER = "#9e2a2f"
DARK_BG = "#1d1f21"
FRAME_BG = "#2b2b2b"
BUTTON_BG = "#5d8fae"
BUTTON_FG = "#ffffff" 
LISTBOX_BG = "#2b2b2b"
LISTBOX_FG = LIGHT_TEXT



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

    def reset_display(self, tk_canvas: tk.Canvas):
        self.offset_x = 0
        self.offset_y = 0
        self.map_image = self.scale_image_to_fit(self.original_map)
        self.update_display(tk_canvas)

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
            [sg.Column(
                [
                    [sg.Text(
                        "Map Information", 
                        font=("Times New Roman", 14, "bold"), 
                        justification="center", 
                        size=(30, 1), 
                        pad=(0, 10),
                        text_color=WHITE_TEXT,  # White text
                        background_color=RED_BANNER,  # Red banner background
                        relief=sg.RELIEF_RAISED,  # Raised border effect for a banner look
                        border_width=2)],  # Adding border width for emphasis

                    [sg.Multiline(
                        default_text="Hover over an area to get more information!", 
                        disabled=True, 
                        justification="center",
                        size=(CANVAS_WIDTH_MAX // 20, 2),
                        write_only=True, 
                        key="-MULTILINE-",
                        no_scrollbar=True,
                        background_color=DARK_BG,
                        text_color=LIGHT_TEXT,
                        font=("Segoe UI", 12)
                    )]
                ], 
                justification="center",
                element_justification="center",
                expand_x=True,
                pad=(10, 10)
            )],

            [sg.HorizontalSeparator(pad=(5, 10))],

            [sg.Frame(
                "",
                [
                    [sg.Text("Search:", font=("Georgia", 12)), 
                    sg.Input(size=(20, 1), key="-SEARCH-", font=("Georgia", 12), enable_events=True)],

                    [sg.Checkbox("Exact Matches?", key="-EXACT_MATCH-", enable_events=True, font=("Georgia", 11))],

                    [sg.Listbox(values=[], size=(30, 5), key="-RESULTS-", enable_events=True, font=("Segoe UI", 12), visible=False)]
                ],
                pad=(10, 10),
                relief=sg.RELIEF_FLAT,
                background_color=DARK_BG
            )],

            [sg.Canvas(background_color="black", size=self.canvas_size, key="-CANVAS-", pad=(10, 10))],

            [sg.Frame(
                "Map Modes", 
                [[sg.Button(
                    mode.name, 
                    key=mode.value, 
                    pad=(5, 5), 
                    button_color=(BUTTON_FG, BUTTON_BG),
                    font=("Garamond", 12)) for mode in self.painter.map_modes]],
                element_justification="center",
                relief=sg.RELIEF_SUNKEN,
                pad=(10, 10),
                background_color=FRAME_BG,
                border_width=1,
                title_color=FRAME_TITLE_COLOR)],

            [sg.HorizontalSeparator(pad=(5, 10))],

            [sg.Button(
                "Reset View", 
                key="-RESET-", 
                pad=(10, 5), 
                font=("Georgia", 12, "bold"), 
                button_color=(BUTTON_BG, BUTTON_FG))],

            [sg.Text('', size=(1, 1), pad=(5, 5))]
        ]

        sg.set_options(font=("Segoe UI", 12))
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

            if event == "-RESET-":
                self.reset_display(tk_canvas)

            if event in {"-EXACT_MATCHES-", "-SEARCH-"}:
                exact_matches_only = values["-EXACT_MATCH-"]
                search_param = values["-SEARCH-"].strip().lower()
                if not search_param:
                    window["-RESULTS-"].update(values=[], visible=False)
                    continue

                province_matches = self.painter.world_data.search(
                    exact_matches_only=exact_matches_only, search_param=search_param)

                name_matches = [p.name for p in province_matches]
                if name_matches:
                    window["-RESULTS-"].update(values=name_matches, visible=True)
                else:
                    window["-RESULTS-"].update(values=[], visible=False)

        window.close()
