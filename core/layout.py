import FreeSimpleGUI as sg



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
    DARK_FRAME_BG = "#2a343b"
    SUNKEN_FRAME_BG = "#283239"
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
        Creates a raised border around the given layout.
        
        Args:
            layout (list[list]): The layout to wrap.
            inner_border (tuple[str, int]): Specifies the hex color and width of the inner border.
            outer_border (tuple[str, int]): Specifies the hex color and width of the outer border.
            pad (tuple[int, int]): Amount of padding to put around each frame in pixels (left/right, top/bottom).
            expand_x (bool):  If True the element will automatically expand in the X direction to fill available space.
            expand_y (bool):  If True the element will automatically expand in the Y direction to fill available space
        
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
        font: tuple[str, int, str]=("Georgia", 12, "bold")):
        """
        Creates text with a framed background.
        
        Args:
            content (str): The text content.
            content_color (str): The hex color for the text content.
            frame_background_color (str): The hex color for the background.
            font (tuple[int, str]|tuple[int, str, str]): Specifies the font family for the text content
                (font_name, font_size, "bold"/"italic"/"underline"/"overstrike").
        
        Returns:
            frame (Frame): The frame containing the wrapped text.
        """
        return sg.Frame("", [
            [sg.Text(
                content, 
                font=font, 
                text_color=content_color, 
                background_color=frame_background_color)]
        ], background_color=frame_background_color, element_justification="left", pad=(5, 5))

    @staticmethod
    def create_text_with_header_label():
        return 

    @staticmethod
    def create_text_with_inline_label(
        label_name: str,
        label_colors: tuple[str, str],
        text_colors: tuple[str, str],
        text_key: str,
        default_text_value: str="",
        font: tuple[str, int, str]=("Georgia", 12)):
        """
        Creates text with a label inline with a value field.
        
        Args:
            label_name (str): The name of the text label.
            label_colors (tuple[str, str]): The label font and label background hex colors.
            text_colors (tuple[str, str]): The text font and field background hex colors.
            text_key (str): The string that will be returned from `window.read()` to access the text value.
                Should follow the format `-NAME-` for clarity.
            default_text_value (str): The default text to show.
            font (tuple[str, int, str]|tuple[str, int]): Specifies the font family for the text content
                (font_name, font_size, "bold"/"italic"/"underline"/"overstrike").
        
        Returns:
            text_list (list[Text, Text]): The label and inline text field.
        """
        label_text_color, label_background = label_colors
        label_text = sg.Text(
            label_name, 
            font=font, 
            text_color=label_text_color, 
            background_color=label_background)

        text_color, field_background = text_colors
        value_text = sg.Text(
            default_text_value, 
            key=text_key, 
            font=font, 
            text_color=text_color, 
            background_color=field_background, 
            size=(10, 1))

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
            background_color=Layout.SUNKEN_FRAME_BG,
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
                background_color=Layout.LIGHT_FRAME_BG)
            ]
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
        return sg.Column([
            [sg.Frame("", [
                [sg.Push(Layout.LIGHT_FRAME_BG), 
                    Layout.create_text_with_frame("Search", Layout.LIGHT_TEXT, Layout.RED_BANNER_BG),
                sg.Push(Layout.LIGHT_FRAME_BG)],

                [sg.Input(size=(30, 1), key="-SEARCH-", font=("Georgia", 12), enable_events=True, text_color=Layout.LIGHT_TEXT, background_color=Layout.DARK_FRAME_BG)],
                [sg.Checkbox("Exact Matches?", key="-EXACT_MATCH-", enable_events=True, font=("Georgia", 11), text_color=Layout.LIGHT_TEXT, background_color=Layout.LIGHT_FRAME_BG)],

                [sg.Push(background_color=Layout.LIGHT_FRAME_BG), sg.Frame("", [
                    [sg.Listbox(values=[], size=(30, 5), key="-RESULTS-", enable_events=True, font=("Segoe UI", 12), visible=False, text_color=Layout.LIGHT_TEXT, background_color=Layout.SUNKEN_FRAME_BG)],
                    [Layout.create_button("Go to", "-GOTO-", Layout.LIGHT_TEXT, Layout.BUTTON_BG, visible=False, font=("Garamond", 12, "bold"))],
                    [Layout.create_button("Clear", "-CLEAR-", Layout.LIGHT_TEXT, Layout.BUTTON_BG, visible=False, font=("Garamond", 12, "bold"))]
                ], background_color=Layout.LIGHT_FRAME_BG, element_justification="center", border_width=0),
                sg.Push(background_color=Layout.LIGHT_FRAME_BG)]

            ], expand_y=True, pad=(10, 10), relief=sg.RELIEF_GROOVE, background_color=Layout.LIGHT_FRAME_BG, border_width=5, title_color=Layout.LIGHT_TEXT)]
        ], vertical_alignment="top", pad=(10, 10), expand_y=True, justification="left", background_color=Layout.DARK_FRAME_BG)

    @staticmethod
    def create_geographic_province_info_frame():
        """Creates the geographical frame section for a province.

        Returns:
            frame (Frame): The frame containing the province info.
        """
        province_label, province_field = Layout.create_text_with_inline_label(
            label_name="Province:",
            label_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_key="-INFO_PROVINCE_NAME-",
            font=("Georgia", 14, "bold"))

        capital_label, capital_field = Layout.create_text_with_inline_label(
            label_name="Capital:",
            label_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_key="-INFO_CAPITAL-")

        area_label, area_field = Layout.create_text_with_inline_label(
            label_name="Area:",
            label_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_key="-INFO_PROVINCE_AREA-",
            font=("Georgia", 14, "bold"))

        region_label, region_field = Layout.create_text_with_inline_label(
            label_name="Region:",
            label_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_colors=(Layout.LIGHT_TEXT, Layout.TOP_BANNER_BG),
            text_key="-INFO_PROVINCE_REGION-")

        return sg.Frame("", [
            [sg.Column([
                [province_label, province_field],
                [capital_label, capital_field]
            ], background_color=Layout.TOP_BANNER_BG, element_justification="left", expand_x=True),

            sg.Column([
                [area_label, area_field],
                [region_label, region_field],
            ], background_color=Layout.TOP_BANNER_BG, element_justification="right", expand_x=True)]
        ], background_color=Layout.TOP_BANNER_BG, relief=sg.RELIEF_RAISED, border_width=4, title_color=Layout.LIGHT_TEXT, pad=(5, 5), expand_x=True)

    @staticmethod
    def create_development_info_frame():
        """Creates the development frame section for a province.

        Returns:
            frame (Frame): The frame containing the development info.
        """
        tax_label, tax_field = Layout.create_text_with_inline_label(
            label_name="Tax",
            label_colors=(Layout.LIGHT_TEXT, Layout.DARK_FRAME_BG),
            text_colors=(Layout.GREEN_TEXT, Layout.SUNKEN_FRAME_BG),
            text_key="-INFO_BASE_TAX-")

        prod_label, prod_field = Layout.create_text_with_inline_label(
            label_name="Production",
            label_colors=(Layout.LIGHT_TEXT, Layout.DARK_FRAME_BG),
            text_colors=(Layout.GREEN_TEXT, Layout.SUNKEN_FRAME_BG),
            text_key="-INFO_BASE_PRODUCTION-")

        pop_label, pop_field = Layout.create_text_with_inline_label(
            label_name="Manpower",
            label_colors=(Layout.LIGHT_TEXT, Layout.DARK_FRAME_BG),
            text_colors=(Layout.GREEN_TEXT, Layout.SUNKEN_FRAME_BG),
            text_key="-INFO_BASE_MANPOWER-")

        return sg.Frame("", [
            [tax_label, tax_field, prod_label, prod_field, pop_label, pop_field]
        ], background_color=Layout.DARK_FRAME_BG, pad=(5, 5), relief=sg.RELIEF_SUNKEN, border_width=3, title_color=Layout.LIGHT_TEXT)

    @staticmethod
    def create_demographic_info_frame():
        """Creates the demographics frame section for a province.

        Returns:
            frame (Frame): The frame containing the demographic info.
        """
        return sg.Frame("", [
            [sg.Text("Cored by:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.DARK_FRAME_BG)],
            [sg.Frame("", [
                [sg.Text("", key="-INFO_OWNER-", font=("Georgia", 12), text_color=Layout.GREEN_TEXT, background_color=Layout.SUNKEN_FRAME_BG, size=(20, 1))]
            ], background_color=Layout.SUNKEN_FRAME_BG, pad=(5, 5), border_width=0)],

            [sg.Text("Culture:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.DARK_FRAME_BG)],
            [sg.Frame("", [
                [sg.Text("", key="-INFO_CULTURE-", font=("Georgia", 12), text_color=Layout.GREEN_TEXT, background_color=Layout.SUNKEN_FRAME_BG, size=(20, 1))]
            ], background_color=Layout.SUNKEN_FRAME_BG, pad=(5, 5), border_width=0)],

            [sg.Text("Religion:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.DARK_FRAME_BG)],
            [sg.Frame("", [
                [sg.Text("", key="-INFO_RELIGION-", font=("Georgia", 12), text_color=Layout.GREEN_TEXT, background_color=Layout.SUNKEN_FRAME_BG, size=(20, 1))]
            ], background_color=Layout.SUNKEN_FRAME_BG, pad=(5, 5), border_width=0)]

        ], background_color=Layout.DARK_FRAME_BG, pad=(5, 5), relief=sg.RELIEF_SUNKEN, border_width=4, expand_x=True)

    @staticmethod
    def create_province_info_column():
        """Creates the province column section.
        
        This section contains the province geographic, development, and demographic information.
        
        Returns:
            column (Column): The column containing the province info.
        """
        return sg.Column([
            [sg.Frame("", [
                [Layout.create_geographic_province_info_frame()],

                [Layout.create_text_with_frame(
                    content="Development",
                    content_color=Layout.LIGHT_TEXT,
                    frame_background_color=Layout.SECTION_BANNER_BG)],
                [Layout.create_development_info_frame(), sg.Push(background_color=Layout.LIGHT_FRAME_BG)],  

                [Layout.create_text_with_frame(
                    content="Demographics",
                    content_color=Layout.LIGHT_TEXT,
                    frame_background_color=Layout.SECTION_BANNER_BG)],
                [Layout.create_demographic_info_frame(), sg.Push(background_color=Layout.LIGHT_FRAME_BG)]

            ], key="-PROVINCE_INFO-", pad=(10, 10), relief=sg.RELIEF_GROOVE, background_color=Layout.LIGHT_FRAME_BG, border_width=5, title_color=Layout.LIGHT_TEXT)]
        ], vertical_alignment="top", pad=(10, 10), expand_y=True, background_color=Layout.DARK_FRAME_BG)

    @staticmethod
    def create_map_canvas_frame(canvas_size: tuple[int, int], key: str):
        """Creates a frame containing the map canvas.
        
        Args:
            canvas_size (tuple[int, int]): The `(x, y)` size of the canvas.
            key (str): The string that will be returned from `window.read()` when the canvas is interacted with.
                Should follow the format `-NAME-` for clarity.
        
        Returns:
            frame (Frame): The frame containing the canvas.
        """
        return sg.Frame("", [
            [sg.Canvas(background_color="black", size=canvas_size, key=key, pad=(10, 10))]
        ], background_color=Layout.LIGHT_FRAME_BG, relief=sg.RELIEF_GROOVE, pad=(10, 10), border_width=5)

    @staticmethod
    def create_map_modes_frame(map_modes: dict):
        """Creates the map modes frame for selecting map modes.
        
        Args:
            map_modes (dict[MapMode]): The possible map modes to choose from when displaying the map.
        
        Returns:
            frame (Frame): The frame containing the map mode buttons.
        """
        return sg.Frame("", [
            [sg.Text("Map Modes", font=("Garmond", 12, "bold"), background_color=Layout.DARK_FRAME_BG, text_color=Layout.LIGHT_TEXT)],
            [Layout.create_button(mode.name, mode.value, Layout.LIGHT_TEXT, Layout.BUTTON_BG)
                for mode in map_modes],
            [Layout.create_button("Reset View", "-RESET-", Layout.LIGHT_TEXT, Layout.BUTTON_BG)]
        ], element_justification="center", relief=sg.RELIEF_GROOVE, pad=(10, 10), background_color=Layout.DARK_FRAME_BG, border_width=5, title_color=Layout.LIGHT_TEXT)

    @staticmethod
    def build_layout(canvas_size: tuple[int, int], map_modes: dict):
        """Driver method that builds the layout to be used within a PySimpleGUI|FreeSimpleGUI `Window` element.
        
        Args:
            canvas_size (tuple[int, int]): The `(x, y)` size of the canvas determined by the display size.
            map_modes (dict[MapMode]): The possible map modes to choose from when displaying the map.
        """
        return [
            [Layout.create_window_header()],

            [sg.Frame("", [
                [Layout.create_search_column(), Layout.create_province_info_column()]
            ], pad=(10, 10), relief=sg.RELIEF_GROOVE, background_color=Layout.LIGHT_FRAME_BG, border_width=5, expand_x=True)],

            [Layout.create_map_canvas_frame(canvas_size=canvas_size, key="-CANVAS-")],

            [Layout.create_map_modes_frame(map_modes=map_modes)],
        ]
