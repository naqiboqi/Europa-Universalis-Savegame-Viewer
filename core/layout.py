"""
Main layout builder for the Europa Universalis world view.

This module defines the layout logic for displaying the complete world state, 
including provinces, areas, and regions. It integrates the sub-layouts into a 
unified interface used in the core UI.
"""


import FreeSimpleGUI as sg
import os

from .layouts import constants
from .layouts import LayoutHelper
from .layouts import ProvinceLayout, AreaLayout, RegionLayout
from .utils import IconLoader


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
icons_folder = os.path.join(base_dir, "data", "icons")

icon_loader = IconLoader()
icon_loader.icons_folder = icons_folder



class Layout:
    """Main layout builder for the Europa Universalis world viewer."""

    CANVAS_WIDTH_MAX = 1200
    """Maximum width of the canvas."""

    @staticmethod
    def create_options_frame():
        load_save_button = sg.Button(
            "LOAD SAVEFILE", 
            key="-LOAD_SAVEFILE-",
            button_color=(constants.GOLD_FRAME_UPPER, constants.BUTTON_BG), 
            font=("Garamond", 12, "bold"))

        button_frame = sg.Frame("", [
            [load_save_button]
        ], background_color=constants.SUNK_FRAME_BG,
        border_width=0,
        element_justification="center",
        expand_x=True,
        relief=sg.RELIEF_GROOVE, 
        pad=(10, 10))

        return button_frame

    @staticmethod
    def create_window_header():
        """Creates the header for the window.
        
        This section contains the information displayed when hovering over parts of the map.
        
        Returns:
            frame (Frame): The frame containing the map info.
        """
        header_text = sg.Text(
            "", 
            key="-SAVEFILE_DATE-",
            background_color=constants.RED_BANNER_BG,
            border_width=2,
            font=("Georgia", 12, "bold"), 
            justification="center", 
            pad=(5, 5),
            relief=sg.RELIEF_RIDGE,
            size=(20, 1), 
            text_color=constants.LIGHT_TEXT)

        info_text = sg.Multiline(
            default_text="Hover over an area to get more information!", 
            key="-MULTILINE-",
            background_color=constants.SUNK_FRAME_BG,
            border_width=3,
            disabled=True,
            font=("Georgia", 12),
            justification="center",
            no_scrollbar=True,
            pad=(5, 5),
            size=(Layout.CANVAS_WIDTH_MAX // 20, 1),
            text_color=constants.LIGHT_TEXT,
            write_only=True)

        load_savefile_button = sg.Button( 
            "LOAD SAVEFILE",
            key="-LOAD_SAVEFILE-",
            border_width=2, 
            font=("Georgia", 10, "bold"),
            button_color=(constants.LIGHT_TEXT, constants.BUTTON_BG),
            pad=(5, 5),
            size=(15, 1))

        exit_button = sg.Button(
            "EXIT",
            key="-EXIT-",
            border_width=2,
            font=("Georgia", 10, "bold"),
            button_color=(constants.LIGHT_TEXT, constants.BUTTON_BG),
            pad=(5, 5),
            size=(15, 1))

        header_row = [
            header_text, 
            sg.Push(background_color=constants.LIGHT_FRAME_BG), 
            info_text, 
            sg.Push(background_color=constants.LIGHT_FRAME_BG), 
            load_savefile_button, exit_button
        ]

        header_column = sg.Column(
            [header_row], 
            background_color=constants.LIGHT_FRAME_BG,
            element_justification="center", 
            expand_x=True,
            justification="center", 
            pad=(0, 0))

        return LayoutHelper.add_border(
            layout=[[header_column]],
            borders=[
                (constants.GOLD_FRAME_LOWER, 3, sg.RELIEF_RIDGE),
                (constants.GOLD_FRAME_UPPER, 3, sg.RELIEF_RIDGE)],
            pad=(2, 2),
            expand_x=True)  

    @staticmethod
    def create_search_column():
        """Creates the search column section.
        
        This section contains the search input and output fields and the search buttons.
        
        Returns:
            column (Column): The column containing the search section.
        """
        search_label = LayoutHelper.create_text_with_frame(
            "Search", 
            content_color=constants.LIGHT_TEXT, 
            expand_x=True,
            frame_background_color=constants.RED_BANNER_BG,
            justification="center",
            relief=sg.RELIEF_RIDGE)

        search_input = sg.Input(
            key="-SEARCH-", 
            background_color=constants.MEDIUM_FRAME_BG,
            enable_events=True, 
            font=("Georgia", 12),
            pad=(10, 10), 
            size=(26, 1), 
            text_color=constants.LIGHT_TEXT)

        matches_checkbox = sg.Checkbox(
            "Exact matches only?", 
            key="-EXACT_MATCH-", 
            background_color=constants.LIGHT_FRAME_BG,
            enable_events=True, 
            font=("Georgia", 11), 
            text_color=constants.LIGHT_TEXT)

        input_frame= sg.Frame("", [
            [search_label],
            [search_input],
            [matches_checkbox]
        ], background_color=constants.LIGHT_FRAME_BG,
        border_width=0,
        element_justification="center",
        pad=(10, 10))

        matches_output = sg.Listbox(
            values=[], 
            key="-RESULTS-", 
            background_color=constants.DARK_FRAME_BG,
            enable_events=True, 
            font=("Georgia", 12), 
            pad=(0, 10),
            size=(26, 5),
            sbar_arrow_color=constants.GOLD_FRAME_UPPER,
            sbar_background_color=constants.RED_BANNER_BG,
            sbar_trough_color=constants.GOLD_FRAME_LOWER,
            sbar_relief=sg.RELIEF_GROOVE,
            sbar_width=5,
            text_color=constants.LIGHT_TEXT,
            visible=False)

        goto_button = sg.Button(
            "Go to",
            key="-GOTO-",
            button_color=(constants.LIGHT_TEXT, constants.BUTTON_BG),
            font=("Garamond", 12, "bold"),
            pad=(15, 10),
            visible=False)

        clear_button = sg.Button(
            "Clear",
            key="-CLEAR-",
            button_color=(constants.LIGHT_TEXT, constants.BUTTON_BG),
            font=("Garamond", 12, "bold"),
            pad=(15, 10),
            visible=False)

        output_frame = sg.Frame("", [
            [matches_output],
            [goto_button],
            [clear_button]
        ], background_color=constants.LIGHT_FRAME_BG, 
        border_width=0,
        element_justification="center",
        pad=(10, 10))

        search_frame = sg.Frame("", [
            [sg.Push(constants.LIGHT_FRAME_BG), input_frame, sg.Push(constants.LIGHT_FRAME_BG)],
            [sg.Push(constants.LIGHT_FRAME_BG), output_frame, sg.Push(constants.LIGHT_FRAME_BG)]
        ], background_color=constants.LIGHT_FRAME_BG,
        border_width=5,
        expand_x=True,
        expand_y=True, 
        pad=(10, 10), 
        relief=sg.RELIEF_GROOVE,  
        title_color=constants.LIGHT_TEXT)

        return sg.Column([
            [search_frame]
        ], background_color=constants.LIGHT_FRAME_BG,
        expand_x=True,
        expand_y=True, 
        element_justification="left",
        justification="left",
        pad=((10, 5), (10, 10)), 
        vertical_alignment="top")

    @staticmethod
    def create_map_canvas_frame(canvas_size: tuple[int, int], key: str):
        """Creates a bordered frame containing the map canvas.
        
        Args:
            canvas_size (tuple[int, int]): The `(x, y)` size of the canvas.
            key (str): The string that will be returned from `window.read()` when the canvas is interacted with.
                Should follow the format `-NAME-` for clarity.
        
        Returns:
            frame (Frame): The frame containing the canvas.
        """
        canvas_frame = sg.Frame("", [
            [sg.Canvas(background_color="black", size=canvas_size, key=key, pad=(0, 0))]
        ], background_color=constants.LIGHT_FRAME_BG, relief=sg.RELIEF_GROOVE, pad=(0, 0), border_width=5)

        return LayoutHelper.add_border(
            layout=[[canvas_frame]], 
            borders=[
                (constants.GOLD_FRAME_LOWER, 3, sg.RELIEF_RIDGE),
                (constants.GOLD_FRAME_UPPER, 3, sg.RELIEF_RIDGE)],
            pad=(15, 10))

    @staticmethod
    def create_options_frame(map_modes: dict):
        """Creates the map modes frame for selecting map modes.
        
        Args:
            map_modes (dict[MapMode]): The possible map modes to choose from when displaying the map.
        
        Returns:
            frame (Frame): The frame containing the map mode buttons.
        """
        map_mode_label = LayoutHelper.create_text_with_frame(
            "Map Modes",
            content_color=constants.LIGHT_TEXT,
            font=("Georgia", 12, "bold"),
            frame_background_color=constants.RED_BANNER_BG,
            justification="center",
            pad=(10, 10),
            relief=sg.RELIEF_RIDGE,
            size=(10, 1))

        borders_checkbox = sg.Checkbox(
            "Show Map Borders?",
            default=True,
            key="-SHOW_MAP_BORDERS-", 
            background_color=constants.DARK_FRAME_BG,
            enable_events=True, 
            font=("Georgia", 11), 
            text_color=constants.LIGHT_TEXT)

        reset_button = sg.Button(
            "RESET VIEW",
            key="-RESET-",
            button_color=(constants.LIGHT_TEXT, constants.BUTTON_BG),
            font=("Garamond", 10, "bold"),
            pad=(15, 15),
            visible=True)

        map_mode_buttons = [
            sg.Button(
                mode.name,
                key=mode.value,
                button_color=(constants.LIGHT_TEXT, constants.BUTTON_BG),
                font=("Garamond", 10, "bold"),
                pad=(15, 15),
                visible=True)
            for mode in map_modes
        ]

        map_mode_frame = sg.Frame("", [
            [map_mode_label],
            [borders_checkbox],
            [reset_button],
            *[[button] for button in map_mode_buttons]
        ], background_color=constants.SUNK_FRAME_BG,
        border_width=5,
        element_justification="center", 
        relief=sg.RELIEF_GROOVE, 
        pad=(0, 0))

        return LayoutHelper.add_border(
            layout=[[map_mode_frame]],
            borders=[
                (constants.GOLD_FRAME_LOWER, 2, sg.RELIEF_RIDGE),
                (constants.GOLD_FRAME_UPPER, 2, sg.RELIEF_RIDGE)],
            pad=(10, 10))

    @staticmethod
    def build_layout(canvas_size: tuple[int, int], map_modes: dict):
        """Driver method that builds the layout to be used within a PySimpleGUI|FreeSimpleGUI `Window` element.
        
        Args:
            canvas_size (tuple[int, int]): The `(x, y)` size of the canvas determined by the display size.
            map_modes (dict[MapMode]): The possible map modes to choose from when displaying the map.
        """
        window_header = Layout.create_window_header()

        selected_info_frame = sg.Frame("", [
            [
                Layout.create_search_column(), 
                ProvinceLayout.create_province_info_column(), 
                AreaLayout.create_area_info_column(),
                RegionLayout.create_region_info_column()
            ]
        ], key="-WORLD_INFO-",
        background_color=constants.MEDIUM_FRAME_BG, 
        border_width=5,
        expand_x=True,  
        expand_y=True,
        pad=(0, 0), 
        relief=sg.RELIEF_GROOVE)

        bordered_info = LayoutHelper.add_border(
            layout=[[selected_info_frame]],
            borders=[
                (constants.GOLD_FRAME_LOWER, 3, sg.RELIEF_RIDGE),
                (constants.GOLD_FRAME_UPPER, 3, sg.RELIEF_RIDGE)],
            pad=(15, 10),
            expand_x=True,
            expand_y=True)

        canvas_frame = Layout.create_map_canvas_frame(canvas_size=canvas_size, key="-CANVAS-")
        map_mode_frame = Layout.create_options_frame(map_modes=map_modes)

        display_frame = sg.Frame("", [
            [canvas_frame, map_mode_frame]
        ], background_color=constants.LIGHT_FRAME_BG,
        border_width=0,
        vertical_alignment="center")

        display_column = sg.Column([
            [display_frame]
        ], background_color=constants.MEDIUM_FRAME_BG,
        vertical_alignment="center")

        layout = [
            [window_header],
            [display_column],
            [bordered_info],
        ]

        return layout
