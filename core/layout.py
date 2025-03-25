import FreeSimpleGUI as sg
import os

from .utils import IconLoader


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
icons_folder = os.path.join(base_dir, "data", "icons")

icon_loader = IconLoader()
icon_loader.icons_folder = icons_folder
print(icon_loader.icons_folder)



class Layout:
    CANVAS_WIDTH_MAX = 1200

    ## Some color constants
    LIGHT_TEXT = "#d2d2d2"
    GOLD_FRAME_UPPER = "#b68950"
    GOLD_FRAME_LOWER = "#9f7240"
    RED_BANNER_BG = "#561b19"
    TOP_BANNER_BG = "#353c25"
    SECTION_BANNER_BG = "#172f48"
    LIGHT_FRAME_BG = "#344048"
    MEDIUM_FRAME_BG = "#2a343b"
    DARK_FRAME_BG = "#283239"
    SUNK_FRAME_BG =  "#252e34"
    WINDOW_BACKGROUND = ""
    BUTTON_BG = "#314b68"
    BUTTON_FG = "#394d66"
    GREEN_TEXT = "#2b8334"


    @staticmethod
    def add_border(
        layout: list[list], 
        inner_border: tuple[str, int], 
        outer_border: tuple[str, int], 
        pad: tuple[int, int]=None, 
        expand_x: bool=False, 
        expand_y: bool=False):
        """
        Creates a raised border around the given layout elements.
        
        Args:
            layout (list[list]): The layout to wrap.
            inner_border (tuple[str, int]): Specifies the hex color and width of the inner border.
            outer_border (tuple[str, int]): Specifies the hex color and width of the outer border.
            pad (tuple[int, int]): Amount of padding to put around each frame in pixels (left/right, top/bottom).
            expand_x (bool): If True the element will automatically expand in the X direction to fill available space.
            expand_y (bool): If True the element will automatically expand in the Y direction to fill available space
        
        Returns:
            outer_frame (Frame): The create frame with the border .
        """
        inner_color, inner_width = inner_border
        inner_frame = sg.Frame("", 
            layout=layout, 
            relief=sg.RELIEF_SUNKEN, 
            border_width=inner_width, 
            background_color=inner_color, 
            pad=pad,
            expand_x=expand_x,
            expand_y=expand_y)

        outer_color, outer_width = outer_border
        outer_frame = sg.Frame("",
            layout=[[inner_frame]],
            relief=sg.RELIEF_RAISED,
            border_width=outer_width,
            background_color=outer_color,
            pad=pad,
            expand_x=expand_x,
            expand_y=expand_y)

        return outer_frame

    @staticmethod
    def create_button(
        name: str,
        key: str,
        font_color: str,
        button_color: str,
        font: tuple[str, int, str]=("Garamond", 10, "bold"),
        visible: bool=True):
        """
        Creates a PySimpleGUI button with the given settings.
        
        Args:
            name (str): The text that will appear on the button.
            key (str): The string that will be returned from `window.read()` when the button is clicked.
                Should follow the format `-NAME-` for clarity.
            font_color (str): The hex color for the button's text.
            button_color (str): The hex color for the button's background.
            font (tuple[str, int, str]|tuple[str, int]): Specifies the font family for the text content
                (font_name, font_size, "bold"/"italic"/"underline"/"overstrike").
            visible (bool): If the button is initially visible.
        
        Returns:
            button (Button): The created button
        """
        return sg.Button(
            name,
            key=key, 
            pad=(5, 5), 
            font=font, 
            button_color=(font_color, button_color),
            visible=visible)

    @staticmethod
    def create_text_with_frame(
        content: str,
        content_color: str,
        frame_background_color: str,
        frame_border_width: int=None,
        content_background_color: str=None,
        font: tuple[str, int, str]=("Georgia", 12, "bold"),
        justification: str=None,
        key: str=None,
        relief: str=None,
        size: tuple[int, int]=(None, None),
        expand_x=False):
        """
        Creates text with a framed background.
        
        Args:
            content (str): The text content.
            content_color (str): The hex color for the text content.
            frame_background_color (str): The hex color for the background.
            content_background_color (str): The hex color for the text background.
                is set to `frame_background_color` as default.
            font (tuple[int, str]|tuple[int, str, str]): Specifies the font family for the text content
                (font_name, font_size, "bold"/"italic"/"underline"/"overstrike").
            justification (str): How the string should be alligned ("left"/"right"/"center").
            key (str): The string that will be used to access/edit the text value.
                Should follow the format `-NAME-` for clarity.
            default_text_value (str): The default text to show.
            size (tuple[int, int]): The `(x, y)` character limit of the text.
            relief (str): Relief style
            expand_x: If True the element will automatically expand in the X direction to fill available space.
        
        Returns:
            frame (Frame): The frame containing the wrapped text.
        """
        text = sg.Text(
            content, 
            font=font, 
            background_color=content_background_color or frame_background_color,
            text_color=content_color, 
            key=key,
            justification=justification,
            size=size,
            expand_x=expand_x)

        return sg.Frame("", [
            [text]
        ], background_color=frame_background_color, 
        border_width=frame_border_width,
        element_justification="left", 
        pad=(5, 5), 
        relief=relief,
        expand_x=expand_x)

    @staticmethod
    def create_text_with_inline_label(
        label_name: str,
        label_colors: tuple[str, str],
        text_colors: tuple[str, str],
        text_field_size: tuple[int, int],
        text_key: str,
        default_text_value: str="",
        font: tuple[str, int, str]=("Georgia", 12),
        justification: str=None,
        visible_field: bool=True,
        expand_x: bool=False):
        """
        Creates text with a label inline with a value field.
        
        Args:
            label_name (str): The name of the text label.
            label_colors (tuple[str, str]): The label font and label background hex colors.
            text_colors (tuple[str, str]): The text font and field background hex colors.
            text_field_size (tuple[int, int]): Size of the text field as (width, height).
            text_key (str): The string that will be used to access/edit the text value.
                Should follow the format `-NAME-` for clarity.
            default_text_value (str): The default text to show.
            font (tuple[str, int, str]|tuple[str, int]): Specifies the font family for the text content
                (font_name, font_size, "bold"/"italic"/"underline"/"overstrike").
            justification (str): How the string should be alligned ("left"/"right"/"center").
            visible_field (bool): If the field is initially visible.
            expand_x: If True the element will automatically expand in the X direction to fill available space.
        
        Returns:
            texts (tuple[Text, Text]): The label and inline text field.
        """
        label_text_color, label_background = label_colors
        label_text = sg.Text(
            label_name, 
            font=font, 
            text_color=label_text_color, 
            background_color=label_background,
            justification=justification)

        text_color, field_background = text_colors
        value_text = sg.Text(
            default_text_value, 
            key=text_key, 
            font=font, 
            text_color=text_color, 
            background_color=field_background, 
            size=text_field_size,
            justification=justification,
            visible=visible_field,
            expand_x=expand_x)

        return label_text, value_text

    @staticmethod
    def create_window_header():
        """Creates the header for the window.
        
        This section contains the information displayed when hovering over parts of the map.
        
        Returns:
            frame (Frame): The frame containing the map info.
        """
        header_text = sg.Text(
            "Map Information", 
            font=("Georgia", 18, "bold"), 
            justification="center", 
            size=(30, 1), 
            pad=(0, 10),
            text_color=Layout.LIGHT_TEXT,
            background_color=Layout.TOP_BANNER_BG,
            relief=sg.RELIEF_RAISED,
            border_width=2)

        info_text = sg.Multiline(
            default_text="Hover over an area to get more information!", 
            disabled=True, 
            justification="center",
            size=(Layout.CANVAS_WIDTH_MAX // 20, 1),
            write_only=True, 
            key="-MULTILINE-",
            no_scrollbar=True,
            background_color=Layout.DARK_FRAME_BG,
            text_color=Layout.LIGHT_TEXT,
            font=("Georgia", 14),
            border_width=3,
            pad=(5, 5))

        layout = [
            [sg.Column([
                [header_text],
                [info_text],
            ], justification="center", 
            element_justification="center", 
            expand_x=True, 
            pad=(5, 5), 
            background_color=Layout.LIGHT_FRAME_BG)]
        ]

        bordered_layout = Layout.add_border(
            layout=layout,
            inner_border=(Layout.GOLD_FRAME_LOWER, 2),
            outer_border=(Layout.GOLD_FRAME_UPPER, 2),
            pad=(5, 5),
            expand_x=True)

        return bordered_layout

    @staticmethod
    def create_search_column():
        """Creates the search column section.
        
        This section contains the search input and output fields and the search buttons.
        
        Returns:
            column (Column): The column containing the search section.
        """
        search_label = Layout.create_text_with_frame(
            "Search", 
            content_color=Layout.LIGHT_TEXT, 
            frame_background_color=Layout.RED_BANNER_BG,
            expand_x=True,
            justification="center",
            relief=sg.RELIEF_SOLID)

        search_input = sg.Input(
            size=(28, 1), 
            key="-SEARCH-", 
            font=("Georgia", 12), 
            enable_events=True, 
            text_color=Layout.LIGHT_TEXT, 
            background_color=Layout.MEDIUM_FRAME_BG)

        matches_checkbox = sg.Checkbox(
            "Exact matches only?", 
            key="-EXACT_MATCH-", 
            enable_events=True, 
            font=("Georgia", 11), 
            text_color=Layout.LIGHT_TEXT, 
            background_color=Layout.LIGHT_FRAME_BG)

        matches_output = sg.Listbox(
            values=[], 
            size=(28, 5), 
            key="-RESULTS-", 
            enable_events=True, 
            font=("Segoe UI", 12), 
            visible=False, 
            text_color=Layout.LIGHT_TEXT, 
            background_color=Layout.DARK_FRAME_BG)

        goto_button = Layout.create_button(
            "Go to", 
            key="-GOTO-", 
            font_color=Layout.LIGHT_TEXT, 
            button_color=Layout.BUTTON_BG, 
            visible=False, 
            font=("Garamond", 12, "bold"))
        clear_button = Layout.create_button(
            "Clear", 
            key="-CLEAR-", 
            font_color=Layout.LIGHT_TEXT, 
            button_color=Layout.BUTTON_BG, 
            visible=False, 
            font=("Garamond", 12, "bold"))

        matches_frame = sg.Frame("", [
            [matches_output],
            [goto_button],
            [clear_button]
        ], background_color=Layout.LIGHT_FRAME_BG, element_justification="center", border_width=0)

        search_frame = sg.Frame("", [
            [sg.Push(Layout.LIGHT_FRAME_BG), search_label, sg.Push(Layout.LIGHT_FRAME_BG)],
            [search_input],
            [matches_checkbox],
            [sg.Push(background_color=Layout.LIGHT_FRAME_BG), matches_frame, sg.Push(background_color=Layout.LIGHT_FRAME_BG)]
        ], expand_x=True, expand_y=True, 
        pad=(10, 10), 
        relief=sg.RELIEF_GROOVE, 
        background_color=Layout.LIGHT_FRAME_BG, 
        border_width=5, 
        title_color=Layout.LIGHT_TEXT)

        return sg.Column([
            [search_frame]
        ], vertical_alignment="top",
        pad=(5, 5), 
        expand_y=True, 
        justification="left", 
        background_color=Layout.MEDIUM_FRAME_BG)

    @staticmethod
    def create_geographic_province_info_frame():
        """Creates the geographical frame section for a province.

        Returns:
            frame (Frame): The frame containing the province info.
        """
        province_name = sg.Text(
            "",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="left",
            key="-INFO_PROVINCE_NAME-",
            text_color=Layout.LIGHT_TEXT)

        capital_name = sg.Text(
            "",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="left",
            key="-INFO_PROVINCE_CAPITAL-",
            text_color=Layout.LIGHT_TEXT)

        area_name = sg.Text(
            "",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="right",
            key="-INFO_PROVINCE_AREA_NAME-",
            text_color=Layout.LIGHT_TEXT)

        region_name = sg.Text(
            "",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="right",
            key="-INFO_PROVINCE_REGION_NAME-",
            text_color=Layout.LIGHT_TEXT)

        return sg.Frame("", [
            [sg.Column([
                [province_name],
                [capital_name]
            ], background_color=Layout.TOP_BANNER_BG, element_justification="left", expand_x=True),

            sg.Column([
                [area_name],
                [region_name],
            ], background_color=Layout.TOP_BANNER_BG, element_justification="right", expand_x=True)]
        ], background_color=Layout.TOP_BANNER_BG, 
        relief=sg.RELIEF_RAISED, 
        border_width=4, 
        title_color=Layout.LIGHT_TEXT, 
        pad=(5, 5), 
        expand_x=True)

    @staticmethod
    def create_development_info_frame(name: str):
        """Creates the development frame section for a province.

        Returns:
            frame (Frame): The frame containing the development info.
        """
        development_icon = sg.Image(icon_loader.get_icon("development"), size=(28, 28))
        total_dev_value = sg.Text(
            "",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),   
            key="-INFO_PROVINCE_TOTAL_DEV-",
            size=(4, 1),
            text_color=Layout.GREEN_TEXT)

        total_dev_frame = sg.Frame("", [
            [development_icon, total_dev_value]
        ], background_color=Layout.SUNK_FRAME_BG, 
        border_width=3, 
        pad=(5, 5),
        relief=sg.RELIEF_GROOVE)

        tax_icon = sg.Image(icon_loader.get_icon("base_tax"), size=(28, 28))
        tax_value = sg.Text(
            "",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),   
            key="-INFO_PROVINCE_BASE_TAX-",
            size=(3, 1),
            text_color=Layout.GREEN_TEXT)
        tax_frame = sg.Frame("", [
            [tax_icon, tax_value]
        ], background_color=Layout.SUNK_FRAME_BG, border_width=0, pad=(5, 5))

        production_icon = sg.Image(icon_loader.get_icon("base_production"), size=(28, 28))
        production_value = sg.Text(
            "",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            key="-INFO_PROVINCE_BASE_PRODUCTION-",
            size=(3, 1),
            text_color=Layout.GREEN_TEXT)
        production_frame = sg.Frame("", [
            [production_icon, production_value]
        ], background_color=Layout.SUNK_FRAME_BG, border_width=0, pad=(5, 5))

        manpower_icon = sg.Image(icon_loader.get_icon("base_manpower"), size=(28, 28))
        manpower_value = sg.Text(
            "",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            key="-INFO_PROVINCE_BASE_MANPOWER-",
            size=(3, 1),
            text_color=Layout.GREEN_TEXT)
        manpower_frame = sg.Frame("", [
            [manpower_icon, manpower_value]
        ], background_color=Layout.SUNK_FRAME_BG, border_width=0, pad=(5, 5))

        return sg.Frame("", [
            [total_dev_frame, tax_frame, production_frame, manpower_frame]
        ], background_color=Layout.DARK_FRAME_BG, 
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN, 
        border_width=3, 
        title_color=Layout.LIGHT_TEXT)

    @staticmethod
    def create_demographic_info_column():
        """Creates the demographics column section for a province.

        Returns:
            column (Column): The column containing the demographic info.
        """
        cored_by_info = Layout.create_text_with_frame(
            "",
            content_color=Layout.GREEN_TEXT,
            expand_x=True,
            font=("Georgia", 12),
            frame_background_color=Layout.SUNK_FRAME_BG,
            justification="left",
            key="-INFO_PROVINCE_OWNER-",
            relief=sg.RELIEF_FLAT,
            size=(20, 1))

        culture_info = Layout.create_text_with_frame(
            "",
            content_color=Layout.GREEN_TEXT,
            expand_x=True,
            font=("Georgia", 12),
            frame_background_color=Layout.SUNK_FRAME_BG,
            justification="left",
            key="-INFO_PROVINCE_CULTURE-",
            relief=sg.RELIEF_FLAT,
            size=(20, 1))

        religion_info = Layout.create_text_with_frame(
            "",
            content_color=Layout.GREEN_TEXT,
            expand_x=True,
            font=("Georgia", 12),
            frame_background_color=Layout.SUNK_FRAME_BG,
            justification="left",
            key="-INFO_PROVINCE_RELIGION-",
            relief=sg.RELIEF_FLAT,
            size=(20, 1))

        demographics_frame = sg.Frame("", [
            [sg.Text("Cored by:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.MEDIUM_FRAME_BG)],
            [cored_by_info],

            [sg.Text("Culture:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.MEDIUM_FRAME_BG)],
            [culture_info],

            [sg.Text("Religion:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.MEDIUM_FRAME_BG)],
            [religion_info]
        ], background_color=Layout.DARK_FRAME_BG, 
        expand_y=True,
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        demographics_header_label = sg.Text(
            "Demographics", 
            background_color=Layout.SECTION_BANNER_BG,
            font=("Georgia", 12, "bold"),
            text_color=Layout.LIGHT_TEXT)
        demographics_icon = sg.Image(icon_loader.get_icon("demographics"), size=(28, 28))
        demographics_header_frame = sg.Frame("", [
            [demographics_header_label, demographics_icon, sg.Push(background_color=Layout.SECTION_BANNER_BG)]
        ], background_color=Layout.SECTION_BANNER_BG, expand_x=True, expand_y=True, relief=sg.RELIEF_SOLID, vertical_alignment="top")

        return sg.Column([
            [demographics_header_frame],
            [demographics_frame]
        ], pad=(10, 10), 
        background_color=Layout.LIGHT_FRAME_BG, 
        expand_y=True, 
        vertical_alignment="top")

    @staticmethod
    def create_trade_info_column():
        """Creates the trade column section for a province.

        Returns:
            column (Column): The column containing the trade info.
        """
        trade_value_icon = sg.Image(icon_loader.get_icon("trade_value_income"), size=(28, 28))
        trade_value_label, trade_value = Layout.create_text_with_inline_label(
            "Trade Value",
            label_colors=(Layout.LIGHT_TEXT, Layout.DARK_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(6, 1),
            text_key="-INFO_PROVINCE_TRADE_VALUE-",
            expand_x=True)

        trade_power_icon = sg.Image(icon_loader.get_icon("trade_power"), size=(28, 28))
        trade_power_label, trade_power_field = Layout.create_text_with_inline_label(
            "Trade Power",
            label_colors=(Layout.LIGHT_TEXT, Layout.DARK_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(6, 1),
            text_key="-INFO_PROVINCE_TRADE_POWER-",
            expand_x=True)

        goods_produced_icon = sg.Image(icon_loader.get_icon("goods_produced"), size=(28, 28))
        goods_produced_label, goods_produced_field = Layout.create_text_with_inline_label(
            "Goods Produced",
            label_colors=(Layout.LIGHT_TEXT, Layout.DARK_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(6, 1),
            text_key="-INFO_PROVINCE_GOODS_PRODUCED-",
            expand_x=True)

        trade_info_frame = sg.Frame("", [
            [trade_value_label, trade_value_icon, trade_value],
            [trade_power_label, trade_power_icon, trade_power_field],
            [goods_produced_label, goods_produced_icon, goods_produced_field],
        ], background_color=Layout.DARK_FRAME_BG, 
        expand_x=True,
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN)

        trade_header_label = sg.Text(
            "Trade", 
            background_color=Layout.SECTION_BANNER_BG,
            font=("Georgia", 12, "bold"),
            text_color=Layout.LIGHT_TEXT)
        trade_icon = sg.Image(icon_loader.get_icon("trade"), size=(28, 28))
        trade_header_frame = sg.Frame("", [
            [trade_header_label, trade_icon, sg.Push(background_color=Layout.SECTION_BANNER_BG)]
        ], background_color=Layout.SECTION_BANNER_BG, 
        expand_x=True, 
        expand_y=True, 
        relief=sg.RELIEF_SOLID, 
        vertical_alignment="top")

        home_trade_node = Layout.create_text_with_frame(
            "",
            content_color=Layout.LIGHT_TEXT,
            frame_background_color=Layout.DARK_FRAME_BG,
            justification="center",
            key="-INFO_PROVINCE_HOME_NODE-",
            size=(12, 1),
            relief=sg.RELIEF_SOLID)

        estuary_icon = sg.Image("", key="-INFO_PROVINCE_HAS_ESTUARY-", size=(28, 28))
        goods_produced_modifier_icon = sg.Image("", key="-INFO_PROVINCE_GOODS_PRODUCED_MODIFIER-", size=(28, 28))
        inland_trade_icon = sg.Image("", key="-INFO_PROVINCE_INLANDE_TRADE_CENTER-", size=(28, 28))
        center_of_trade = sg.Image("", key="-INFO_PROVINCE_CENTER_OF_TRADE-", size=(84, 40))

        goods_and_trade_modifiers = sg.Frame("", [
            [estuary_icon, inland_trade_icon, goods_produced_modifier_icon, center_of_trade]  
        ], background_color=Layout.SUNK_FRAME_BG, 
        element_justification="center", 
        expand_x=True,
        relief=sg.RELIEF_SUNKEN)

        home_node_icon = sg.Image(icon_loader.get_icon("trade_office"), size=(40, 40))
        trade_influences_column = sg.Column([
            [home_node_icon, home_trade_node],
            [goods_and_trade_modifiers]
        ], background_color=Layout.MEDIUM_FRAME_BG, pad=(5, 5))

        trade_good = sg.Image("", key="-INFO_PROVINCE_TRADE_GOOD-", size=(64, 64))
        return sg.Column([
            [trade_header_frame],
            [trade_info_frame, trade_influences_column, trade_good],
        ], background_color=Layout.LIGHT_FRAME_BG, expand_x=True, expand_y=True, pad=(10, 0), vertical_alignment="top")

    @staticmethod
    def create_military_info_column():
        """Creates the military column section for a province.

        Returns:
            column (Column): The column containing the military info.
        """
        manpower_label, manpower_value = Layout.create_text_with_inline_label(
            "Manpower",
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(5, 1),
            text_key="-INFO_PROVINCE_LOCAL_MANPOWER-",
            expand_x=True)

        sailors_label, sailors_value = Layout.create_text_with_inline_label(
            "Sailors",
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(5, 1),
            text_key="-INFO_PROVINCE_LOCAL_SAILORS-",
            expand_x=True)

        troops_info_column = sg.Column([
            [manpower_label, manpower_value, sailors_label, sailors_value],
        ], background_color=Layout.MEDIUM_FRAME_BG)

        garrison_icon = sg.Image(icon_loader.get_icon("fort_defense"), size=(28, 28))
        garrison_label, garrison_value = Layout.create_text_with_inline_label(
            "Garrison",
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(5, 1),
            text_key="-INFO_PROVINCE_GARRISON_SIZE-")

        defense_info_column = sg.Column([
            [garrison_label, garrison_icon, garrison_value],
        ], background_color=Layout.MEDIUM_FRAME_BG)

        military_info_frame = sg.Frame("", [
            [troops_info_column, defense_info_column]
        ], background_color=Layout.MEDIUM_FRAME_BG, 
        element_justification="center",
        relief=sg.RELIEF_SUNKEN)

        military_label = sg.Text(
            "Military", 
            background_color=Layout.SECTION_BANNER_BG,
            font=("Georgia", 12, "bold"),
            text_color=Layout.LIGHT_TEXT)
        military_icon = sg.Image(icon_loader.get_icon("military"), size=(28, 28))
        military_header_frame = sg.Frame("", [
            [military_label, military_icon, sg.Push(background_color=Layout.SECTION_BANNER_BG)]
        ], background_color=Layout.SECTION_BANNER_BG, expand_x=True, relief=sg.RELIEF_SOLID)

        fort_level = sg.Image("", key="-INFO_PROVINCE_FORT_LEVEL-", size=(48, 48))
        return sg.Column([
            [military_header_frame],
            [military_info_frame, fort_level]
        ], background_color=Layout.LIGHT_FRAME_BG, pad=(10, 10), vertical_alignment="top")

    @staticmethod
    def create_province_info_column():
        """Creates the province column section.
        
        This section contains the province geographic, development, and demographic information.
        
        Returns:
            column (Column): The column containing the province info.
        """
        autonomy_icon = sg.Image(icon_loader.get_icon("local_autonomy"), size=(28, 28))

        autonomy_value = sg.Text(
            "",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            justification="center",
            key="-INFO_PROVINCE_LOCAL_AUTONOMY-",
            size=(5, 1),
            text_color=Layout.GREEN_TEXT)

        autonomy_frame = sg.Frame("", [
            [autonomy_icon, autonomy_value]
        ], background_color=Layout.MEDIUM_FRAME_BG, border_width=0)

        devastation_icon = sg.Image(icon_loader.get_icon("local_devastation"), size=(28, 28))
        devastation_value = sg.Text(
            "",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            justification="center",
            key="-INFO_PROVINCE_LOCAL_DEVASTATION-",
            size=(5, 1),
            text_color=Layout.GREEN_TEXT)

        devastation_frame = sg.Frame("", [
            [devastation_icon, devastation_value]
        ], background_color=Layout.MEDIUM_FRAME_BG, border_width=0)

        province_status_frame = sg.Frame("", [
            [autonomy_frame, devastation_frame]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        border_width=4,
        expand_x=True, 
        relief=sg.RELIEF_SUNKEN)

        province_status_column = sg.Column([
            [province_status_frame],
        ], background_color=Layout.LIGHT_FRAME_BG, expand_x=True)

        development_info_frame = Layout.create_development_info_frame(name="PROVINCE")
        demographic_info_column = Layout.create_demographic_info_column()

        trade_and_mil_column = sg.Column([
            [Layout.create_trade_info_column()],
            [Layout.create_military_info_column()]
        ], background_color=Layout.LIGHT_FRAME_BG, expand_x=True, pad=(5, 5))

        development_label = Layout.create_text_with_frame(
            content="Development",
            content_color=Layout.LIGHT_TEXT,
            frame_background_color=Layout.SECTION_BANNER_BG,
            relief=sg.RELIEF_SOLID,
            expand_x=True,
            justification="center")

        geographic_info_frame = Layout.create_geographic_province_info_frame()
        province_info_frame = sg.Frame("", [
            [geographic_info_frame],
            [province_status_column, development_label, development_info_frame],
            [demographic_info_column, trade_and_mil_column]
        ], background_color=Layout.LIGHT_FRAME_BG, 
        border_width=5, 
        expand_y=True,
        pad=(10, 10),   
        relief=sg.RELIEF_GROOVE, 
        title_color=Layout.LIGHT_TEXT)

        return sg.Column([
            [province_info_frame]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        expand_y=True,
        key="-PROVINCE_INFO-",
        pad=(5, 5),
        vertical_alignment="top")

    @staticmethod
    def create_geographic_area_info_frame():
        """Creates the geographical frame section for an area.

        Returns:
            frame (Frame): The frame containing the area info.
        """
        area_label, area_field = Layout.create_text_with_inline_label(
            label_name="Area:",
            label_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_field_size=(15, 1),
            text_key="-INFO_AREA_NAME-",
            font=("Georgia", 14, "bold"))

        region_label, region_field = Layout.create_text_with_inline_label(
            label_name="Region:",
            label_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_field_size=(15, 1),
            text_key="-INFO_AREA_REGION-",
            font=("Georgia", 14, "bold"),
            justification="right")

        area_info_column = sg.Column([
                [area_label, area_field]
            ], background_color=Layout.TOP_BANNER_BG, element_justification="left", expand_x=True)

        region_info_column =  sg.Column([
                [region_label, region_field],
            ], background_color=Layout.TOP_BANNER_BG, element_justification="right", expand_x=True)

        return sg.Frame("", [
            [area_info_column, region_info_column]
        ], background_color=Layout.TOP_BANNER_BG, 
        relief=sg.RELIEF_RAISED, 
        border_width=4, 
        title_color=Layout.LIGHT_TEXT, 
        pad=(5, 5), 
        expand_x=True)

    @staticmethod
    def create_area_info_column():
        area_provinces_output = sg.Listbox(
            values=[], 
            background_color=Layout.DARK_FRAME_BG, 
            enable_events=True, 
            font=("Garamond", 12,"bold"), 
            key="-INFO_AREA_PROVINCES-", 
            size=(30, 8),
            text_color=Layout.LIGHT_TEXT)

        return sg.Column([
            [sg.Frame("", [
                [Layout.create_geographic_area_info_frame()],
                [Layout.create_text_with_frame(
                    content="Development",
                    content_color=Layout.LIGHT_TEXT,
                    frame_background_color=Layout.SECTION_BANNER_BG)],
                [Layout.create_development_info_frame(name="AREA")],
                [Layout.create_text_with_frame(
                    content="Provinces",
                    content_color=Layout.LIGHT_TEXT,
                    frame_background_color=Layout.SECTION_BANNER_BG)],
                [area_provinces_output]

            ], pad=(10, 10), 
            relief=sg.RELIEF_GROOVE, 
            background_color=Layout.LIGHT_FRAME_BG, 
            expand_y=True, 
            border_width=5, 
            title_color=Layout.LIGHT_TEXT)]
        ], key="-AREA_INFO-", 
        vertical_alignment="top", 
        pad=(10, 10), 
        expand_y=True, 
        background_color=Layout.MEDIUM_FRAME_BG, 
        visible=False)

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
        canvas_frame =  sg.Frame("", [
            [sg.Canvas(background_color="black", size=canvas_size, key=key, pad=(0, 0))]
        ], background_color=Layout.LIGHT_FRAME_BG, relief=sg.RELIEF_GROOVE, pad=(5, 5), border_width=5)

        return Layout.add_border(
            layout=[[canvas_frame]], 
            inner_border=(Layout.GOLD_FRAME_LOWER, 2),
            outer_border=(Layout.GOLD_FRAME_UPPER, 2),
            pad=(5, 5))

    @staticmethod
    def create_map_modes_frame(map_modes: dict):
        """Creates the map modes frame for selecting map modes.
        
        Args:
            map_modes (dict[MapMode]): The possible map modes to choose from when displaying the map.
        
        Returns:
            frame (Frame): The frame containing the map mode buttons.
        """

        map_mode_label = Layout.create_text_with_frame(
            "Map Modes",
            content_color=Layout.LIGHT_TEXT,
            font=("Georgia", 10, "bold"),
            frame_background_color=Layout.RED_BANNER_BG,
            justification="center",
            relief=sg.RELIEF_SOLID,
            size=(20, 1))

        reset_button = Layout.create_button(
            "RESET ZOOM", 
            button_color=Layout.BUTTON_BG,
            font=("Georgia", 10),
            font_color=Layout.LIGHT_TEXT,
            key="-RESET-")

        return sg.Frame("", [
            [map_mode_label],
            [Layout.create_button(
                mode.name,
                button_color=Layout.BUTTON_BG,
                font=("Georgia", 10),
                font_color=Layout.LIGHT_TEXT,
                key=mode.value)
                for mode in map_modes],
            [sg.Push(background_color=Layout.SUNK_FRAME_BG), reset_button, sg.Push(background_color=Layout.SUNK_FRAME_BG)]
        ], element_justification="center", 
        relief=sg.RELIEF_GROOVE, 
        pad=(10, 10), 
        background_color=Layout.SUNK_FRAME_BG, 
        border_width=5)

    @staticmethod
    def build_layout(canvas_size: tuple[int, int], map_modes: dict):
        """Driver method that builds the layout to be used within a PySimpleGUI|FreeSimpleGUI `Window` element.
        
        Args:
            canvas_size (tuple[int, int]): The `(x, y)` size of the canvas determined by the display size.
            map_modes (dict[MapMode]): The possible map modes to choose from when displaying the map.
        """
        print("Building layout....")
        selected_info_frame = sg.Frame("", [
                [Layout.create_search_column(), Layout.create_province_info_column(), Layout.create_area_info_column()]
            ], pad=(5, 5), 
            relief=sg.RELIEF_GROOVE, 
            background_color=Layout.LIGHT_FRAME_BG, 
            size=(600, 500), 
            border_width=5, 
            expand_x=True, 
            expand_y=True)

        bordered_info = Layout.add_border(
            layout=[[selected_info_frame]],
            inner_border=(Layout.GOLD_FRAME_LOWER, 2),
            outer_border=(Layout.GOLD_FRAME_UPPER, 2),
            pad=(5, 5),
            expand_x=True,
            expand_y=True)

        return [
            [Layout.create_window_header()],
            [bordered_info],
            [Layout.create_map_canvas_frame(canvas_size=canvas_size, key="-CANVAS-")],
            [Layout.create_map_modes_frame(map_modes=map_modes)],
        ]
