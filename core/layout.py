import FreeSimpleGUI as sg
import os

from .utils import IconLoader


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
icons_folder = os.path.join(base_dir, "data", "icons")

icon_loader = IconLoader()
icon_loader.icons_folder = icons_folder



class Layout:
    CANVAS_WIDTH_MAX = 1200
    """Maximum width for the canvas."""
    LIGHT_TEXT = "#d2d2d2"
    """Color for light text."""
    GOLD_FRAME_UPPER = "#b68950"
    """Upper border color for gold frame."""
    GOLD_FRAME_LOWER = "#9f7240"
    """Lower border color for gold frame."""
    RED_BANNER_BG = "#561b19"
    """Background color for red banners."""
    TOP_BANNER_BG = "#353c25"
    """Background color for top banners."""
    SECTION_BANNER_BG = "#172f48"
    """Background color for section banners."""
    LIGHT_FRAME_BG = "#344048"
    """Background color for light frames."""
    MEDIUM_FRAME_BG = "#2a343b"
    """Background color for medium frames."""
    DARK_FRAME_BG = "#283239"
    """Background color for dark frames."""
    SUNK_FRAME_BG = "#252e34"
    """Background color for sunken frames."""
    BUTTON_BG = "#314b68"
    """Background color for buttons."""
    GREEN_TEXT = "#2b8334"
    """Color for green text."""

    @staticmethod
    def add_border(
        layout: list[list], 
        borders: list[tuple[str, int, str]], 
        pad: tuple[int, int]=None, 
        expand_x: bool=False, 
        expand_y: bool=False) -> sg.Frame:
        """
        Creates a border around the given layout.
        
        Args:
            layout (list[list]): The layout to wrap.
            borders (list[tuple[str, int, str]]): Tuples that specify the (color, width, relief type) for each border.
            pad (tuple[int, int]): Amount of padding to put around the outermost border in pixels (left/right, top/bottom).
            expand_x (bool): If True the element will automatically expand in the X direction to fill available space.
            expand_y (bool): If True the element will automatically expand in the Y direction to fill available space
        
        Returns:h n
            outer_frame (Frame): The created frame with the border.
        """
        for i, (color, width, relief_type) in enumerate(reversed(borders)):
            layout = [[sg.Frame("", 
                layout=layout, 
                border_width=width, 
                background_color=color,
                expand_x=expand_x, 
                expand_y=expand_y,
                pad=(pad if i == len(borders) - 1 else (None, None)), 
                relief=relief_type)]]

        return layout[0][0]

    @staticmethod
    def create_icon_with_border(
        icon_name: str,
        borders: tuple[str, int, str],
        border_pad: tuple[int, int],
        image_size: tuple[int, int],
        image_key: str=None):
        """
        Creates an icon with a framed border.

        This method loads an image given a name, and returns the bordered image. 

        Args:
            icon_name (str): The name of the icon to be loaded.
            borders (tuple[str, int, str]): Tuples that specify the (color, width, relief type) for each border.
            border_pad (tuple[int, int]): Amount of padding to put around the outermost border in pixels (left/right, top/bottom).
            image_size (tuple[int, int]): The `(x, y)` size of the image in pixels.
            image_key (str|None): The string that will be used to access/edit the image.
                Should follow the format `-NAME-` for clarity.

        Returns:
            framed_image (Frame): A frame containing the bordered image.
        """
        image = sg.Image(
            filename=icon_loader.get_icon(icon_name), 
            key=image_key, 
            pad=(0, 0), 
            size=image_size)
        return Layout.add_border(layout=[[image]], borders=borders, pad=border_pad)

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
        expand_x=False,
        pad: tuple[int, int]=None):
        """
        Creates text with a framed border.
        
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
        pad=pad if pad else (5, 5), 
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
    def create_options_frame():
        load_save_button = sg.Button(
            "LOAD SAVEFILE", 
            key="-LOAD_SAVEFILE-",
            button_color=(Layout.GOLD_FRAME_UPPER, Layout.BUTTON_BG), 
            font=("Garamond", 12, "bold"))

        button_frame = sg.Frame("", [
            [load_save_button]
        ], background_color=Layout.SUNK_FRAME_BG,
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
            "Map Information", 
            background_color=Layout.RED_BANNER_BG,
            border_width=2,
            font=("Georgia", 14), 
            justification="center", 
            pad=(5, 5),
            relief=sg.RELIEF_RIDGE,
            size=(15, 1), 
            text_color=Layout.LIGHT_TEXT)

        info_text = sg.Multiline(
            default_text="Hover over an area to get more information!", 
            key="-MULTILINE-",
            background_color=Layout.SUNK_FRAME_BG,
            border_width=3,
            disabled=True,
            font=("Georgia", 14),
            justification="center",
            no_scrollbar=True,
            pad=(5, 5),
            size=(Layout.CANVAS_WIDTH_MAX // 20, 1),
            text_color=Layout.LIGHT_TEXT,
            write_only=True)

        load_savefile_button = sg.Button(
            "LOAD SAVEFILE",
            key="-LOAD_SAVEFILE-",
            border_width=2,
            font=("Georgia", 12),
            button_color=(Layout.LIGHT_TEXT, Layout.BUTTON_BG),
            pad=(5, 5),
            size=(15, 1))

        exit_button = sg.Button(
            "EXIT",
            key="-EXIT-",
            border_width=2,
            font=("Georgia", 12),
            button_color=(Layout.LIGHT_TEXT, Layout.BUTTON_BG),
            pad=(5, 5),
            size=(15, 1))

        header_row = [
            header_text, 
            sg.Push(background_color=Layout.LIGHT_FRAME_BG), 
            info_text, 
            sg.Push(background_color=Layout.LIGHT_FRAME_BG), 
            load_savefile_button, exit_button
        ]

        header_column = sg.Column(
            [header_row], 
            background_color=Layout.LIGHT_FRAME_BG,
            element_justification="center", 
            expand_x=True,
            justification="center", 
            pad=(0, 0))

        return Layout.add_border(
            layout=[[header_column]],
            borders=[
                (Layout.GOLD_FRAME_LOWER, 3, sg.RELIEF_RIDGE),
                (Layout.GOLD_FRAME_UPPER, 3, sg.RELIEF_RIDGE)],
            pad=(2, 2),
            expand_x=True)  

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
            expand_x=True,
            frame_background_color=Layout.RED_BANNER_BG,
            justification="center",
            relief=sg.RELIEF_RIDGE)

        search_input = sg.Input(
            key="-SEARCH-", 
            background_color=Layout.MEDIUM_FRAME_BG,
            enable_events=True, 
            font=("Georgia", 12),
            pad=(10, 10), 
            size=(26, 1), 
            text_color=Layout.LIGHT_TEXT)

        matches_checkbox = sg.Checkbox(
            "Exact matches only?", 
            key="-EXACT_MATCH-", 
            background_color=Layout.LIGHT_FRAME_BG,
            enable_events=True, 
            font=("Georgia", 11), 
            text_color=Layout.LIGHT_TEXT)

        input_frame= sg.Frame("", [
            [search_label],
            [search_input],
            [matches_checkbox]
        ], background_color=Layout.LIGHT_FRAME_BG,
        border_width=0,
        element_justification="center",
        pad=(10, 10))

        matches_output = sg.Listbox(
            values=[], 
            key="-RESULTS-", 
            background_color=Layout.DARK_FRAME_BG,
            enable_events=True, 
            font=("Georgia", 12), 
            pad=(0, 10),
            size=(26, 5),
            sbar_arrow_color=Layout.GOLD_FRAME_UPPER,
            sbar_background_color=Layout.RED_BANNER_BG,
            sbar_trough_color=Layout.GOLD_FRAME_LOWER,
            sbar_relief=sg.RELIEF_GROOVE,
            sbar_width=5,
            text_color=Layout.LIGHT_TEXT,
            visible=False)

        goto_button = sg.Button(
            "Go to",
            key="-GOTO-",
            button_color=(Layout.LIGHT_TEXT, Layout.BUTTON_BG),
            font=("Garamond", 12, "bold"),
            pad=(15, 10),
            visible=False)

        clear_button = sg.Button(
            "Clear",
            key="-CLEAR-",
            button_color=(Layout.LIGHT_TEXT, Layout.BUTTON_BG),
            font=("Garamond", 12, "bold"),
            pad=(15, 10),
            visible=False)

        output_frame = sg.Frame("", [
            [matches_output],
            [goto_button],
            [clear_button]
        ], background_color=Layout.LIGHT_FRAME_BG, 
        border_width=0,
        element_justification="center",
        pad=(10, 10))

        search_frame = sg.Frame("", [
            [sg.Push(Layout.LIGHT_FRAME_BG), input_frame, sg.Push(Layout.LIGHT_FRAME_BG)],
            [sg.Push(Layout.LIGHT_FRAME_BG), output_frame, sg.Push(Layout.LIGHT_FRAME_BG)]
        ], background_color=Layout.LIGHT_FRAME_BG,
        border_width=5,
        expand_x=True,
        expand_y=True, 
        pad=(10, 10), 
        relief=sg.RELIEF_GROOVE,  
        title_color=Layout.LIGHT_TEXT)

        return sg.Column([
            [search_frame]
        ], background_color=Layout.LIGHT_FRAME_BG,
        expand_x=True,
        expand_y=True, 
        element_justification="left",
        justification="left",
        pad=((10, 5), (10, 10)), 
        vertical_alignment="top")

    @staticmethod
    def create_geographic_province_info_frame():
        """Creates the geographical frame section for a province.

        Returns:
            frame (Frame): The frame containing the province info.
        """
        province_name = sg.Text(
            "",
            key="-INFO_PROVINCE_NAME-",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="left",
            text_color=Layout.LIGHT_TEXT)

        capital_name = sg.Text(
            "",
            key="-INFO_PROVINCE_CAPITAL-",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="left",
            text_color=Layout.LIGHT_TEXT)

        area_name = sg.Text(
            "",
            key="-INFO_PROVINCE_AREA_NAME-",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="right",
            text_color=Layout.LIGHT_TEXT)

        region_name = sg.Text(
            "",
            key="-INFO_PROVINCE_REGION_NAME-",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="right",
            text_color=Layout.LIGHT_TEXT)

        return sg.Frame("", [
            [sg.Column([
                [province_name],
                [capital_name]
            ], background_color=Layout.TOP_BANNER_BG,
            element_justification="left", 
            expand_x=True),

            sg.Column([
                [area_name],
                [region_name],
            ], background_color=Layout.TOP_BANNER_BG, 
            element_justification="right", 
            expand_x=True)]
        ], background_color=Layout.TOP_BANNER_BG, 
        border_width=4, 
        expand_x=True,
        pad=(5, 5),
        relief=sg.RELIEF_RAISED, 
        vertical_alignment="center")

    @staticmethod
    def create_development_info_frame(name: str):
        """Creates the development frame section for a province.

        Returns:
            frame (Frame): The frame containing the development info.
        """
        development_icon= Layout.create_icon_with_border(
            icon_name="development",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        total_dev_value = sg.Text(
            "",
            key=f"-INFO_{name}_TOTAL_DEV-",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),   
            size=(5, 1),
            text_color=Layout.GREEN_TEXT)

        total_dev_frame = sg.Frame("", [
            [development_icon, total_dev_value]
        ], background_color=Layout.SUNK_FRAME_BG, 
        border_width=3, 
        pad=(10, 0),
        relief=sg.RELIEF_FLAT)

        tax_icon = Layout.create_icon_with_border(
            icon_name="base_tax",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        tax_value = sg.Text(
            "",
            key=f"-INFO_{name}_BASE_TAX-",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),   
            size=(4, 1),
            text_color=Layout.GREEN_TEXT)
        tax_frame = sg.Frame("", [
            [tax_icon, tax_value]
        ], background_color=Layout.SUNK_FRAME_BG, 
        border_width=2, 
        pad=(5, 0),
        relief=sg.RELIEF_FLAT)

        production_icon = Layout.create_icon_with_border(
            icon_name="base_production",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        production_value = sg.Text(
            "",
            key=f"-INFO_{name}_BASE_PRODUCTION-",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            size=(4, 1),
            text_color=Layout.GREEN_TEXT)
        production_frame = sg.Frame("", [
            [production_icon, production_value]
        ], background_color=Layout.SUNK_FRAME_BG, 
        border_width=2,
        pad=(5, 0),
        relief=sg.RELIEF_FLAT)

        manpower_icon = Layout.create_icon_with_border(
            icon_name="base_manpower",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        manpower_value = sg.Text(
            "",
            key=f"-INFO_{name}_BASE_MANPOWER-",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            size=(4, 1),
            text_color=Layout.GREEN_TEXT)
        manpower_frame = sg.Frame("", [
            [manpower_icon, manpower_value]
        ], background_color=Layout.SUNK_FRAME_BG, 
        border_width=2, 
        pad=(5, 0),
        relief=sg.RELIEF_FLAT)

        return sg.Frame("", [
            [total_dev_frame, tax_frame, production_frame, manpower_frame]
        ], background_color=Layout.DARK_FRAME_BG, 
        border_width=3, 
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN, 
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
            [sg.Text(
                "Cored By",
                background_color=Layout.MEDIUM_FRAME_BG,
                font=("Georgia", 12), 
                text_color=Layout.LIGHT_TEXT)],
            [cored_by_info],

            [sg.Text(
                "Culture", 
                background_color=Layout.MEDIUM_FRAME_BG,
                font=("Georgia", 12), 
                text_color=Layout.LIGHT_TEXT)],
            [culture_info],

            [sg.Text(
                "Religion", 
                background_color=Layout.MEDIUM_FRAME_BG,
                font=("Georgia", 12), 
                text_color=Layout.LIGHT_TEXT)],
            [religion_info]
        ], background_color=Layout.DARK_FRAME_BG, 
        expand_y=True,
        pad=(0, 0), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        demographics_header_label = sg.Text(
            "Demographics", 
            background_color=Layout.SECTION_BANNER_BG,
            font=("Georgia", 12, "bold"),
            text_color=Layout.LIGHT_TEXT)
        demographics_icon = Layout.create_icon_with_border(
            icon_name="demographics",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        demographics_header_frame = sg.Frame("", [
            [demographics_header_label, demographics_icon, sg.Push(background_color=Layout.SECTION_BANNER_BG)]
        ], background_color=Layout.SECTION_BANNER_BG, 
        expand_x=True, 
        pad=((0, 0), (0, 15)),
        relief=sg.RELIEF_SOLID, 
        vertical_alignment="top")

        return sg.Column([
            [demographics_header_frame],
            [demographics_frame]
        ], background_color=Layout.LIGHT_FRAME_BG, 
        expand_y=True, 
        pad=(0, 10), 
        vertical_alignment="top")

    @staticmethod
    def create_trade_info_column():
        """Creates the trade column section for a province.

        Returns:
            column (Column): The column containing the trade info.
        """
        trade_value_icon = Layout.create_icon_with_border(
            icon_name="trade_value_income",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_value_label, trade_value = Layout.create_text_with_inline_label(
            "Trade Value",
            text_key="-INFO_PROVINCE_TRADE_VALUE-",
            label_colors=(Layout.LIGHT_TEXT, Layout.DARK_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(6, 1),
            expand_x=True)

        trade_power_icon = Layout.create_icon_with_border(
            icon_name="trade_power",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_power_label, trade_power_field = Layout.create_text_with_inline_label(
            "Trade Power",
            text_key="-INFO_PROVINCE_TRADE_POWER-", 
            label_colors=(Layout.LIGHT_TEXT, Layout.DARK_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(6, 1),
            expand_x=True)

        goods_produced_icon = Layout.create_icon_with_border(
            icon_name="goods_produced",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        goods_produced_label, goods_produced_field = Layout.create_text_with_inline_label(
            "Goods Produced",
            text_key="-INFO_PROVINCE_GOODS_PRODUCED-",
            label_colors=(Layout.LIGHT_TEXT, Layout.DARK_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(6, 1),
            expand_x=True)

        trade_info_frame = sg.Frame("", [
            [trade_value_label, trade_value_icon, trade_value],
            [trade_power_label, trade_power_icon, trade_power_field],
            [goods_produced_label, goods_produced_icon, goods_produced_field],
        ], background_color=Layout.DARK_FRAME_BG,
        border_width=3,
        expand_x=True,  
        pad=(10, 5), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        trade_info_column = sg.Column([
            [trade_info_frame]
        ], background_color=Layout.LIGHT_FRAME_BG, pad=(5, 5), vertical_alignment="center")

        trade_header_label = sg.Text(
            "Trade", 
            background_color=Layout.SECTION_BANNER_BG,
            font=("Georgia", 12, "bold"),
            text_color=Layout.LIGHT_TEXT)
        trade_icon = Layout.create_icon_with_border(
            icon_name="trade",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_header_frame = sg.Frame("", [
            [trade_header_label, trade_icon, sg.Push(background_color=Layout.SECTION_BANNER_BG)]
        ], background_color=Layout.SECTION_BANNER_BG, 
        expand_x=True,
        relief=sg.RELIEF_SOLID)

        home_trade_node = Layout.create_text_with_frame(
            "",
            key="-INFO_PROVINCE_HOME_NODE-",
            content_color=Layout.LIGHT_TEXT,
            frame_background_color=Layout.BUTTON_BG,
            justification="center",
            pad=(10, 10),
            size=(15, 1),
            relief=sg.RELIEF_FLAT)

        estuary_icon = Layout.create_icon_with_border(
            icon_name="",
            image_key="-INFO_PROVINCE_HOME_NODE-",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(10, 5),
            image_size=(28, 28))

        goods_modifier_icon = Layout.create_icon_with_border(
            icon_name="",
            image_key="-INFO_PROVINCE_GOODS_PRODUCED_MODIFIER-",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))

        inland_trade_icon = Layout.create_icon_with_border(
            icon_name="",
            image_key="-INFO_PROVINCE_INLAND_TRADE_CENTER-",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))

        center_of_trade_icon = Layout.create_icon_with_border(
            icon_name="",
            image_key="-INFO_PROVINCE_CENTER_OF_TRADE-",
            borders=[
                (Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE),
                (Layout.GOLD_FRAME_UPPER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(84, 40))

        goods_and_trade_modifiers = sg.Frame("", [
            [estuary_icon, inland_trade_icon, goods_modifier_icon, center_of_trade_icon]  
        ], background_color=Layout.SUNK_FRAME_BG, 
        border_width=0,
        element_justification="center", 
        expand_x=True,
        pad=(5, 5))

        home_trade_icon = Layout.create_icon_with_border(
            icon_name="trade_office",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(10, 10),
            image_size=(40, 40))

        trade_influences_frame = sg.Frame("", [
            [home_trade_icon, home_trade_node],
            [goods_and_trade_modifiers]
        ], background_color=Layout.DARK_FRAME_BG,
        pad=(5, 5),
        relief=sg.RELIEF_SUNKEN)

        trade_influences_column = sg.Column([
            [trade_influences_frame]
        ], background_color=Layout.LIGHT_FRAME_BG, pad=(5, 5), vertical_alignment="center")

        trade_good_icon = Layout.create_icon_with_border(
            icon_name="",
            image_key="-INFO_PROVINCE_TRADE_GOOD-",
            borders=[
                (Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE),
                (Layout.GOLD_FRAME_UPPER, 1, sg.RELIEF_RIDGE)],
            border_pad=(0, 5),
            image_size=(64, 64))
        trade_good_value = sg.Text(
            "",
            key="-INFO_PROVINCE_TRADE_GOOD_PRICE-",
            background_color=Layout.DARK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            justification="center",
            pad=(0, 0),
            size=(4, 1),
            text_color=Layout.LIGHT_TEXT)

        ducat_income_icon = Layout.create_icon_with_border(
            "income",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(0, 0),
            image_size=(24, 24))

        value_frame = sg.Frame("", [
            [trade_good_value, ducat_income_icon]
        ], background_color=Layout.DARK_FRAME_BG, 
        relief=sg.RELIEF_FLAT,
        vertical_alignment="center")

        trade_good_frame = sg.Frame("", [
            [sg.Push(Layout.DARK_FRAME_BG), trade_good_icon, sg.Push(Layout.DARK_FRAME_BG)],
            [sg.Push(Layout.DARK_FRAME_BG), value_frame, sg.Push(Layout.DARK_FRAME_BG)]
        ], background_color=Layout.DARK_FRAME_BG,
        pad=(5, 5),
        relief=sg.RELIEF_FLAT)

        trade_good_column = sg.Column([
            [trade_good_frame]
        ], background_color=Layout.LIGHT_FRAME_BG, pad=(0, 0), vertical_alignment="center")

        return sg.Column([
            [trade_header_frame],
            [trade_info_column, trade_influences_column, trade_good_column],
        ], background_color=Layout.LIGHT_FRAME_BG, 
        expand_x=True, 
        expand_y=True, 
        pad=(0, 0),
        vertical_alignment="center")

    @staticmethod
    def create_military_info_column():
        """Creates the military column section for a province.

        Returns:
            column (Column): The column containing the military info.
        """
        manpower_icon = Layout.create_icon_with_border(
            icon_name="base_manpower",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        manpower_label, manpower_value = Layout.create_text_with_inline_label(
            "Manpower",
            text_key="-INFO_PROVINCE_LOCAL_MANPOWER-",
            expand_x=True,
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(5, 1))

        sailors_icon = Layout.create_icon_with_border(
            icon_name="sailors",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        sailors_label, sailors_value = Layout.create_text_with_inline_label(
            "Sailors",
            text_key="-INFO_PROVINCE_LOCAL_SAILORS-",
            expand_x=True,
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(5, 1))

        troops_info_column = sg.Column([
            [manpower_label, manpower_icon, manpower_value, 
            sailors_icon, sailors_label, sailors_value]
        ], background_color=Layout.MEDIUM_FRAME_BG)

        garrison_icon = Layout.create_icon_with_border(
            icon_name="fort_defense",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        garrison_label, garrison_value = Layout.create_text_with_inline_label(
            "Garrison",
            text_key="-INFO_PROVINCE_GARRISON_SIZE-",
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(5, 1))

        defense_info_column = sg.Column([
            [garrison_label, garrison_icon, garrison_value],
        ], background_color=Layout.MEDIUM_FRAME_BG, pad=(5, 5))

        military_info_frame = sg.Frame("", [
            [troops_info_column, defense_info_column]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        element_justification="center",
        expand_x=True,
        relief=sg.RELIEF_SUNKEN)

        military_label = sg.Text(
            "Military", 
            background_color=Layout.SECTION_BANNER_BG,
            font=("Georgia", 12, "bold"),
            text_color=Layout.LIGHT_TEXT)
        military_icon = Layout.create_icon_with_border(
            icon_name="military",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        military_header_frame = sg.Frame("", [
            [military_label, military_icon, sg.Push(background_color=Layout.SECTION_BANNER_BG)]
        ], background_color=Layout.SECTION_BANNER_BG, 
        expand_x=True, 
        pad=((10, 10), (0, 10)),
        relief=sg.RELIEF_SOLID)

        fort_level = sg.Image("", key="-INFO_PROVINCE_FORT_LEVEL-", )
        fort_level = Layout.create_icon_with_border(
            "",
            image_key="-INFO_PROVINCE_FORT_LEVEL-",
            borders=[(Layout.GOLD_FRAME_UPPER, 1, sg.RELIEF_RIDGE)],
            border_pad=(10, 10),
            image_size=(48, 48))

        return sg.Column([
            [military_header_frame],
            [military_info_frame, fort_level]
        ], background_color=Layout.LIGHT_FRAME_BG, 
        expand_x=True, 
        pad=(0, 0), 
        vertical_alignment="top")

    @staticmethod
    def create_status_column(name: str):
        autonomy_icon = Layout.create_icon_with_border(
            icon_name="local_autonomy",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        autonomy_value = sg.Text(
            "",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            justification="center",
            key=f"-INFO_{name}_LOCAL_AUTONOMY-",
            size=(5, 1),
            text_color=Layout.GREEN_TEXT)

        autonomy_frame = sg.Frame("", [
            [autonomy_icon, autonomy_value]
        ], background_color=Layout.MEDIUM_FRAME_BG, border_width=0)

        devastation_icon = Layout.create_icon_with_border(
            icon_name="local_devastation",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        devastation_value = sg.Text(
            "",
            background_color=Layout.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            justification="center",
            key=f"-INFO_{name}_LOCAL_DEVASTATION-",
            size=(5, 1),
            text_color=Layout.GREEN_TEXT)

        devastation_frame = sg.Frame("", [
            [devastation_icon, devastation_value]
        ], background_color=Layout.MEDIUM_FRAME_BG, border_width=0)

        province_status_frame = sg.Frame("", [
            [autonomy_frame, devastation_frame]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        border_width=4,
        pad=(5, 5),
        relief=sg.RELIEF_SUNKEN)

        return sg.Column([
            [province_status_frame],
        ], background_color=Layout.LIGHT_FRAME_BG, expand_x=True)

    @staticmethod
    def create_province_info_column():
        """Creates the province column section.
        
        This section contains the province's trade, military, and demographic information.
        
        Returns:
            column (Column): The column containing the province info.
        """
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
            pad=(20, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")

        area_km2_label = Layout.create_text_with_frame(
            "Area in km^2",
            content_color=Layout.LIGHT_TEXT,
            frame_background_color=Layout.SECTION_BANNER_BG,
            pad=(15, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        area_km2_value = Layout.create_text_with_frame(
            "",
            key="-INFO_PROVINCE_SIZE_KM-",
            content_color=Layout.LIGHT_TEXT,
            font=("Georgia", 12),
            frame_background_color=Layout.SUNK_FRAME_BG,
            frame_border_width=2,
            justification="center",
            pad=((5, 15), (15, 15)),
            relief=sg.RELIEF_SUNKEN,
            size=(15, 1))

        geographic_info_frame = Layout.create_geographic_province_info_frame()
        province_info_frame = sg.Frame("", [
            [geographic_info_frame],
            [development_label, development_info_frame,
                sg.Push(background_color=Layout.LIGHT_FRAME_BG),
            area_km2_label, area_km2_value],
            [demographic_info_column, trade_and_mil_column]
        ], background_color=Layout.LIGHT_FRAME_BG, 
        border_width=5,
        expand_x=True,
        expand_y=True,
        key="-PROVINCE_INFO_FRAME-",
        pad=(10, 10),
        size=(985, 510),
        relief=sg.RELIEF_GROOVE)

        return sg.Column([
            [province_info_frame]
        ], background_color=Layout.LIGHT_FRAME_BG,
        expand_x=True,
        expand_y=True,
        key="-PROVINCE_INFO_COLUMN-",
        pad=((5, 10), (10, 10)),
        vertical_alignment="top")

    @staticmethod
    def create_geographic_area_info_frame():
        """Creates the geographical frame section for an area.

        Returns:
            frame (Frame): The frame containing the area info.
        """
        area_name = sg.Text(
            "",
            key="-INFO_AREA_NAME-",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="left",
            text_color=Layout.LIGHT_TEXT)

        spacer_left = sg.Text(
            "", 
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="left")

        region_name = sg.Text(
            "",
            key="-INFO_AREA_REGION_NAME-",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="right",
            text_color=Layout.LIGHT_TEXT)

        spacer_right = sg.Text(
            "",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="right")

        area_column = sg.Column([
                [area_name],
                [spacer_left]
            ], background_color=Layout.TOP_BANNER_BG,
            element_justification="left",
            expand_x=True)

        region_column = sg.Column([
                [region_name],
                [spacer_right]
            ], background_color=Layout.TOP_BANNER_BG,
            element_justification="right",
            expand_x=True)

        return sg.Frame("", [
            [area_column, sg.Push(background_color=Layout.TOP_BANNER_BG), region_column]
        ], background_color=Layout.TOP_BANNER_BG,
        border_width=4,
        expand_x=True,
        pad=(5, 5),
        relief=sg.RELIEF_RAISED,
        vertical_alignment="center")

    @staticmethod
    def create_provinces_table_header():
        """Creates the header for the province table.
        
        Returns:
            frame (Frame): The frame containing the header icons.
        """
        province_icon = Layout.create_icon_with_border(
            icon_name="map_province",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        province_header = sg.Frame("", [
            [province_icon]
        ], background_color=Layout.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(220, 40))

        owner_icon = Layout.create_icon_with_border(
            icon_name="protective_attitude",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        owner_header = sg.Frame("", [
            [owner_icon]
        ], background_color=Layout.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(220, 40))

        development_icon = Layout.create_icon_with_border(
            icon_name="development",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        development_header = sg.Frame("", [
            [development_icon]
        ], background_color=Layout.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(44, 40))

        trade_power_icon = Layout.create_icon_with_border(
            icon_name="trade_power",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_power_header = sg.Frame("", [
            [trade_power_icon]
        ], background_color=Layout.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(111, 40))

        religion_icon = Layout.create_icon_with_border(
            icon_name="religion",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        religion_header = sg.Frame("", [
            [religion_icon]
        ], background_color=Layout.SECTION_BANNER_BG,
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(165, 40))

        culture_icon = Layout.create_icon_with_border(
            icon_name="culture",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        culture_header = sg.Frame("", [
            [culture_icon]
        ], background_color=Layout.SECTION_BANNER_BG,
        border_width=0, 
        element_justification="center",
        pad=(0, 0), 
        size=(198, 40))

        icon_row = sg.Column([
            [province_header, 
            owner_header, 
            development_header, 
            trade_power_header, 
            religion_header, 
            culture_header]
        ], background_color=Layout.SECTION_BANNER_BG, 
        pad=(0, 0))

        return sg.Frame("", 
            layout=[[icon_row]], 
            background_color=Layout.SECTION_BANNER_BG,
            expand_x=True,
            pad=(0, 0), 
            relief=sg.RELIEF_SOLID)

    @staticmethod
    def create_area_provinces_table():
        """Creates the table that will be used to display the an area's provinces.
        
        Includes fields for province name, owner, development, religion and culture.
        
        Returns:
            column (Column): The table and its header packed into a column.
        """
        table_header = Layout.create_provinces_table_header()

        table = sg.Table(
            values=[],
            key="-INFO_AREA_PROVINCES_TABLE-",
            alternating_row_color=Layout.DARK_FRAME_BG,
            background_color=Layout.MEDIUM_FRAME_BG,
            auto_size_columns=False,
            col_widths=[20, 20, 4, 10, 15, 18],
            headings=["Name", "Owner", "Dev.", "Trade Power", "Religion", "Culture"],
            header_background_color=Layout.SECTION_BANNER_BG,
            header_relief=sg.RELIEF_SOLID,
            font=("Georgia", 12),
            text_color=Layout.LIGHT_TEXT,
            hide_vertical_scroll=False,
            justification="left",
            num_rows=5,
            pad=(0, 0),
            row_height=28,
            sbar_arrow_color=Layout.GOLD_FRAME_UPPER,
            sbar_background_color=Layout.RED_BANNER_BG,
            sbar_trough_color=Layout.GOLD_FRAME_LOWER,
            sbar_relief=sg.RELIEF_GROOVE,
            sbar_width=5)

        provinces_info = sg.Frame("", [
            [table_header],
            [table]
        ], expand_x=True, pad=(0, 0))

        return sg.Column([
            [provinces_info]
        ], background_color=Layout.LIGHT_FRAME_BG,
        pad=(10, 0))

    @staticmethod
    def create_income_column(name: str):
        total_income_icon = Layout.create_icon_with_border(
            icon_name="total_income",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        total_income_label, total_income_value = Layout.create_text_with_inline_label(
            "Total Income",
            text_key=f"-INFO_{name}_INCOME-",
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(10, 1),
            expand_x=True)

        total_income_column = sg.Column([
            [total_income_label, total_income_icon, total_income_value]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        pad=(0, 0))

        tax_income_icon = Layout.create_icon_with_border(
            icon_name="income",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        tax_income_label, tax_income_value = Layout.create_text_with_inline_label(
            "Tax",
            text_key=f"-INFO_{name}_TAX_INCOME-", 
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(10, 1),
            expand_x=True)

        tax_income_column = sg.Column([
            [tax_income_label, tax_income_icon, tax_income_value]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        pad=(0, 0))

        goods_income_icon = Layout.create_icon_with_border(
            icon_name="trade_value_income",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        goods_income_label, goods_income_value = Layout.create_text_with_inline_label(
            "Production",
            text_key=f"-INFO_{name}_PRODUCTION_INCOME-",
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(15, 1),
            expand_x=True)  

        goods_income_column = sg.Column([
            [goods_income_label, goods_income_icon, goods_income_value]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        pad=(0, 0))

        income_info_frame = sg.Frame("", [
            [total_income_column, tax_income_column, goods_income_column]
        ], background_color=Layout.DARK_FRAME_BG,
        border_width=3,
        expand_x=True,
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        return sg.Column([
            [income_info_frame]
        ], background_color=Layout.LIGHT_FRAME_BG,
        pad=((10, 10), (15, 10)),
        vertical_alignment="top")

    @staticmethod
    def create_trade_column(name: str):
        trade_power_icon = Layout.create_icon_with_border(
            icon_name="trade_power",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_power_label, trade_power_value = Layout.create_text_with_inline_label(
            "Trade Power",
            text_key=f"-INFO_{name}_TRADE_POWER-",
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(10, 1),
            expand_x=True)

        trade_power_column = sg.Column([
            [trade_power_label, trade_power_icon, trade_power_value]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        pad=(0, 0))

        goods_produced_icon = Layout.create_icon_with_border(
            icon_name="goods_produced",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        goods_produced_label, goods_produced_value = Layout.create_text_with_inline_label(
            "Goods Produced",
            text_key=f"-INFO_{name}_GOODS_PRODUCED-", 
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(10, 1),
            expand_x=True)

        goods_produced_column = sg.Column([
            [goods_produced_label, goods_produced_icon, goods_produced_value]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        pad=(0, 0))

        dominant_good_icon = Layout.create_icon_with_border (
            icon_name="warehouse",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        dominant_good_label, dominant_good_value = Layout.create_text_with_inline_label(
            "Dominant Trade Good",
            text_key=f"-INFO_{name}_DOMINANT_TRADE_GOOD-",
            label_colors=(Layout.LIGHT_TEXT, Layout.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(Layout.LIGHT_TEXT, Layout.SUNK_FRAME_BG),
            text_field_size=(15, 1),
            expand_x=True)  

        dominant_good_column = sg.Column([
            [dominant_good_label, dominant_good_icon, dominant_good_value]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        pad=(0, 0))

        income_info_frame = sg.Frame("", [
            [trade_power_column, goods_produced_column, dominant_good_column]
        ], background_color=Layout.DARK_FRAME_BG,
        border_width=3,
        expand_x=True,
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        return sg.Column([
            [income_info_frame]
        ], background_color=Layout.LIGHT_FRAME_BG,
        pad=((10, 10), (0, 10)),
        vertical_alignment="top")

    @staticmethod
    def create_area_info_column():
        """Creates the area column section.
        
        This section contains the area's provinces table and the area's overall income and trade information.
        
        Returns:
            column (Column): The column containing the area info.
        """
        geographic_info_frame = Layout.create_geographic_area_info_frame()

        development_label = Layout.create_text_with_frame(
            content="Development",
            content_color=Layout.LIGHT_TEXT,
            frame_background_color=Layout.SECTION_BANNER_BG,
            pad=(15, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        development_info_frame = Layout.create_development_info_frame(name="AREA")

        area_provinces_table = Layout.create_area_provinces_table()

        income_info_column = Layout.create_income_column(name="AREA")
        trade_info_column = Layout.create_trade_column(name="AREA")

        area_km2_label = Layout.create_text_with_frame(
            "Area in km^2",
            content_color=Layout.LIGHT_TEXT,
            frame_background_color=Layout.SECTION_BANNER_BG,
            pad=(15, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        area_km2_value = Layout.create_text_with_frame(
            "",
            key="-INFO_AREA_SIZE_KM-",
            content_color=Layout.LIGHT_TEXT,
            font=("Georgia", 12),
            frame_background_color=Layout.SUNK_FRAME_BG,
            frame_border_width=2,
            justification="center",
            pad=((5, 15), (15, 15)),
            relief=sg.RELIEF_SUNKEN,
            size=(15, 1))

        area_info_frame = sg.Frame("", [
            [geographic_info_frame],
            [development_label, development_info_frame,
                sg.Push(background_color=Layout.LIGHT_FRAME_BG),
            area_km2_label, area_km2_value],
            [area_provinces_table],
            [income_info_column],
            [trade_info_column]
        ], background_color=Layout.LIGHT_FRAME_BG,
        border_width=5,
        expand_x=True,
        expand_y=True,
        key="-AREA_INFO_FRAME-",
        pad=(10, 10),
        relief=sg.RELIEF_GROOVE,
        size=(985, 510))

        return sg.Column([
            [area_info_frame]
        ], background_color=Layout.LIGHT_FRAME_BG,
        expand_x=True,
        expand_y=True,
        key="-AREA_INFO_COLUMN-",
        pad=((5, 10), 10, 10),
        vertical_alignment="top",
        visible=False)

    @staticmethod
    def create_geographic_region_info_frame():
        """Creates the geographical frame section for an area.

        Returns:
            frame (Frame): The frame containing the area info.
        """
        region_name = sg.Text(
            "",
            key="-INFO_REGION_NAME-",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="right",
            text_color=Layout.LIGHT_TEXT)

        spacer_left = sg.Text(
            "", 
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="left")

        region_column = sg.Column([
            [region_name],
            [spacer_left]
        ], background_color=Layout.TOP_BANNER_BG,
        element_justification="left",
        expand_x=True)

        spacer_right = sg.Text(
            "",
            background_color=Layout.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="right")

        spacer_column = sg.Column([
            [spacer_right],
        ], background_color=Layout.TOP_BANNER_BG,
        element_justification="left",
        expand_x=True)

        return sg.Frame("", [
            [region_column, sg.Push(background_color=Layout.TOP_BANNER_BG), spacer_column]
        ], background_color=Layout.TOP_BANNER_BG,
        border_width=4,
        expand_x=True,
        pad=(5, 5),
        relief=sg.RELIEF_RAISED,
        vertical_alignment="center")

    @staticmethod
    def create_areas_table_header():
        """Creates the header for the area table.
        
        Returns:
            frame (Frame): The frame containing the header icons.
        """
        area_icon = Layout.create_icon_with_border(
            icon_name="map_area",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        area_header = sg.Frame("", [
            [area_icon]
        ], background_color=Layout.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(220, 40))

        development_icon = Layout.create_icon_with_border(
            icon_name="development",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        development_header = sg.Frame("", [
            [development_icon]
        ], background_color=Layout.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(44, 40))

        trade_power_icon = Layout.create_icon_with_border(
            icon_name="trade_power",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_power_header = sg.Frame("", [
            [trade_power_icon]
        ], background_color=Layout.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(111, 40))

        religion_icon = Layout.create_icon_with_border(
            icon_name="religion",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        religion_header = sg.Frame("", [
            [religion_icon]
        ], background_color=Layout.SECTION_BANNER_BG,
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(198, 40))

        culture_icon = Layout.create_icon_with_border(
            icon_name="culture",
            borders=[(Layout.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        culture_header = sg.Frame("", [
            [culture_icon]
        ], background_color=Layout.SECTION_BANNER_BG,
        border_width=0, 
        element_justification="center",
        pad=(0, 0), 
        size=(198, 40))

        icon_row = sg.Column([
            [area_header, 
            development_header, 
            trade_power_header,
            religion_header,
            culture_header]
        ], background_color=Layout.SECTION_BANNER_BG, 
        pad=(0, 0))

        return sg.Frame("", 
            layout=[[icon_row]], 
            background_color=Layout.SECTION_BANNER_BG,
            expand_x=True,
            pad=(0, 0), 
            relief=sg.RELIEF_SOLID)

    @staticmethod
    def create_region_areas_table():
        table_header = Layout.create_areas_table_header()

        table = sg.Table(
            values=[],
            key="-INFO_REGION_AREAS_TABLE-",
            alternating_row_color=Layout.DARK_FRAME_BG,
            background_color=Layout.MEDIUM_FRAME_BG,
            auto_size_columns=False,
            col_widths=[20, 4, 10, 18, 18],
            headings=["Name", "Dev.", "Trade Power", "Dominant Religion", "Dominant Culture"],
            header_background_color=Layout.SECTION_BANNER_BG,
            header_relief=sg.RELIEF_SOLID,
            font=("Georgia", 12),
            text_color=Layout.LIGHT_TEXT,
            hide_vertical_scroll=False,
            justification="left",
            num_rows=5,
            pad=(0, 0),
            row_height=28,
            sbar_arrow_color=Layout.GOLD_FRAME_UPPER,
            sbar_background_color=Layout.RED_BANNER_BG,
            sbar_trough_color=Layout.GOLD_FRAME_LOWER,
            sbar_relief=sg.RELIEF_GROOVE,
            sbar_width=5)

        areas_info = sg.Frame("", [
            [table_header],
            [table]
        ], expand_x=True, pad=(0, 0))

        return sg.Column([
            [areas_info]
        ], background_color=Layout.LIGHT_FRAME_BG,
        pad=(10, 0))

    @staticmethod
    def create_region_info_column():
        """Creates the region column section.
        
        This section contains the region's areas table and the regions's overall income and trade information.
        
        Returns:
            column (Column): The column containing the region info.
        """
        geographic_info_frame = Layout.create_geographic_region_info_frame()

        development_label = Layout.create_text_with_frame(
            content="Development",
            content_color=Layout.LIGHT_TEXT,
            frame_background_color=Layout.SECTION_BANNER_BG,
            pad=(15, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        development_info_frame = Layout.create_development_info_frame(name="REGION")

        region_areas_table = Layout.create_region_areas_table()

        income_info_column = Layout.create_income_column(name="REGION")
        trade_info_column = Layout.create_trade_column(name="REGION")

        area_km2_label = Layout.create_text_with_frame(
            "Area in km^2",
            content_color=Layout.LIGHT_TEXT,
            frame_background_color=Layout.SECTION_BANNER_BG,
            pad=(15, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        area_km2_value = Layout.create_text_with_frame(
            "",
            key="-INFO_REGION_SIZE_KM-",
            content_color=Layout.LIGHT_TEXT,
            font=("Georgia", 12),
            frame_background_color=Layout.SUNK_FRAME_BG,
            frame_border_width=2,
            justification="center",
            pad=((5, 15), (15, 15)),
            relief=sg.RELIEF_SUNKEN,
            size=(15, 1))

        region_info_frame = sg.Frame("", [
            [geographic_info_frame],
            [development_label, development_info_frame,
                sg.Push(background_color=Layout.LIGHT_FRAME_BG),
            area_km2_label, area_km2_value],
            [region_areas_table],
            [income_info_column],
            [trade_info_column]
        ], background_color=Layout.LIGHT_FRAME_BG,
        border_width=5,
        expand_x=True,
        expand_y=True,
        key="REGION_INFO_FRAME-",
        pad=(10, 10),
        relief=sg.RELIEF_GROOVE,
        size=(985, 510))

        return sg.Column([
            [region_info_frame]
        ], background_color=Layout.LIGHT_FRAME_BG,
        expand_x=True,
        expand_y=True,
        key="-REGION_INFO_COLUMN-",
        pad=((5, 10), 10, 10),
        vertical_alignment="top",
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
        ], background_color=Layout.LIGHT_FRAME_BG, relief=sg.RELIEF_GROOVE, pad=(0, 0), border_width=5)

        return Layout.add_border(
            layout=[[canvas_frame]], 
            borders=[
                (Layout.GOLD_FRAME_LOWER, 3, sg.RELIEF_RIDGE),
                (Layout.GOLD_FRAME_UPPER, 3, sg.RELIEF_RIDGE)],
            pad=(15, 10))

    @staticmethod
    def create_map_modes_frame(map_modes: dict):
        """Creates the map modes frame for selecting map modes.
        
        Args:
            map_modes (dict[MapMode]): The possible map modes to choose from when displaying the map.
        
        Returns:
            frame (Frame): The frame containing the map mode buttons.
        """
        map_mode_label = Layout.create_text_with_frame(
            "MAP MODES",
            content_color=Layout.LIGHT_TEXT,
            font=("Georgia", 12, "bold"),
            frame_background_color=Layout.RED_BANNER_BG,
            justification="center",
            relief=sg.RELIEF_SOLID,
            size=(10, 1))

        reset_button = sg.Button(
            "RESET",
            key="-RESET-",
            button_color=(Layout.LIGHT_TEXT, Layout.BUTTON_BG),
            font=("Garamond", 10, "bold"),
            pad=(15, 15),
            visible=True)

        map_mode_buttons = [
            sg.Button(
                mode.name,
                key=mode.value,
                button_color=(Layout.LIGHT_TEXT, Layout.BUTTON_BG),
                font=("Garamond", 10, "bold"),
                pad=(15, 15),
                visible=True)
            for mode in map_modes
        ]

        map_mode_frame = sg.Frame("", [
            [map_mode_label],
            [reset_button],
            *[[button] for button in map_mode_buttons]
        ], background_color=Layout.SUNK_FRAME_BG,
        border_width=5,
        element_justification="center", 
        relief=sg.RELIEF_GROOVE, 
        pad=(0, 0))

        return Layout.add_border(
            layout=[[map_mode_frame]],
            borders=[
                (Layout.GOLD_FRAME_LOWER, 2, sg.RELIEF_RIDGE),
                (Layout.GOLD_FRAME_UPPER, 2, sg.RELIEF_RIDGE)],
            pad=(10, 10))

    @staticmethod
    def build_layout(canvas_size: tuple[int, int], map_modes: dict):
        """Driver method that builds the layout to be used within a PySimpleGUI|FreeSimpleGUI `Window` element.
        
        Args:
            canvas_size (tuple[int, int]): The `(x, y)` size of the canvas determined by the display size.
            map_modes (dict[MapMode]): The possible map modes to choose from when displaying the map.
        """
        print("Building layout....")
        window_header = Layout.create_window_header()

        selected_info_frame = sg.Frame("", [
            [Layout.create_search_column(), 
                Layout.create_province_info_column(), 
                Layout.create_area_info_column(),
                Layout.create_region_info_column()]
        ], key="-WORLD_INFO-",
        background_color=Layout.LIGHT_FRAME_BG, 
        border_width=5,
        expand_x=True,  
        expand_y=True,
        pad=(0, 0), 
        relief=sg.RELIEF_GROOVE)

        bordered_info = Layout.add_border(
            layout=[[selected_info_frame]],
            borders=[
                (Layout.GOLD_FRAME_LOWER, 3, sg.RELIEF_RIDGE),
                (Layout.GOLD_FRAME_UPPER, 3, sg.RELIEF_RIDGE)],
            pad=(15, 10),
            expand_x=True,
            expand_y=True)

        canvas_frame = Layout.create_map_canvas_frame(canvas_size=canvas_size, key="-CANVAS-")
        map_mode_frame = Layout.create_map_modes_frame(map_modes=map_modes)

        display_frame = sg.Frame("", [
            [canvas_frame, map_mode_frame]
        ], background_color=Layout.LIGHT_FRAME_BG,
        border_width=0,
        vertical_alignment="center")

        display_column = sg.Column([
            [display_frame]
        ], background_color=Layout.MEDIUM_FRAME_BG,
        vertical_alignment="center")

        layout = [
            [window_header],
            [display_column],
            [bordered_info],
        ]

        return layout
