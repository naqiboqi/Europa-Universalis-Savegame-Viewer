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
    def create_button(
        name: str,
        key: str,
        font_color: str,
        button_color: str,
        font: tuple[str, int, str]=("Garamond", 10, "bold"),
        visible: bool=True):
        """
        Returns a PySimpleGUI button with the given settings.
        
        Args:
            name (str): The text that will appear on the button.
            key (str): The string that will be returned from `window.read()` when the button is clicked.
                Should follow the format `-NAME-` for clarity.
            font_color (str): The hex color for the button's text.
            button_color (str): The hex color for the button's background.
            visible (bool): If the button is initially visible.
        """
        return sg.Button(
            name,
            key=key, 
            pad=(5, 5), 
            font=font, 
            button_color=(font_color, button_color),
            visible=visible)

    @staticmethod
    def build_layout():
        layout = []
        
        return layout

    @staticmethod
    def create_window_header():
        return sg.Frame("", [
                [sg.Frame("", [
                    [sg.Column([
                        [sg.Text(
                            "Map Information", 
                            font=("Georgia", 18, "bold"), 
                            justification="center", 
                            size=(30, 1), 
                            pad=(0, 10),
                            text_color=Layout.LIGHT_TEXT,
                            background_color=Layout.TOP_BANNER_BG,
                            relief=sg.RELIEF_RAISED,
                            border_width=2)],

                        [sg.Multiline(
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
                            pad=(5, 5))],
                    ], justification="center", element_justification="center", expand_x=True, pad=(5, 5), background_color=Layout.LIGHT_FRAME_BG)]
                ], expand_x=True, relief=sg.RELIEF_SUNKEN, border_width=2, background_color=Layout.GOLD_FRAME_LOWER, pad=(5, 5))]
            ], expand_x=True, relief=sg.RELIEF_RAISED, border_width=2, background_color=Layout.GOLD_FRAME_UPPER, pad=(15, 15))

    @staticmethod
    def create_search_column():
        return sg.Column([
            [sg.Frame("", [
                [sg.Push(background_color=Layout.LIGHT_FRAME_BG), sg.Frame("", [
                    [sg.Text("Search", font=("Georgia", 12, "bold"), text_color=Layout.LIGHT_TEXT, background_color=Layout.RED_BANNER_BG)]
                ], pad=(30, 5), background_color=Layout.RED_BANNER_BG),
                sg.Push(background_color=Layout.LIGHT_FRAME_BG)],
                [sg.Input(size=(30, 1), key="-SEARCH-", font=("Georgia", 12), enable_events=True, text_color=Layout.LIGHT_TEXT, background_color=Layout.DARK_FRAME_BG)],

                [sg.Checkbox("Exact Matches?", key="-EXACT_MATCH-", enable_events=True, font=("Georgia", 11), text_color=Layout.LIGHT_TEXT, background_color=Layout.LIGHT_FRAME_BG)],

                [sg.Push(background_color=Layout.LIGHT_FRAME_BG), sg.Frame("", [
                    [sg.Listbox(values=[], size=(30, 5), key="-RESULTS-", enable_events=True, font=("Segoe UI", 12), visible=False, text_color=Layout.LIGHT_TEXT, background_color=Layout.SUNKEN_FRAME_BG)],
                    [Layout.create_button("Go to", "-GOTO-", Layout.LIGHT_TEXT, Layout.BUTTON_BG, visible=False)],
                    [Layout.create_button("Clear", "-CLEAR-", Layout.LIGHT_TEXT, Layout.BUTTON_BG, visible=False)]
                    ], background_color=Layout.LIGHT_FRAME_BG, element_justification="center", border_width=0),
                sg.Push(background_color=Layout.LIGHT_FRAME_BG)]
            ], expand_y=True, pad=(10, 10), relief=sg.RELIEF_GROOVE, background_color=Layout.LIGHT_FRAME_BG, border_width=5, title_color=Layout.LIGHT_TEXT)]
            ], vertical_alignment="top", pad=(10, 10), expand_y=True, justification="left", background_color=Layout.DARK_FRAME_BG)

    @staticmethod
    def create_province_info_column():
        return sg.Column([
            [sg.Frame("", [
                [sg.Frame("", [
                    [sg.Column([
                        [sg.Text("Province:", font=("Georgia", 14, "bold"), text_color=Layout.LIGHT_TEXT, background_color=Layout.TOP_BANNER_BG),
                        sg.Text("", key="-INFO_NAME-", font=("Georgia", 14, "bold"), text_color=Layout.LIGHT_TEXT, background_color=Layout.TOP_BANNER_BG)],

                        [sg.Text("Capital:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.TOP_BANNER_BG),
                        sg.Text("", key="-INFO_CAPITAL-", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.TOP_BANNER_BG)],
                    ], background_color=Layout.TOP_BANNER_BG, element_justification="left", expand_x=True),

                    sg.Column([
                        [sg.Text("Area:", font=("Georgia", 14, "bold"), text_color=Layout.LIGHT_TEXT, background_color=Layout.TOP_BANNER_BG),
                        sg.Text("", key="-INFO_PROVINCE_AREA-", font=("Georgia", 14, "bold"), text_color=Layout.LIGHT_TEXT, background_color=Layout.TOP_BANNER_BG)],

                        [sg.Text("Region:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.TOP_BANNER_BG),
                        sg.Text("", key="-INFO_PROVINCE_REGION-", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.TOP_BANNER_BG)],
                    ], background_color=Layout.TOP_BANNER_BG, element_justification="right", expand_x=True)]
                ], background_color=Layout.TOP_BANNER_BG, relief=sg.RELIEF_RAISED, border_width=4, title_color=Layout.LIGHT_TEXT, pad=(5, 5), expand_x=True)],

                [sg.Frame("", [
                    [sg.Text("Development", font=("Georgia", 12, "bold"), text_color=Layout.LIGHT_TEXT, background_color=Layout.SECTION_BANNER_BG)]
                ], background_color=Layout.SECTION_BANNER_BG, pad=(5, 5), element_justification="left")],
                [sg.Frame("", [
                    [sg.Text("Tax:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.DARK_FRAME_BG),  
                    sg.Text("", key="-INFO_BASE_TAX-", font=("Georgia", 12), text_color=Layout.GREEN_TEXT, background_color=Layout.DARK_FRAME_BG, size=(10, 1)),  

                    sg.Text("Production:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.DARK_FRAME_BG),  
                    sg.Text("", key="-INFO_BASE_PRODUCTION-", font=("Georgia", 12), text_color=Layout.GREEN_TEXT, background_color=Layout.DARK_FRAME_BG, size=(10, 1)),  

                    sg.Text("Manpower:", font=("Georgia", 12), text_color=Layout.LIGHT_TEXT, background_color=Layout.DARK_FRAME_BG),  
                    sg.Text("", key="-INFO_BASE_MANPOWER-", font=("Georgia", 12), text_color=Layout.GREEN_TEXT, background_color=Layout.DARK_FRAME_BG, size=(10, 1))]
                ], background_color=Layout.DARK_FRAME_BG, pad=(5, 5), relief=sg.RELIEF_SUNKEN, border_width=3, title_color=Layout.LIGHT_TEXT),
                sg.Push(background_color=Layout.LIGHT_FRAME_BG)],  

                [sg.Frame("", [
                    [sg.Text("Demographics", font=("Georgia", 12, "bold"), text_color=Layout.LIGHT_TEXT, background_color=Layout.SECTION_BANNER_BG, pad=(1, 1))]
                ], background_color=Layout.SECTION_BANNER_BG, pad=(1, 1), element_justification="left")],
                [sg.Frame("", [
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

                ], background_color=Layout.DARK_FRAME_BG, pad=(5, 5), relief=sg.RELIEF_SUNKEN, border_width=4, expand_x=True),
                sg.Push(background_color=Layout.LIGHT_FRAME_BG)]
            ], key="-PROVINCE_INFO-", pad=(10, 10), relief=sg.RELIEF_GROOVE, background_color=Layout.LIGHT_FRAME_BG, border_width=5, title_color=Layout.LIGHT_TEXT)]
        ], vertical_alignment="top", pad=(10, 10), expand_y=True, background_color=Layout.DARK_FRAME_BG)




    @staticmethod
    def create_map_canvas(canvas_size: tuple[int, int], key: str):
        return sg.Canvas(background_color="black", size=canvas_size, key=key, pad=(10, 10))

    @staticmethod
    def create_map_modes_frame(map_modes: dict):
        return sg.Frame("", [
            [sg.Text("Map Modes", font=("Garmond", 12, "bold"), background_color=Layout.DARK_FRAME_BG, text_color=Layout.LIGHT_TEXT)],
            [Layout.create_button(mode.name, mode.value, Layout.LIGHT_TEXT, Layout.BUTTON_BG)
                for mode in map_modes],
            [Layout.create_button("Reset View", "-RESET-", Layout.LIGHT_TEXT, Layout.BUTTON_BG)]
            ], element_justification="center",
            relief=sg.RELIEF_GROOVE,
            pad=(10, 10),
            background_color=Layout.DARK_FRAME_BG,
            border_width=5,
            title_color=Layout.LIGHT_TEXT)

    @staticmethod
    def get_layout(canvas_size: tuple[int, int], map_modes: dict):
        return [
            [Layout.create_window_header()],

            [sg.Frame("", [
                [
                    Layout.create_search_column(), Layout.create_province_info_column()
                ]
            ], pad=(10, 10), relief=sg.RELIEF_GROOVE, background_color=Layout.LIGHT_FRAME_BG, border_width=5, expand_x=True)],
            
            [sg.Frame("", [
                [
                    Layout.create_map_canvas(canvas_size=canvas_size, key="-CANVAS-")
                ]
            ], background_color=Layout.LIGHT_FRAME_BG, relief=sg.RELIEF_GROOVE, pad=(10, 10), border_width=5)],

            [Layout.create_map_modes_frame(map_modes=map_modes)],

            [sg.Text("", size=(1, 1), pad=(5, 5), background_color=Layout.LIGHT_FRAME_BG)]
        ]
