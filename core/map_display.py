"""
Map Displaying and interacting with the Europa Universalis IV savegame viewing.

This module contains the implementation  for rendering 
the map, handling user interactions such as zooming, panning, and searching, 
and managing UI elements using PySimpleGUI and Tkinter.
"""


from __future__ import annotations

import FreeSimpleGUI as sg
import os
import threading
import tkinter as tk

from PIL import Image, ImageDraw, ImageFont, ImageTk
from sys import exit
from . import MapHandler, MapPainter, EUColors, EUWorldData
from . import Layout
from .layouts import constants
from .models import EUMapEntity, EUProvince, ProvinceType, EUArea, EURegion, EUTradeNode
from .models import MapMode
from .utils import draw_trade_value_pie_bytes, IconLoader, MapUtils


icon_loader = IconLoader()



class MapDisplayer:
    """Handles displaying the map and managing user interactions.

    This class is responsible for rendering the map, handling zooming and panning, 
    managing UI elements, and responding to user events such as searching and 
    selecting different map modes.

    Attributes:
        painter (MapPainter): The map painter instance responsible for drawing the map.
        saves_folder (str): The path of the saves folder, used for selecting files.
        world_data (EUWorldData): The world data associated with the map.

        handler (MapHandler): The event handler for managing interactions.
        image_id (int): The ID of the displayed image in the canvas.
        original_map (PIL.Image): The original unscaled backend map image.
        map_image (PIL.Image): The currently displayed backedn map image.
        tk_image (tk.PhotoImage): The Tkinter-compatible image for displaying.
        tk_canvas (tk.Canvas): The window's canvas for the displaying the current image.
        window (sg.Window): The PySimpleGUI window for the UI.

        canvas_size (tuple[int, int]): The `(x, y)` dimensions of the display canvas.
        max_scale (float): The maximum zoom level allowed.
        map_scale (float): The current zoom level of the map.
        min_scale (float): The minimum zoom level allowed.

        offset_x (int): The horizontal offset for panning.
        offset_y (int): The vertical offset for panning.

        show_map_borders (bool): If the map should display subdivision borders.
        selected_item: (EUProvince|EUArea|EURegion|None): The current selected item, to get information for
            and display in the window's information section, if any.
        search_results: (list[EUMapEntity]): The results from the user's search, if any.
    """
    def __init__(self, painter: MapPainter, saves_folder: str):
        self.painter = painter
        self.saves_folder = saves_folder
        self.world_data = None

        self.handler: MapHandler = None
        self.image_id = None
        self.original_map = None
        self.map_image = None
        self.tk_image = None
        self.tk_canvas = None
        self.window = None

        self.canvas_size: tuple[int, int] = None
        self.max_scale = 5.0
        self.map_scale = 1.0
        self.min_scale = 1.0

        self.offset_x = 0
        self.offset_y = 0

        self.show_map_borders = True
        self.selected_item = None
        self.search_results = []

    def send_message_callback(self, message: str):
        """Thread-safe callback to request a message be displayed in the GUI.

        Posts a event to the PySimpleGUI window so the message can be handled
        and displayed in the main thread.

        Args:
            message (str): The message to send.
        """
        self.window.write_event_value("-SEND_MESSAGE-", message)

    def send_message_to_multiline(self, message: str):
        """Displays a message in the multiline element of the GUI.

        Should only be called from the main thread, either directly or through `send_message_callback`.

        Args:
            message (str): The message to display.
        """
        self.window["-MULTILINE-"].update(value=message)
        self.window.refresh()

    def image_to_tkimage(self, image: Image.Image):
        """Converts a PIL Image to a TkInter Image."""
        return ImageTk.PhotoImage(image)

    def scale_image_to_fit(self, image: Image.Image):
        """Scales the map to fit within the canvas.
        
        Sets the new size of the map and also sets the minimum and maximum zoom levels.
        
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
        self.update_canvas(offset_x=0, offset_y=0)

        self.window.refresh()

    def clear_ui_window(self):
        for key in self.window.AllKeysDict:
            if not isinstance(key, str):
                continue

            element = self.window[key]
            if isinstance(element, sg.Text):
                element.update(value="")
            if isinstance(element, sg.Input):
                element.update(value="")

    def update_canvas(self, offset_x: int=None, offset_y: int=None):
        """Updates the canvas by applying all pan and/or zoom adjustments to the image.
        
        This is done after every zoom and pan event, or after changing the map mode or selected savefile.
        """
        if offset_x == None:
            offset_x = self.offset_x
        if offset_y == None:
            offset_y = self.offset_y

        self.tk_image = self.image_to_tkimage(self.map_image)
        self.tk_canvas.itemconfig(self.image_id, image=self.tk_image)
        self.tk_canvas.coords(self.image_id, offset_x, offset_y)

        self.window.refresh()

    def reset_canvas_to_initial(self):
        """Resets the canvas to its initial zoom and pan settings."""
        self.offset_x = 0
        self.offset_y = 0
        self.map_image = self.scale_image_to_fit(self.original_map)

        self.update_canvas()

    def refresh_canvas(self):
        """Refreshes the canvas after loading a new savefile.
        
        Draws the map for the new savefile and calls `rest_canvas_to_inital` to reset pan and zoom.
        """
        self.original_map = self.painter.get_cached_map_image(borders=self.show_map_borders)
        self.map_image = self.scale_image_to_fit(self.original_map)
        self.reset_canvas_to_initial()

    def update_details_from_selected_item(self, selected_item: EUMapEntity):
        """Updates the information section in the window based on the user's seclected item.
        
        This can either be from the user searching for or clicking on a province, area, region, or country.
        
        Args:
            selected_item (EUMapEntity): The selected item to display details for.
        
        Returns:
            window (Window): The updated PySimpleGUI window.
        """
        if isinstance(selected_item, EUProvince):
            self._update_province_details(selected_item)

        elif isinstance(selected_item, EUArea):
            self._update_area_details(selected_item)

        elif isinstance(selected_item, EURegion):
            self._update_region_details(selected_item)

        elif isinstance(selected_item, EUTradeNode):
            self._update_trade_node_details(selected_item)

        return self.window.refresh()

    def _update_province_details(self, province: EUProvince):
        """Checks the type of the province and calls the appropriate `update....province_details()` method."""
        if province.province_type == ProvinceType.OWNED:
            self.update_owned_province_details(province)
        elif province.province_type == ProvinceType.NATIVE:
            self.update_native_province_details(province)

    def update_owned_province_details(self, province: EUProvince):
        """Updates the information displayed for a specific province in the UI.

        This method retrieves the relevant data for a province, such as its name, owner, capital,
        development, tax, production, manpower, trade power, and fort level, and trade goods.

        Args:
            province (EUProvince): The province to be displayed.
        """
        window = self.window
        data = {
            "-INFO_PROVINCE_NAME-": province.name,
            "-INFO_PROVINCE_OWNER-": province.owner_name,
            "-INFO_PROVINCE_CAPITAL-": province.capital,
            "-INFO_PROVINCE_AREA_NAME-": self.world_data.province_to_area.get(province.province_id, None).name, 
            "-INFO_PROVINCE_REGION_NAME-": self.world_data.province_to_region.get(province.province_id, None).name,
            "-INFO_PROVINCE_LOCAL_AUTONOMY-": f"{province.local_autonomy}%",
            "-INFO_PROVINCE_LOCAL_DEVASTATION-": f"{province.devastation}%",
            "-INFO_PROVINCE_LOCAL_UNREST-": province.unrest,
            "-INFO_PROVINCE_TOTAL_DEV-": province.development,
            "-INFO_PROVINCE_BASE_TAX-": province.base_tax,
            "-INFO_PROVINCE_BASE_PRODUCTION-": province.base_production,
            "-INFO_PROVINCE_BASE_MANPOWER-": province.base_manpower,
            "-INFO_PROVINCE_TRADE_POWER-": province.trade_power,
            "-INFO_PROVINCE_HOME_NODE-": MapUtils.format_name(province.trade),
            "-INFO_PROVINCE_GOODS_PRODUCED-": province.goods_produced,
            "-INFO_PROVINCE_LOCAL_MANPOWER-": province.manpower,
            "-INFO_PROVINCE_LOCAL_SAILORS-": province.sailors,
            "-INFO_PROVINCE_SIZE_KM-": province.area_km2,
            "-INFO_PROVINCE_GARRISON_SIZE-": province.garrison,
            "-INFO_PROVINCE_CULTURE-": MapUtils.format_name(province.culture),
            "-INFO_PROVINCE_RELIGION-": MapUtils.format_name(province.religion),
        }

        window["-REGION_INFO_COLUMN-"].update(visible=False)
        window["-AREA_INFO_COLUMN-"].update(visible=False)
        window["-TRADE_NODE_INFO_COLUMN-"].update(visible=False)
        window["-NATIVE_PROVINCE_INFO_COLUMN-"].update(visible=False)
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
            fort_level_icon = icon_loader.get_icon(forts[province.fort_level])
            fort_level_element.update(filename=fort_level_icon)

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

        trade_info_element = self.window["-INFO_PROVINCE_TRADE_INFO_FRAME-"]
        if province.center_of_trade in centers_of_trade:
            inland_cot = icon_loader.get_icon(inland_centers_of_trade[province.center_of_trade])
            inland_trade_element.update(filename=inland_cot)

            cot = icon_loader.get_icon(centers_of_trade[province.center_of_trade])
            center_of_trade_element.update(filename=cot)
            trade_info_element.update(visible=True)
        else:
            trade_info_element.update(visible=False)

        hre_icon = icon_loader.get_icon("hre_province" if province.hre else "not_hre_province")
        hre_icon_element = self.window["-INFO_PROVINCE_IS_HRE-"]
        hre_icon_element.update(filename=hre_icon)

    def update_native_province_details(self, province: EUProvince):
        window = self.window
        data = {
            "-INFO_NATIVE_PROVINCE_NAME-": province.name,
            "-INFO_NATIVE_PROVINCE_AREA_NAME-": self.world_data.province_to_area.get(province.province_id, None).name, 
            "-INFO_NATIVE_PROVINCE_COLONIAL_REGION-": self.world_data.province_to_region.get(province.province_id, None).name,
            "-INFO_NATIVE_PROVINCE_TOTAL_DEV-": province.development,
            "-INFO_NATIVE_PROVINCE_BASE_TAX-": province.base_tax,
            "-INFO_NATIVE_PROVINCE_BASE_PRODUCTION-": province.base_production,
            "-INFO_NATIVE_PROVINCE_BASE_MANPOWER-": province.base_manpower,
            "-INFO_NATIVE_PROVINCE_TRADE_GOOD_NAME-": MapUtils.format_name(province.trade_goods),
            "-INFO_NATIVE_PROVINCE_SIZE_KM-": province.area_km2,
            "-INFO_NATIVE_PROVINCE_CULTURE-": MapUtils.format_name(province.culture),
            "-INFO_NATIVE_PROVINCE_RELIGION-": MapUtils.format_name(province.religion),
            "-INFO_NATIVE_PROVINCE_NATIVE_SIZE-": province.native_size * 1000,
            "-INFO_NATIVE_PROVINCE_NATIVE_HOSTILENESS-": province.native_hostileness,
            "-INFO_NATIVE_PROVINCE_NATIVE_FEROCITY-": province.native_ferocity
        }

        window["-REGION_INFO_COLUMN-"].update(visible=False)
        window["-AREA_INFO_COLUMN-"].update(visible=False)
        window["-TRADE_NODE_INFO_COLUMN-"].update(visible=False)
        window["-PROVINCE_INFO_COLUMN-"].update(visible=False)
        window["-NATIVE_PROVINCE_INFO_COLUMN-"].update(visible=True)

        for element, attr_value in data.items():
            if attr_value is not None:
                window_element = window[element]
                window_element.update(value=attr_value, visible=True)
            else:
                window[element].update(value=0)

        trade_good_element = self.window["-INFO_NATIVE_PROVINCE_TRADE_GOOD-"]
        trade_good_element.update(filename=icon_loader.get_icon(province.trade_goods), visible=True)

    def _update_area_details(self, area: EUArea):
        """Updates the information displayed for a specific area in the UI.

        This method retrieves the relevant data for an area, such as its name, region,
        total development, base tax, base production, and base manpower. It also updates
        the area provinces table with information for each province within the area.

        Args:
            area (EUArea): The area to be displayed.
        """
        window = self.window

        if area.is_land_area:
            area_province = list(area.provinces.values())[0]
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
            window["-NATIVE_PROVINCE_INFO_COLUMN-"].update(visible=False)
            window["-PROVINCE_INFO_COLUMN-"].update(visible=False)
            window["-TRADE_NODE_INFO_COLUMN-"].update(visible=False)
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
                    province.owner_name,
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

    def _update_region_details(self, region: EURegion):
        """Updates the information displayed for a specific region in the UI.
        
        This method retrieves the relevant data for an region, such as its name, total development, and income. 
        It also updates the region areas table with information for each area within the region.

        Args:
            region (EURegion): The region to be displayed.
        """
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
            window["-NATIVE_PROVINCE_INFO_COLUMN-"].update(visible=False)
            window["-AREA_INFO_COLUMN-"].update(visible=False)
            window["-TRADE_NODE_INFO_COLUMN-"].update(visible=False)
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

    def _update_trade_node_details(self, trade_node: EUTradeNode):
        """Updates the information displayed for a specific trade node in the UI.
        
        This method retrieves the relevant data for an trade node, such as its name, total development, and incoming and outgoing trade value. 
        It also updates the trade node's table with information for each country that contributes trade to the node.

        Args:
            trade_node (EUTradeNode): The trade node to be displayed.
        """
        window = self.window
        node_province = list(trade_node.provinces.values())[0]
        
        data = {
            "-INFO_TRADE_NODE_NAME-": trade_node.name,
            "-INFO_TRADE_NODE_REGION_NAME-": f"{self.world_data.province_to_region.get(node_province.province_id).name} Charter",
            "-INFO_TRADE_NODE_PRIVATEER_EFFICIENCY-": f"{trade_node.privateer_efficiency_modifier:.2f}",
            "-INFO_TRADE_NODE_NUM_LIGHT_SHIPS-": trade_node.num_light_ships,
            "-INFO_TRADE_NODE_INCOMING_VALUE-": f"+{trade_node.incoming_value_total:.2f}",
            "-INFO_TRADE_NODE_LOCAL_VALUE-": f"+{trade_node.local_trade_value:.2f}",
            "-INFO_TRADE_NODE_OUTGOING_VALUE-": f"-{trade_node.outgoing_trade_value:.2f}",
            "-INFO_TRADE_NODE_TOTAL_REMAINING_VALUE-": f"{trade_node.remaining_total_value:.2f}",
        }

        window["-PROVINCE_INFO_COLUMN-"].update(visible=False)
        window["-NATIVE_PROVINCE_INFO_COLUMN-"].update(visible=False)
        window["-AREA_INFO_COLUMN-"].update(visible=False)
        window["-REGION_INFO_COLUMN-"].update(visible=False)
        window["-TRADE_NODE_INFO_COLUMN-"].update(visible=True)

        for element, attr_value in data.items():
            if attr_value is not None:
                try:
                    window[element].update(value=attr_value, visible=True)
                except (AttributeError, TypeError):
                    window[element].update(values=attr_value, visible=True)

        # trade_power_pie = draw_trade_value_pie_bytes(trade_node=trade_node)
        # if trade_power_pie:
        #     window["-INFO_TRADE_NODE_RETAINED_PIE-"].update(data=trade_power_pie)

        participant_rows = []
        for participant in trade_node:
            country = self.world_data.countries.get(participant.tag)
            country_name = country.name if country.name else country.tag

            row = [
                country_name,
                participant.has_merchant_in_node,
                participant.node_merchant_mission,
                participant.total_trade_income,
                participant.ship_trade_power,
                participant.trade_power
            ]

            participant_rows.append(row)

        if not participant_rows:
            participant_rows = [["No", "Partipants", "In", "This", "Trade", "Node"], []]
        window["-INFO_TRADE_NODE_PARTICIPANTS_TABLE-"].update(values=participant_rows)

    def handle_setup_complete(self):
        """Handles display adjustments after game and save data is loaded for the first time."""
        self.painter.set_base_world_image(image=self.world_data.world_image)

        self.refresh_canvas()
        self.window["POLITICAL"].update(button_color=(constants.LIGHT_TEXT, constants.SELECTED_BUTTON_BG))
        self.window["-SAVEFILE_DATE-"].update(value=f"The World in {self.world_data.current_save_date}")

        self.handler = MapHandler(displayer=self, tk_canvas=self.tk_canvas)
        self.handler.bind_events()

    def handle_save_loaded(self):
        """Handles map reloading when a new save file is loaded."""
        self.painter.clear_cache()
        self.refresh_canvas()

        self.window["-SAVEFILE_DATE-"].update(value=f"The World in {self.world_data.current_save_date}")
        self.send_message_callback("Save loaded!")

        self.handler.disabled = False

    def handle_load_savefile(self):
        """Handles loading a new save file."""
        new_savefile = sg.popup_get_file("Select a savefile to load", file_types=(("EU4 Save", "*.eu4"),))
        if new_savefile:
            self.handler.disabled = True

            self.clear_ui_window()
            self.send_message_callback(rf"Loading new savefile: {new_savefile}....")
            self.display_loading_screen(message="Loading map....")

            def load_savefile():
                self.world_data.build_world(save_folder=self.saves_folder, savefile=new_savefile)
                self.window.write_event_value("-SAVE_LOADED-", None)

            threading.Thread(target=load_savefile, daemon=True).start()

    def handle_border_toggle(self, values):
        """Toggles displaying map borders."""
        self.show_map_borders = values["-SHOW_MAP_BORDERS-"]
        self.original_map = self.painter.get_cached_map_image(borders=self.show_map_borders)
        self.map_image = self.original_map.resize(self.map_image.size, Image.Resampling.LANCZOS)
        self.update_canvas()

    def handle_map_mode_change(self, map_modes: dict[str, MapMode], new_map_mode: MapMode):
        """Updates the map mode and redraws the map for that mode.
        
        Args:
            map_modes: (dict[str, MapMode]): The possible map modes, used to determine which buttons to color.
            map_mode (MapMode): The new map mode selected by the user.
        """
        if new_map_mode == self.painter.map_mode:
            return

        self.send_message_callback("Loading map....")
        self.display_loading_screen(message="Loading map....")

        self.painter.map_mode = new_map_mode
        self.original_map = self.painter.get_cached_map_image(borders=self.show_map_borders)
        self.map_image = self.original_map.resize(self.map_image.size, Image.Resampling.LANCZOS)

        self.send_message_callback(f"Displaying map {self.painter.map_mode.value.capitalize()}")
        self.color_map_mode_buttons(map_modes)
        self.reset_canvas_to_initial()

    def color_map_mode_buttons(self, map_modes: dict[str, MapMode]):
        """Colors the map mode buttons depending on which map mode is the current one.
        
        The current map mode will be highlighted in a brighter blue.
        
        Args:
            map_modes (dict[str, MapMode]): The possible map modes.
        """
        new_map_mode = self.painter.map_mode
        for map_mode in map_modes:
            map_mode_button = self.window[map_mode]
            button_color = (constants.LIGHT_TEXT, constants.SELECTED_BUTTON_BG if map_mode == new_map_mode.name else constants.BUTTON_BG)
            map_mode_button.update(button_color=button_color)

    def handle_search_for(self, values):
        """Handles searching for entities in the world data.
        
        Updates the window's results field to show the entities that match the user's search.
        If there are any matches, the user can click its row within results and choose to go to its loation
        and display more information via the `GO TO` button.
        """
        self.window["-CLEAR-"].update(visible=True)
        exact_matches_only = values["-EXACT_MATCH-"]
        search_param = values["-SEARCH-"].strip().lower()

        if not search_param:
            self.window["-RESULTS-"].update(values=[], visible=False)
            self.window["-CLEAR-"].update(visible=False)
            return

        matches = self.world_data.search(
            exact_matches_only=exact_matches_only, search_param=search_param)
        self.search_results = matches

        name_matches = [item.name for item in self.search_results]
        if name_matches:
            self.window["-RESULTS-"].update(values=name_matches, visible=True)
            self.window["-GOTO-"].update(visible=True)
        else:
            self.window["-RESULTS-"].update(values=[])
            self.window["-GOTO-"].update(visible=False)

    def handle_result_select(self, values):
        """Handles selection of a search result.
        
        Sets the current `selected_item`, that the user can visit via the `GO TO` button.
        """
        selected = values["-RESULTS-"]
        if selected:
            item_name = selected[0]
            selected_item = next((
                item for item in self.search_results
                if item.name.lower() == item_name.lower()), None)

            self.selected_item = selected_item

    def handle_go_to(self):
        """Handles navigation to the selected entity location and displays its information in the details panel."""
        if self.selected_item:
            self.handler.go_to_entity_location(self.selected_item)
            self.window = self.update_details_from_selected_item(self.selected_item)

    def handle_table(self, event: tuple, table_key: str):
        """Handles selection of a table column or row."""
        row, col = event[2]
        if row == -1:
            self.window[table_key].sort_by_column(col)

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
        """
        window = self.window
        mode_names = {mode.value.upper(): mode for mode in self.painter.map_modes}

        while True:
            event, values = window.read(timeout=1)
            if event in {sg.WIN_CLOSED, "Exit", "-EXIT-"}:
                break

            # Always listen for these events, as they are also used for setup (when the handler is disabled).
            if event == "-SEND_MESSAGE-":
                message = values[event]
                self.send_message_to_multiline(message=message)

            if event == "-SETUP_COMPLETE-":
                self.handle_setup_complete()

            if event == "-SAVE_LOADED-":
                self.handle_save_loaded()

            if event == "-LOAD_SAVEFILE-":
                self.handle_load_savefile()

            # Following events are dependent on the handler are disabled during setup.
            if not self.handler or getattr(self.handler, "disabled", False):
                continue

            if event == "-SHOW_MAP_BORDERS-":
                self.handle_border_toggle(values)

            if event in mode_names:
                self.handle_map_mode_change(mode_names, mode_names[event])

            if event in {"-EXACT_MATCHES-", "-SEARCH-"}:
                self.handle_search_for(values)

            if event == "-RESULTS-":
                self.handle_result_select(values)

            if event == "-GOTO-":
                self.handle_go_to()

            if isinstance(event, tuple) and "TABLE" in event[0] and event[1] == "+CLICKED+":
                self.handle_table(event=event, table_key=event[0])

            if event == "-RESET-":
                self.reset_canvas_to_initial()

    def _load_game_data_async(self, maps_folder: str, tags_folder: str):
        """Loads game data and initializes the world for display asynchronously.

        Args:
            maps_folder (str): The folder that contains the world definition files.
            tags_folder (str): The folder that contains the tag (country) definitions.

        This function:
        - Loads color and tag data needed to parse the world map.
        - Loads and parses the EU4 world data from map files.
        - If a default savefile is present, builds the world state from it.
        - Caches and scales the world map image for display.
        - Updates relevant UI elements, including the map canvas and savefile date.
        - Binds map interaction events via MapHandler.

        Should be called from a background thread to avoid blocking the UI.
        """
        default_savefile_path = os.path.join(self.saves_folder, "default_1444.eu4")
        if not os.path.exists(default_savefile_path):
            self.send_message_callback("Can't find default game data.... closing program.")
            exit(f"Error: Can't find default game data at {default_savefile_path}")
            return

        self.send_message_callback("Loading game data....")
        colors = EUColors.load_colors(maps_folder=maps_folder, tags_folder=tags_folder)
        world = EUWorldData.load_world_data(maps_folder=maps_folder, colors=colors)

        world.update_status_callback = self.send_message_callback
        world.build_world(self.saves_folder, default_savefile_path)
        self.world_data = world

        self.painter.world_data = self.world_data
        self.painter.colors = colors
        self.painter.update_status_callback = self.send_message_callback

        self.window.write_event_value("-SETUP_COMPLETE-", None)

    def create_layout(self):
        """Creates the layout that will be used for the UI and sets the canvas size.
        
        Returns:
            layout (list[list[...]]): The layout for the Window.
        """
        self.set_canvas_size()
        return Layout.build_layout(self.canvas_size, self.painter.map_modes)

    def set_canvas_size(self):
        screen_width, screen_height = sg.Window.get_screen_size()
        canvas_width_max = min(Layout.CANVAS_WIDTH_MAX, int(screen_width * 0.9))

        if self.original_map:
            map_width, map_height = self.original_map.size
        else:
            map_width, map_height = constants.DEFAULT_MAP_SIZE

        canvas_height = int(canvas_width_max * (map_height / map_width))
        self.canvas_size = (canvas_width_max, canvas_height)

    def launch(self, maps_folder: str, tags_folder: str):
        """Initializes and displays the main EU4 Map Viewer UI window.

        Args:
            maps_folder (str): The folder that contains the world definition files.
            tags_folder (str): The folder that contains the tag (country) definitions.

        This method performs the following steps:
        - Sets up the PySimpleGUI theme and window layout.
        - Initializes and displays a loading screen.
        - Loads and displays the base map image in a canvas.
        - Starts a background thread to asynchronously load game data.
        - Enters the main UI event loop to handle user interactions.
        - Closes the window upon exiting the event loop.

        This is the main entry point for launching the application's interface.
        """
        sg.theme("DarkBlue")

        layout = self.create_layout()
        window = sg.Window(
            title="EU4 Map Viewer", 
            layout=layout,
            background_color=constants.MEDIUM_FRAME_BG,
            finalize=True, 
            return_keyboard_events=True)

        self.window = window
        self.window.move_to_center()
        self.window["-SAVEFILE_DATE-"].update(value="")

        self.tk_canvas = window["-CANVAS-"].TKCanvas
        self.display_loading_screen(message="Loading game data....")

        self.tk_image = self.image_to_tkimage(self.map_image)
        self.image_id = self.tk_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.display_loading_screen(message="Loading game data....")

        # Run setup in the background so the GUI doesn't freeze.
        threading.Thread(target=self._load_game_data_async, args=(maps_folder, tags_folder), daemon=True).start()

        self.ui_read_loop()

        self.window.close()
