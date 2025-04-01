"""
Map Displaying and interacting with the Europa Universalis IV savegame viewing.

This module contains the implementation  for rendering 
the map, handling user interactions such as zooming, panning, and searching, 
and managing UI elements using PySimpleGUI and Tkinter.
"""


from __future__ import annotations

import FreeSimpleGUI as sg
import threading
import tkinter as tk

from PIL import Image, ImageDraw, ImageFont, ImageTk
from . import MapHandler, MapPainter
from . import Layout
from .models import EUProvince, ProvinceType, EUArea, EURegion
from .models import MapMode
from .utils import IconLoader, MapUtils


icon_loader = IconLoader()



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

        selected_item: (EUProvince|EUArea|EURegion|None): The current selected item, to get information for
            and display in the window's information section, if any.
        search_results: (list[EUProvince|EUArea|EURegion]): The results from the user's search, if any.
    """
    def __init__(self, painter: MapPainter=None, saves_folder: str=None):
        self.painter = painter
        self.save_folder = saves_folder
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
        """Converts a PIL Image to a TkInter Image."""
        return ImageTk.PhotoImage(image)

    def scale_image_to_fit(self, image: Image.Image):
        """Scales the image to fit within the canvas.
        
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

    def display_loading_screen(
        self,
        canvas_size: tuple[int, int]=None, 
        color: tuple[int, int, int]=(25, 25, 25),
        message: str=""):
        """Displays a loading screen with an optional message.

        Args:
            canvas_size (tuple[int, int], optional): The `(x, y)` dimensions of the loading image.
                Defaults to the size of the canvas if not provided.
            color (tuple[int, int, int], optional): The background color of the loading image in RGB format.
                Defaults to a dark gray (25, 25, 25).
            message (str, optional): The optional message to display on the loading screen.

        Returns:
            PIL.Image.Image: The generated loading image.
        """
        if not canvas_size:
            canvas_size = self.canvas_size

        map_image = Image.new(mode="RGB", size=canvas_size, color=color)
        draw = ImageDraw.Draw(map_image)

        try:
            font = ImageFont.truetype("georgia.ttf", 36)
        except IOError:
            font = ImageFont.load_default()

        text_size = draw.textbbox((0, 0), text=message, font=font)
        text_width, text_height = text_size[2] - text_size[0], text_size[3] - text_size[1]

        text_center_x = (canvas_size[0] - text_width) // 2
        text_center_y = (canvas_size[1] - text_height) // 2

        draw.text((text_center_x, text_center_y), text=message, fill="white", font=font)

        self.map_image = map_image
        self.update_canvas()
        self.window.refresh()

        return map_image

    def update_canvas(self):
        """Updates the canvas by applying all pan and/or zoom adjustments to the image.
        
        This is done after every zoom and pan event, and after changing the map mode or selected savefile.
        """
        self.tk_image = self.image_to_tkimage(self.map_image)
        self.tk_canvas.itemconfig(self.image_id, image=self.tk_image)
        self.tk_canvas.coords(self.image_id, self.offset_x, self.offset_y)

    def reset_canvas_to_initial(self):
        """Resets the canvas to its initial zoom and pan settings.
        
        Centers the map and zooms out to the minimum level.
        """
        self.offset_x = 0
        self.offset_y = 0
        self.map_image = self.scale_image_to_fit(self.original_map)
        self.update_canvas()

    def refresh_canvas_image(self):
        """Refreshes the canvas after loading a new savefile.
        
        Draws the map for the new savefile and resets the canvas to the minimum zoom level and default pan location.
        """
        ## TODO Also maybe add asynchronous functionality so that the UI doesnt freeze while busy
        self.original_map = self.painter.draw_map()
        self.map_image = self.scale_image_to_fit(self.original_map)
        self.reset_canvas_to_initial()

    def update_map_mode(self, map_mode: MapMode):
        """Updates the map mode and redraws the map for that mode.
        
        Args:
            map_mode (MapMode): The new map mod selected by the user.
        """
        if map_mode == self.painter.map_mode:
            return

        self.display_loading_screen(message="Loading map....")

        self.painter.map_mode = map_mode
        self.original_map = self.painter.draw_map()

        self.map_image = self.original_map.resize(self.map_image.size, Image.Resampling.LANCZOS)
        self.update_canvas()

    def create_layout(self):
        """Creates the layout that will be used for the UI and sets the canvas size.
        
        Returns:
            layout (list[list]): The layout for the Window.
        """
        screen_width, screen_height = sg.Window.get_screen_size()
        canvas_width_max = min(Layout.CANVAS_WIDTH_MAX, int(screen_width * 0.9))

        map_width, map_height = self.original_map.size
        canvas_height = int(canvas_width_max * (map_height / map_width))
        self.canvas_size = (canvas_width_max, canvas_height)

        return Layout.build_layout(self.canvas_size, self.painter.map_modes)

    def update_province_details(self, province: EUProvince):
        """Updates the information displayed for a specific province in the UI.

        This method retrieves the relevant data for a province, such as its name, owner, capital,
        development, tax, production, manpower, trade power, and fort level, and trade goods.

        Args:
            province (EUProvince): The province to be displayed.
        """
        window = self.window

        if province.province_type == ProvinceType.OWNED:
            data = {
                "-INFO_PROVINCE_NAME-": province.name,
                "-INFO_PROVINCE_OWNER-": province.owner.name or province.owner.tag,
                "-INFO_PROVINCE_CAPITAL-": province.capital,
                "-INFO_PROVINCE_AREA_NAME-": self.world_data.province_to_area.get(province.province_id, None).name, 
                "-INFO_PROVINCE_TOTAL_DEV-": province.development,
                "-INFO_PROVINCE_REGION_NAME-": self.world_data.province_to_region.get(province.province_id, None).name,
                "-INFO_PROVINCE_BASE_TAX-": province.base_tax,
                "-INFO_PROVINCE_BASE_PRODUCTION-": province.base_production,
                "-INFO_PROVINCE_BASE_MANPOWER-": province.base_manpower,
                "-INFO_PROVINCE_TRADE_POWER-": province.trade_power,
                "-INFO_PROVINCE_GOODS_PRODUCED-": province.goods_produced,
                "-INFO_PROVINCE_LOCAL_MANPOWER-": province.manpower,
                "-INFO_PROVINCE_LOCAL_SAILORS-": province.sailors,
                "-INFO_PROVINCE_HOME_NODE-": province.trade_node,
                "-INFO_PROVINCE_SIZE_KM-": province.area_km2,
                "-INFO_PROVINCE_GARRISON_SIZE-": province.garrison,
                "-INFO_PROVINCE_CULTURE-": MapUtils.format_name(province.culture),
                "-INFO_PROVINCE_RELIGION-": MapUtils.format_name(province.religion),
            }

            window["-REGION_INFO_COLUMN-"].update(visible=False)
            window["-AREA_INFO_COLUMN-"].update(visible=False)
            window["-PROVINCE_INFO_COLUMN-"].update(visible=True)

            for element, attr_value in data.items():
                if attr_value is not None:
                    window_element = window[element]
                    window_element.update(value=attr_value, visible=True)
                else:
                    window[element].update(value=0)

            trade_good_element = window["-INFO_PROVINCE_TRADE_GOOD-"]
            trade_good_element.update(filename=icon_loader.get_icon(province.trade_goods), visible=True)

            trade_good_price_element = window["-INFO_PROVINCE_TRADE_GOOD_PRICE-"]
            trade_value = self.world_data.trade_goods.get(province.trade_goods) or 0.00
            trade_good_price_element.update(value=f"{trade_value:.2f}")

            trade_income_element = window["-INFO_PROVINCE_TRADE_VALUE-"]
            trade_income_element.update(value=trade_value * province.base_production / 10)

            fort_level_element = window["-INFO_PROVINCE_FORT_LEVEL-"]
            forts = {
                0: "no_fort",
                1: "fort_15th",
                2: "fort_16th",
                3: "fort_17th",
                4: "fort_18th"
            }

            if province.fort_level in forts:
                fort_level_element.update(filename=icon_loader.get_icon(forts[province.fort_level]))

            inland_trade_element = window["-INFO_PROVINCE_INLAND_TRADE_CENTER-"]
            inland_centers_of_trade = {
                1: "cot_1",
                2: "cot_2",
                3: "cot_3"
            }

            center_of_trade_element = window["-INFO_PROVINCE_CENTER_OF_TRADE-"]
            centers_of_trade = {
                1: "cot_emporium",
                2: "cot_market_town",
                3: "cot_world_trade_center"
            }

            if province.center_of_trade in centers_of_trade:
                inland_cot = icon_loader.get_icon(inland_centers_of_trade[province.center_of_trade])
                inland_trade_element.update(filename=inland_cot)

                cot = icon_loader.get_icon(centers_of_trade[province.center_of_trade])
                center_of_trade_element.update(filename=cot)

    def update_area_details(self, area: EUArea):
        """Updates the information displayed for a specific area in the UI.

        This method retrieves the relevant data for an area, such as its name, region,
        total development, base tax, base production, and base manpower. It also updates
        the area provinces table with information for each province within the area.

        Args:
            area (EUArea): The area to be displayed.
        """
        window = self.window

        area_province = list(area.provinces.values())[0]
        if area.is_land_area:
            data = {
                "-INFO_AREA_NAME-" : area.name,
                "-INFO_AREA_REGION_NAME-": self.world_data.province_to_region.get(area_province.province_id, None).name,
                "-INFO_AREA_TOTAL_DEV-": area.development,
                "-INFO_AREA_BASE_TAX-": area.base_tax,
                "-INFO_AREA_BASE_PRODUCTION-": area.base_production,
                "-INFO_AREA_BASE_MANPOWER-": area.base_manpower,
                "-INFO_AREA_INCOME-": area.income,
                "-INFO_AREA_TAX_INCOME-": area.tax_income,
                "-INFO_AREA_TRADE_POWER-": area.trade_power,
                "-INFO_AREA_GOODS_PRODUCED-": area.goods_produced,
                "-INFO_AREA_DOMINANT_TRADE_GOOD-": MapUtils.format_name(area.dominant_trade_good),
                "-INFO_AREA_SIZE_KM-": area.area_km2
            }

            window["-REGION_INFO_COLUMN-"].update(visible=False)
            window["-PROVINCE_INFO_COLUMN-"].update(visible=False)
            window["-AREA_INFO_COLUMN-"].update(visible=True)

            for element, attr_value in data.items():
                if attr_value is not None:
                    try:
                        window[element].update(value=attr_value, visible=True)
                    except (AttributeError, TypeError):
                        window[element].update(values=attr_value, visible=True)

            province_rows = []
            for province in area:
                row = [
                    province.name,
                    province.owner.name,
                    province.development,
                    province.trade_power,
                    MapUtils.format_name(province.religion),
                    MapUtils.format_name(province.culture),
                ]
                province_rows.append(row)

            window["-INFO_AREA_PROVINCES_TABLE-"].update(values=province_rows)

            total_production_element = window["-INFO_AREA_PRODUCTION_INCOME-"]
            total_production_income = round(sum(
                province.goods_produced * self.world_data.trade_goods.get(province.trade_goods, 0.00)
                for province in area), 2)

            total_production_element.update(value=total_production_income)

            total_income_element = window["-INFO_AREA_INCOME-"]
            total_income_element.update(value=round(area.tax_income + total_production_income, 2))

    def update_region_details(self, region: EURegion):
        """Updates the information displayed for a specific region in the UI."""
        window = self.window

        if region.is_land_region:
            data = {
                "-INFO_REGION_NAME-": region.name,
                "-INFO_REGION_TOTAL_DEV-": region.development,
                "-INFO_REGION_BASE_TAX-": region.base_tax,
                "-INFO_REGION_BASE_PRODUCTION-": region.base_production,
                "-INFO_REGION_BASE_MANPOWER-": region.base_manpower,
                "-INFO_REGION_TAX_INCOME-": region.tax_income,
                "-INFO_REGION_TRADE_POWER-": region.trade_power,
                "-INFO_REGION_GOODS_PRODUCED-": region.goods_produced,
                "-INFO_REGION_DOMINANT_TRADE_GOOD-": MapUtils.format_name(region.dominant_trade_good),
                "-INFO_REGION_SIZE_KM-": region.area_km2
            }

            window["-PROVINCE_INFO_COLUMN-"].update(visible=False)
            window["-AREA_INFO_COLUMN-"].update(visible=False)
            window["-REGION_INFO_COLUMN-"].update(visible=True)

            for element, attr_value in data.items():
                if attr_value is not None:
                    try:
                        window[element].update(value=attr_value, visible=True)
                    except (AttributeError, TypeError):
                        window[element].update(values=attr_value, visible=True)

            area_rows = []
            for area in region:
                row = [
                    area.name,
                    area.development,
                    area.trade_power,
                    MapUtils.format_name(area.dominant_religion),
                    MapUtils.format_name(area.dominant_culture)
                ]

                area_rows.append(row)

            window["-INFO_REGION_AREAS_TABLE-"].update(values=area_rows)
            total_production_element = window["-INFO_REGION_PRODUCTION_INCOME-"]
            total_production_income = round(sum(
                province.goods_produced * self.world_data.trade_goods.get(province.trade_goods, 0.00)
                for province in region.provinces), 2)

            total_production_element.update(value=total_production_income)

            total_income_element = window["-INFO_REGION_INCOME-"]
            total_income_element.update(value=round(region.tax_income + total_production_income, 2))

    def update_details_from_selected_item(self, selected_item: EUProvince|EUArea|EURegion):
        """Updates the information section in the window based on the user's seclected item.
        
        This can either be from the user searching for or clicking on a province, area, region, or country.
        
        Args:
            selected_item (EUProvince|EUArea|EURegion): The selected item to display details for.
        
        Returns:
            window (Window): The updated PySimpleGUI window.
        """
        if isinstance(selected_item, EUProvince):
            self.update_province_details(selected_item)

        elif isinstance(selected_item, EUArea):
            self.update_area_details(selected_item)

        elif isinstance(selected_item, EURegion):
            self.update_region_details(selected_item)

        return self.window.refresh()

    def ui_read_loop(self):
        """Main event loop for handling user interactions within the PySimpleGUI window.

        This method listens for and processes all user input events, including:
        
        - **Map Mode Changes:** Handles switching between different map modes.
        - **Search Functionality:** Processes user input for searching and displaying results.
        - **Results Navigation:** Allows users to select and navigate to provinces or entities based on search results.
        - **Reset Functionality:** Resets the map view to its original state.

        The loop continues to run until the window is closed or the user selects "Exit".
        It updates the window dynamically based on the events triggered by the user, 
        such as searching for provinces, going to specific entity locations, or changing map modes.
        
        Returns:
            None
        """
        window = self.window
        mode_names = {mode.value: mode for mode in self.painter.map_modes}

        while True:
            event, values = window.read(timeout=1)
            if event in {sg.WIN_CLOSED, "Exit", "-EXIT-"}:
                break

            if event == "-MAP_LOADED-":
                self.refresh_canvas_image()

            if event in mode_names:
                self.update_map_mode(mode_names[event])

            if event == "-LOAD_SAVEFILE-":
                new_savefile = sg.popup_get_file("Select a savefile to load", file_types=(("EU4 Save", "*.eu4"),))
                if new_savefile:
                    print(f"Loading new savefile: {new_savefile}....")
                    loading_image = self.display_loading_screen(message="Loading map....")

                    def load_savefile():
                        self.world_data.build_world(save_folder=self.save_folder, savefile=new_savefile)
                        self.window.write_event_value("-MAP_LOADED-", None)

                    threading.Thread(target=load_savefile, daemon=True).start()

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
                    selected_item = next((
                        item for item in self.search_results
                        if item.name.lower() == item_name.lower()), None)

                    self.selected_item = selected_item

            if event == "-GOTO-":
                if self.selected_item:
                    self.handler.go_to_entity_location(self.selected_item)
                    self.window = self.update_details_from_selected_item(self.selected_item)

            if event == "-RESET-":
                self.reset_canvas_to_initial()

    def display_map(self):
        """Displays the main UI window for the Europa Universalis IV map viewer.

        Initializes the GUI using the `PySimpleGUI` library.
        """
        sg.theme("DarkBlue")

        self.original_map = self.painter.draw_map()
        layout = self.create_layout()
        self.map_image = self.scale_image_to_fit(self.original_map)

        window = sg.Window("EU4 Map Viewer", 
            layout, 
            background_color=Layout.MEDIUM_FRAME_BG,
            finalize=True, 
            return_keyboard_events=True)

        self.window = window
        self.window.move_to_center()
        self.tk_canvas = window["-CANVAS-"].TKCanvas

        self.tk_image = self.image_to_tkimage(self.map_image)
        self.image_id = self.tk_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.handler = MapHandler(self, self.tk_canvas)
        self.handler.bind_events()

        self.ui_read_loop()
        self.window.close()
