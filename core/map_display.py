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
from . import MapHandler, MapPainter
from . import Layout
from .models import EUProvince, ProvinceType, EUArea, EURegion
from .models import MapMode


CANVAS_WIDTH_MAX = 1200

## Some color constants
LIGHT_TEXT = "#d2d2d2"
GOLD_FRAME_UPPER = "#b68950"
GOLD_FRAME_LOWER = "#9f7240"
RED_BANNER_BG = "#561b19"
TOP_BANNER_BG = "#353c25"
SECTION_BANNER_BG = "#172f48"
LIGHT_FRAME_BG = "#344048"
DARK_FRAME_BG = "#2a343b"
SUNKEN_FRAME_BG = "#283239"
WINDOW_BACKGROUND = ""
BUTTON_BG = "#314b68"
BUTTON_FG = "#394d66"
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
        """Creates the UI layout for the map viewer.
        
        Returns:
            layout (list[list]): The layout for the Window.
        """
        screen_width, screen_height = sg.Window.get_screen_size()
        CANVAS_WIDTH_MAX = min(1200, int(screen_width * 0.9))

        map_width, map_height = self.original_map.size
        canvas_height = int(CANVAS_WIDTH_MAX * (map_height / map_width))
        self.canvas_size = (CANVAS_WIDTH_MAX, canvas_height)
        return Layout.build_layout(self.canvas_size, self.painter.map_modes)

    def update_province_details(self, province: EUProvince):
        window = self.window

        if province.province_type == ProvinceType.OWNED:
            data = {
                "-INFO_PROVINCE_NAME-": province.name,
                "-INFO_OWNER-": province.owner.name or province.owner.tag,
                "-INFO_CAPITAL-": province.capital,
                "-INFO_PROVINCE_AREA-": self.world_data.province_to_area.get(province.province_id, None).name, 
                "-INFO_PROVINCE_REGION-": self.world_data.province_to_region.get(province.province_id, None).name,
                "-INFO_PROVINCE_BASE_TAX-": province.base_tax,
                "-INFO_PROVINCE_BASE_PRODUCTION-": province.base_production,
                "-INFO_PROVINCE_BASE_MANPOWER-": province.base_manpower,
                "-INFO_PROVINCE_TRADE_POWER-": province.trade_power,
                "-INFO_PROVINCE_GOODS_PRODUCED-": province.base_production / 10,
                "-INFO_PROVINCE_TRADE_GOOD-": province.trade_goods,
                "-INFO_PROVINCE_HOME_NODE-": province.trade_node,
                "-INFO_PROVINCE_GARRISON_SIZE-": province.garrison,
                "-INFO_PROVINCE_FORT_LEVEL-": province.fort_level,
                # "-INFO_PROVINCE_LOCAL_AUTONOMY-": province.local_autonomy,
                # "-INFO_PROVINCE_DEVASTATION-": province.devastation,
                "-INFO_CULTURE-": province.culture,
                "-INFO_RELIGION-": province.religion,
            }

            window["-AREA_INFO-"].update(visible=False)
            window["-PROVINCE_INFO-"].update(visible=True)
            for element, attr_value in data.items():
                if attr_value is not None:
                    window[element].update(value=attr_value, visible=True)
                else:
                    window[element].update(visible=False)

    def update_area_details(self, area: EUArea):
        window = self.window
        area_province = list(area.provinces.values())[0]

        if area.is_land_area:
            data = {
                "-INFO_AREA_NAME-" : area.name,
                "-INFO_AREA_REGION-" : self.world_data.province_to_region.get(area_province.province_id, None).name,
                "-INFO_AREA_BASE_TAX-" : sum(province.base_tax for province in area.provinces.values()),
                "-INFO_AREA_BASE_PRODUCTION-" : sum(province.base_production for province in area.provinces.values()),
                "-INFO_AREA_BASE_MANPOWER-" : sum(province.base_manpower for province in area.provinces.values()),
                "-INFO_AREA_PROVINCES-" : [province.name for province in area.provinces.values()]
            }

            window["-PROVINCE_INFO-"].update(visible=False)
            window["-AREA_INFO-"].update(visible=True)
            for element, attr_value in data.items():
                if attr_value is not None:
                    try:
                        window[element].update(value=attr_value, visible=True)
                    except (AttributeError, TypeError):
                        window[element].update(values=attr_value, visible=True)
                else:
                    window[element].update(visible=False)

    def update_details(self, selected_item: EUProvince|EUArea|EURegion):
        if hasattr(selected_item, "province_type"):
            self.update_province_details(selected_item)

        elif isinstance(selected_item, EUArea):
            self.update_area_details(selected_item)

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
                window["-CLEAR-"].update(visible=True)
                exact_matches_only = values["-EXACT_MATCH-"]
                search_param = values["-SEARCH-"].strip().lower()
                if not search_param:
                    window["-RESULTS-"].update(values=[], visible=False)
                    window["-CLEAR-"].update(visible=False)
                    continue

                matches = self.world_data.search(
                    exact_matches_only=exact_matches_only, search_param=search_param)
                self.search_results = matches

                name_matches = [item.name for item in self.search_results]
                if name_matches:
                    window["-RESULTS-"].update(values=name_matches, visible=True)
                    window["-GOTO-"].update(visible=True)
                else:
                    window["-RESULTS-"].update(values=[])
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
