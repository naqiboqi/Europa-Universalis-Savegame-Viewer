"""
Map Displaying and interacting with the Europa Universalis IV savegame viewing.

This module contains the implementation  for rendering 
the map, handling user interactions such as zooming, panning, and searching, 
and managing UI elements using PySimpleGUI and Tkinter.
"""


from __future__ import annotations

import FreeSimpleGUI as sg
import tkinter as tk

from PIL import Image, ImageTk
from . import MapHandler
from . import MapPainter
from .models import MapMode


CANVAS_WIDTH_MAX = 1400


## Some color constants
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
    """Handles displaying the map and managing user interactions.

    This class is responsible for rendering the map, handling zooming and panning, 
    managing UI elements, and responding to user events such as searching and 
    selecting different map modes.

    Attributes:
        painter (MapPainter): The map painter instance responsible for drawing the map.
        canvas_size (tuple): The dimensions of the display canvas.
        handler (MapHandler): The event handler for managing interactions.
        image_id (int): The ID of the displayed image in the canvas.
        original_map (PIL.Image): The original unscaled map image.
        map_image (PIL.Image): The currently displayed map image.
        tk_image (tk.PhotoImage): The Tkinter-compatible image for rendering.
        window (sg.Window): The PySimpleGUI window for the UI.

        max_scale (float): The maximum zoom level allowed.
        map_scale (float): The current zoom level of the map.
        min_scale (float): The minimum zoom level allowed.

        offset_x (int): The horizontal offset for panning.
        offset_y (int): The vertical offset for panning.
    """
    def __init__(self, painter: MapPainter):
        self.painter = painter

        self.canvas_size = ()
        self.handler: MapHandler = None
        self.image_id = None
        self.original_map = None
        self.map_image = None
        self.tk_image = None
        self.window = None

        self.max_scale = 5.0
        self.map_scale = 1.0
        self.min_scale = 1.0

        self.offset_x = 0
        self.offset_y = 0
        
        self.search_results = []

    def image_to_tkimage(self, image: Image.Image):
        """Converts a PIL image to a TkInter image."""
        return ImageTk.PhotoImage(image)

    def scale_image_to_fit(self, image: Image.Image):
        """Scales the image down to fit within the canvas.
        
        Sets the new size of the image and also sets the minimum and maximum scales for the canvas.
        
        Args:
            image (Image): The image to scale.
        
        Returns:
            Image: The scaled image.
        """
        width, height = image.size
        canvas_width, canvas_height = self.canvas_size

        self.map_scale = min(canvas_width / width, canvas_height / height)
        self.max_scale = 10 * self.map_scale
        self.min_scale = self.map_scale

        return image.resize((self.canvas_size), Image.Resampling.LANCZOS)

    def reset_display(self, tk_canvas: tk.Canvas):
        """Resets the canvas and image to their inital settings.
        
        Args:
            tk_canvas (tk.Canvas): The window canvas for the current image.
        """
        self.offset_x = 0
        self.offset_y = 0
        self.map_image = self.scale_image_to_fit(self.original_map)
        self.update_display(tk_canvas)

    def update_display(self, tk_canvas: tk.Canvas):
        """Updates the canvas and image.
        
        Applies any pan or zoom adjustments to the canvas for user interaction.
        
        Args:
            tk_canvas (tk.Canvas): The window canvas for the current image.
        """
        self.tk_image = self.image_to_tkimage(self.map_image)
        tk_canvas.itemconfig(self.image_id, image=self.tk_image)
        tk_canvas.coords(self.image_id, self.offset_x, self.offset_y)

    def update_map_mode(self, map_mode: MapMode, tk_canvas: tk.Canvas):
        """Updates the map mode and redraws the map.
        
        Args:
            map_mode (MapMode): The new map mode.
            tk_canvas (tk.Canvas): The window canvas for the current image. """
        if map_mode == self.painter.map_mode:
            return

        self.painter.map_mode = map_mode
        self.original_map = self.painter.draw_map()

        self.map_image = self.original_map.resize(self.map_image.size, Image.Resampling.LANCZOS)
        self.tk_image = self.image_to_tkimage(self.map_image)
        tk_canvas.itemconfig(self.image_id, image=self.tk_image)
        tk_canvas.coords(self.image_id, self.offset_x, self.offset_y)

    def create_layout(self):
        """Creates the UI layout for the map viewer and returns it."""
        map_width, map_height = self.original_map.size
        canvas_height = int(CANVAS_WIDTH_MAX * (map_height / map_width))
        self.canvas_size = (CANVAS_WIDTH_MAX, canvas_height)

        return [
            [sg.Column(
                [
                    [sg.Text(
                        "Map Information", 
                        font=("Times New Roman", 14, "bold"), 
                        justification="center", 
                        size=(30, 1), 
                        pad=(0, 10),
                        text_color=WHITE_TEXT,
                        background_color=RED_BANNER,
                        relief=sg.RELIEF_RAISED,
                        border_width=2)],

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

                    [sg.Listbox(values=[], size=(30, 5), key="-RESULTS-", enable_events=True, font=("Segoe UI", 12), visible=False)],
                    [sg.Button(
                        "Go to",
                        key="-GOTO-",
                        pad=(5, 5),
                        font=("Georgia", 12, "bold"),
                        button_color=(BUTTON_BG, BUTTON_FG),
                        visible=False)]
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

    def display_map(self):
        """Displays the main UI window for the Europa Universalis IV map viewer.

        This method initializes the graphical user interface (GUI) using the `PySimpleGUI` library.
        It includes:
        
        - **Map Display:** A canvas that renders the scaled game map.
        - **Information Panel:** Displays details about hovered provinces.
        - **Search Bar:** Allows users to search for provinces by name.
        - **Map Modes:** Buttons to switch between different map visualizations.
        - **Reset Button:** Resets the map view to its original state.

        The event loop continuously listens for user actions to update the UI.
        """
        sg.theme("DarkBlue")

        self.original_map = self.painter.draw_map()
        layout = self.create_layout()
        self.map_image = self.scale_image_to_fit(self.original_map)

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

            if event in {"-EXACT_MATCHES-", "-SEARCH-"}:
                exact_matches_only = values["-EXACT_MATCH-"]
                search_param = values["-SEARCH-"].strip().lower()
                if not search_param:
                    window["-RESULTS-"].update(values=[], visible=False)
                    continue

                province_matches = self.painter.world_data.search(
                    exact_matches_only=exact_matches_only, search_param=search_param)
                self.search_results = province_matches

                name_matches = [p.name for p in province_matches]
                if name_matches:
                    window["-RESULTS-"].update(values=name_matches, visible=True)
                    window["-GOTO-"].update(visible=True)
                else:
                    window["-RESULTS-"].update(values=[], visible=False)
                    window["-GOTO-"].update(visible=False)

            if event == "-RESULTS-":
                selected = values["-RESULTS-"]
                if selected:
                    province_name = selected[0]
                    selected_province = next((p for p in self.search_results if p.name.lower() == province_name.lower()), None)
                    if selected_province:
                        print(f"Selected province {selected_province}")

            if event == "-GOTO-":
                if selected_province:
                    self.handler.go_to(selected_province)

            if event == "-RESET-":
                self.reset_display(tk_canvas)

        window.close()
