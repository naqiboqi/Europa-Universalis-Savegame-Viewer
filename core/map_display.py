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
from .models import EUProvince, EUArea, EURegion
from .models import MapMode


CANVAS_WIDTH_MAX = 1400


## Some color constants
LIGHT_TEXT = "#d2d2d2"
WHITE_TEXT = "#ffffff"
GOLD_ACCENT = "#ffcc00"
GOLD_FRAME = "#D4AF37"
TEAL_ACCENT = "#0e6f74"
FRAME_BG = "#2c2f36"
FRAME_TITLE_COLOR = GOLD_ACCENT
DARK_BG = "#1d1f21"
FRAME_BG = "#2b2b2b"
BUTTON_BG = "#5d8fae"
BUTTON_FG = "#ffffff" 
LISTBOX_BG = "#2b2b2b"
LISTBOX_FG = LIGHT_TEXT

GOLD_FRAME_UPPER = "#b68950"
GOLD_FRAME_LOWER = "#9f7240"
RED_BANNER = "#9e2a2f"
TOP_BANNER_BG = "#353c25"
SECTION_BANNER_BG = "#172f48"
LIGHT_FRAME_BG = "#344048"
DARK_FRAME_BG = "#2a343b"
BUTTON_COLOR = "#314b68"
GREEN_TEXT = "#2b8334"



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
        tk_canvas (tk.Canvas): The window canvas for the current image.
        window (sg.Window): The PySimpleGUI window for the UI.

        max_scale (float): The maximum zoom level allowed.
        map_scale (float): The current zoom level of the map.
        min_scale (float): The minimum zoom level allowed.

        offset_x (int): The horizontal offset for panning.
        offset_y (int): The vertical offset for panning.
    """
    def __init__(self, painter: MapPainter):
        self.painter = painter
        self.world_data = painter.world_data

        self.canvas_size = ()
        self.handler: MapHandler = None
        self.image_id = None
        self.original_map = None
        self.map_image = None
        self.tk_image = None
        self.tk_canvas = None
        self.window = None

        self.max_scale = 5.0
        self.map_scale = 1.0
        self.min_scale = 1.0

        self.offset_x = 0
        self.offset_y = 0

        self.selected_item = None
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

    def reset_display(self):
        """Resets the canvas and image to their inital settings."""
        self.offset_x = 0
        self.offset_y = 0
        self.map_image = self.scale_image_to_fit(self.original_map)
        self.update_display()

    def update_display(self):
        """Updates the canvas and image.
        
        Applies any pan or zoom adjustments to the canvas for user interaction.
        """
        self.tk_image = self.image_to_tkimage(self.map_image)
        self.tk_canvas.itemconfig(self.image_id, image=self.tk_image)
        self.tk_canvas.coords(self.image_id, self.offset_x, self.offset_y)

    def update_map_mode(self, map_mode: MapMode):
        """Updates the map mode and redraws the map.
        
        Args:
            map_mode (MapMode): The new map mode.
        """
        if map_mode == self.painter.map_mode:
            return

        self.painter.map_mode = map_mode
        self.original_map = self.painter.draw_map()

        self.map_image = self.original_map.resize(self.map_image.size, Image.Resampling.LANCZOS)
        self.tk_image = self.image_to_tkimage(self.map_image)
        self.tk_canvas.itemconfig(self.image_id, image=self.tk_image)
        self.tk_canvas.coords(self.image_id, self.offset_x, self.offset_y)

    def create_layout(self):
        """Creates the UI layout for the map viewer and returns it."""
        map_width, map_height = self.original_map.size
        canvas_height = int(CANVAS_WIDTH_MAX * (map_height / map_width))
        self.canvas_size = (CANVAS_WIDTH_MAX, canvas_height)

        return [
            [sg.Frame("", [  # Outer Frame
                [sg.Frame("", [  # Inner Frame
                    [sg.Column([
                        [sg.Text(
                            "Map Information", 
                            font=("Georgia", 18, "bold"), 
                            justification="center", 
                            size=(30, 1), 
                            pad=(0, 10),
                            text_color=LIGHT_TEXT,
                            background_color=TOP_BANNER_BG,
                            relief=sg.RELIEF_RAISED,  # Raised for a slight glow effect
                            border_width=2)],

                        [sg.Multiline(
                            default_text="Hover over an area to get more information!", 
                            disabled=True, 
                            justification="center",
                            size=(CANVAS_WIDTH_MAX // 20, 2),
                            write_only=True, 
                            key="-MULTILINE-",
                            no_scrollbar=True,
                            background_color=LIGHT_FRAME_BG,
                            text_color=LIGHT_TEXT,
                            font=("Segoe UI", 12),
                            border_width=2,
                            pad=(5, 5))],

                        [sg.Text("", size=(30, 1), pad=(0, 10), background_color=LIGHT_FRAME_BG)]
                    ], justification="center", element_justification="center", expand_x=True, pad=(5, 5), background_color=LIGHT_FRAME_BG)]
                ], expand_x=True, relief=sg.RELIEF_SUNKEN, border_width=2, background_color=GOLD_FRAME_LOWER, pad=(5, 5))]  # Darker Inner Frame
            ], expand_x=True, relief=sg.RELIEF_RAISED, border_width=2, background_color=GOLD_FRAME_UPPER, pad=(15, 15))],  # Lighter Outer Frame

            [sg.Frame("", [
                [sg.Text("Search:", font=("Georgia", 12, "bold"), text_color=LIGHT_TEXT, background_color=LIGHT_FRAME_BG)], 
                [sg.Input(size=(20, 1), key="-SEARCH-", font=("Georgia", 12), enable_events=True, text_color=LIGHT_TEXT, background_color=LIGHT_FRAME_BG)],

                [sg.Checkbox("Exact Matches?", key="-EXACT_MATCH-", enable_events=True, font=("Georgia", 11), text_color=LIGHT_TEXT, background_color=LIGHT_FRAME_BG)],

                [sg.Listbox(values=[], size=(30, 5), key="-RESULTS-", enable_events=True, font=("Segoe UI", 12), visible=False, text_color=LIGHT_TEXT, background_color=LIGHT_FRAME_BG)],
                [sg.Button(
                    "Go to",
                    key="-GOTO-",
                    pad=(5, 5),
                    font=("Georgia", 12, "bold"),
                    button_color=(LIGHT_TEXT, BUTTON_COLOR),
                    visible=False)]
                ], pad=(10, 10), relief=sg.RELIEF_GROOVE, background_color=LIGHT_FRAME_BG, border_width=5),
                
                sg.Push(background_color=LIGHT_FRAME_BG),
                sg.Frame("", [
                    [sg.Frame("", [
                        [sg.Column([
                            [sg.Text("Province:", font=("Georgia", 14, "bold"), text_color=LIGHT_TEXT, background_color=TOP_BANNER_BG),
                            sg.Text("", key="-INFO_NAME-", font=("Georgia", 14, "bold"), text_color=LIGHT_TEXT, background_color=TOP_BANNER_BG)],

                            [sg.Text("Capital:", font=("Georgia", 12), text_color=LIGHT_TEXT, background_color=TOP_BANNER_BG),
                            sg.Text("", key="-INFO_CAPITAL-", font=("Georgia", 12), text_color=LIGHT_TEXT, background_color=TOP_BANNER_BG)],
                        ], background_color=TOP_BANNER_BG, element_justification="left", expand_x=True),

                        sg.Column([
                            [sg.Text("Area:", font=("Georgia", 14, "bold"), text_color=LIGHT_TEXT, background_color=TOP_BANNER_BG),
                            sg.Text("", key="-INFO_PROVINCE_AREA-", font=("Georgia", 14, "bold"), text_color=LIGHT_TEXT, background_color=TOP_BANNER_BG)],

                            [sg.Text("Region:", font=("Georgia", 12), text_color=LIGHT_TEXT, background_color=TOP_BANNER_BG),
                            sg.Text("", key="-INFO_PROVINCE_REGION-", font=("Georgia", 12), text_color=LIGHT_TEXT, background_color=TOP_BANNER_BG)],
                        ], background_color=TOP_BANNER_BG, element_justification="right", expand_x=True)]
                    ], background_color=TOP_BANNER_BG, relief=sg.RELIEF_RAISED, border_width=4, title_color=LIGHT_TEXT, pad=(5, 5), expand_x=True)],

                    [sg.Push(background_color=LIGHT_FRAME_BG),
                        sg.Frame("", [
                        [sg.Text("Development", font=("Georgia", 12, "bold"), text_color=LIGHT_TEXT, background_color=SECTION_BANNER_BG, relief=sg.RELIEF_RAISED)],

                        [sg.Text("Tax:", font=("Georgia", 12), text_color=LIGHT_TEXT, background_color=DARK_FRAME_BG),  
                        sg.Text("", key="-INFO_BASE_TAX-", font=("Georgia", 12), text_color=GREEN_TEXT, background_color=DARK_FRAME_BG, size=(10, 1)),  
                        
                        sg.Text("Production:", font=("Georgia", 12), text_color=LIGHT_TEXT, background_color=DARK_FRAME_BG),  
                        sg.Text("", key="-INFO_BASE_PRODUCTION-", font=("Georgia", 12), text_color=GREEN_TEXT, background_color=DARK_FRAME_BG, size=(10, 1)),  
                        
                        sg.Text("Manpower:", font=("Georgia", 12), text_color=LIGHT_TEXT, background_color=DARK_FRAME_BG),  
                        sg.Text("", key="-INFO_BASE_MANPOWER-", font=("Georgia", 12), text_color=GREEN_TEXT, background_color=DARK_FRAME_BG, size=(10, 1))]
                    ], background_color=DARK_FRAME_BG, pad=(5, 10), relief=sg.RELIEF_SUNKEN, border_width=3, title_color=LIGHT_TEXT),
                    sg.Push(background_color=LIGHT_FRAME_BG)],  

                    [sg.Push(background_color=LIGHT_FRAME_BG),
                        sg.Frame("", [
                            [sg.Text("Demographics", font=("Georgia", 12, "bold"), text_color=LIGHT_TEXT, background_color=SECTION_BANNER_BG, relief=sg.RELIEF_RAISED)],

                            [sg.Text("Cored By:", font=("Georgia", 12), text_color=LIGHT_TEXT, background_color=DARK_FRAME_BG),  
                            sg.Text("", key="-INFO_OWNER-", font=("Georgia", 12), text_color=GREEN_TEXT, background_color=DARK_FRAME_BG, size=(20, 1))],

                            [sg.Text("Culture:", font=("Georgia", 12), text_color=LIGHT_TEXT, background_color=DARK_FRAME_BG),  
                            sg.Text("", key="-INFO_CULTURE-", font=("Georgia", 12), text_color=GREEN_TEXT, background_color=DARK_FRAME_BG, size=(20, 1))],

                            [sg.Text("Religion:", font=("Georgia", 12), text_color=LIGHT_TEXT, background_color=DARK_FRAME_BG),  
                            sg.Text("", key="-INFO_RELIGION-", font=("Georgia", 12), text_color=GREEN_TEXT, background_color=DARK_FRAME_BG, size=(20, 1))]
                        ], background_color=DARK_FRAME_BG, pad=(5, 10), relief=sg.RELIEF_SUNKEN, border_width=4, expand_x=True),
                    sg.Push(background_color=LIGHT_FRAME_BG)]
                ], key="-PROVINCE_INFO-", pad=(10, 10), relief=sg.RELIEF_GROOVE, background_color=LIGHT_FRAME_BG, border_width=5, title_color=LIGHT_TEXT)
            ],
            
            [sg.Frame("", [
                [sg.Canvas(background_color="black", size=self.canvas_size, key="-CANVAS-", pad=(10, 10))]
            ], background_color=LIGHT_FRAME_BG, relief=sg.RELIEF_GROOVE, pad=(10, 10), border_width=5)],

            [sg.Frame("Map Modes", [
                [sg.Button(
                    mode.name, 
                    key=mode.value, 
                    pad=(5, 5), 
                    button_color=(LIGHT_TEXT, BUTTON_COLOR),
                    font=("Garamond", 12, "bold")) for mode in self.painter.map_modes]],
                element_justification="center",
                relief=sg.RELIEF_GROOVE,
                pad=(10, 10),
                background_color=LIGHT_FRAME_BG,
                border_width=3,
                title_color=LIGHT_TEXT),

                sg.Button(
                    "Reset View", 
                    key="-RESET-", 
                    pad=(10, 5), 
                    font=("Georgia", 12, "bold"), 
                    button_color=(LIGHT_TEXT, BUTTON_COLOR))],

            [sg.Text("", size=(1, 1), pad=(5, 5), background_color=LIGHT_FRAME_BG)]
        ]

    def update_details(self, selected_item: EUProvince|EUArea|EURegion):
        window = self.window

        if isinstance(selected_item, EUProvince):
            province = selected_item
            data = {
                "-INFO_NAME-" : province.name,
                "-INFO_OWNER-" : province.owner.name or province.owner.tag,
                "-INFO_CAPITAL-" : province.capital,
                "-INFO_PROVINCE_AREA-" : self.world_data.province_to_area.get(province.province_id, None).name, 
                "-INFO_PROVINCE_REGION-" : self.world_data.province_to_region.get(province.province_id, None).name,
                "-INFO_BASE_TAX-" : province.base_tax,
                "-INFO_BASE_PRODUCTION-" : province.base_production,
                "-INFO_BASE_MANPOWER-" : province.base_manpower,
                "-INFO_CULTURE-" : province.culture,
                "-INFO_RELIGION-" : province.religion,
                }

            for element, attr_value in data.items():
                if attr_value is not None:
                    print(f"{element}: {attr_value}")
                    window[element].update(value=attr_value, visible=True)
                else:
                    window[element].update(visible=False)

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

        window = sg.Window("EU4 Map Viewer", layout, finalize=True, return_keyboard_events=True, background_color=LIGHT_FRAME_BG)
        window.move_to_center()
        self.window = window

        canvas = window["-CANVAS-"]
        self.tk_canvas: tk.Canvas = canvas.TKCanvas

        self.tk_image = self.image_to_tkimage(self.map_image)
        self.image_id = self.tk_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.handler = MapHandler(self, self.tk_canvas)
        self.handler.bind_events()

        mode_names = {mode.value: mode for mode in self.painter.map_modes}

        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, "Exit"):
                break

            if event in mode_names:
                self.update_map_mode(mode_names[event])

            if event in {"-EXACT_MATCHES-", "-SEARCH-"}:
                exact_matches_only = values["-EXACT_MATCH-"]
                search_param = values["-SEARCH-"].strip().lower()
                if not search_param:
                    window["-RESULTS-"].update(values=[], visible=False)
                    continue

                matches = self.world_data.search(
                    exact_matches_only=exact_matches_only, search_param=search_param)
                self.search_results = matches

                name_matches = [item.name for item in self.search_results]
                if name_matches:
                    window["-RESULTS-"].update(values=name_matches, visible=True)
                    window["-GOTO-"].update(visible=True)
                else:
                    window["-RESULTS-"].update(values=[], visible=False)
                    window["-GOTO-"].update(visible=False)

            if event == "-RESULTS-":
                selected = values["-RESULTS-"]
                if selected:
                    item_name = selected[0]
                    selected_item = next(
                        (item for item in self.search_results
                        if item.name.lower() == item_name.lower()),
                        None)

                    self.selected_item = selected_item

            if event == "-GOTO-":
                if self.selected_item:
                    self.handler.go_to_entity_location(self.selected_item)
                    self.update_details(self.selected_item)

            if event == "-RESET-":
                self.reset_display()

        window.close()
