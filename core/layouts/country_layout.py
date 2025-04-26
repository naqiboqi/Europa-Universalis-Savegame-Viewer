"""
Layout builder for country-related UI components.

This module defines how country data is visually structured and rendered within 
the Europa Universalis UI.

Classes:
    - **CountryLayout**: Builds and manages the layout for displaying countries and 
        
"""


import FreeSimpleGUI as sg

from . import constants
from . import LayoutHelper
from ..utils import IconLoader


icon_loader = IconLoader()


class CountryLayout:
    """The layout building for displaying area information."""
    
    @staticmethod
    def create_country_header_frame():
        """Creates the header frame for a country.

        Returns:
            frame (Frame): The frame containing the country header.
        """
        country_name = sg.Text(
            "",
            key="-INFO_COUNTRY_NAME-",
            background_color=constants.RED_BANNER_BG,
            font=("Georgia", 14),
            justification="left",
            text_color=constants.LIGHT_TEXT)

        government_name = sg.Text(
            "", 
            key="-INFO_COUNTRY_GOVERNMENT_NAME-",
            background_color=constants.RED_BANNER_BG,
            font=("Georgia", 12),
            justification="left",
            text_color=constants.LIGHT_TEXT)

        spacer_right_1 = sg.Text(
            "",
            background_color=constants.RED_BANNER_BG,
            font=("Georgia", 14),
            justification="right")

        spacer_right_2 = sg.Text(
            "",
            background_color=constants.RED_BANNER_BG,
            font=("Georgia", 12),
            justification="right")

        left_column = sg.Column([
                [country_name],
                [government_name]
            ], background_color=constants.RED_BANNER_BG,
            element_justification="left",
            expand_x=True)

        right_column = sg.Column([
                [spacer_right_1],
                [spacer_right_2]
            ], background_color=constants.RED_BANNER_BG,
            element_justification="right",
            expand_x=True)

        return sg.Frame("", [
            [left_column, sg.Push(background_color=constants.RED_BANNER_BG), right_column]
        ], background_color=constants.RED_BANNER_BG,
        border_width=4,
        expand_x=True,
        pad=(5, 5),
        relief=sg.RELIEF_RAISED,
        vertical_alignment="center")

    @staticmethod
    def create_country_info_column():
        """Creates the country column section.
        
        Returns:
            column (Column): The column containing the country info.
        """
        development_label = LayoutHelper.create_text_with_frame(
            content="Development",
            content_color=constants.LIGHT_TEXT,
            frame_background_color=constants.SECTION_BANNER_BG,
            pad=(15, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        development_info_frame = LayoutHelper.create_development_info_frame(name="COUNTRY")

        area_km2_label = LayoutHelper.create_text_with_frame(
            "Area in km^2",
            content_color=constants.LIGHT_TEXT,
            frame_background_color=constants.SECTION_BANNER_BG,
            pad=(15, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        area_km2_value = LayoutHelper.create_text_with_frame(
            "",
            key="-INFO_COUNTRY_SIZE_KM-",
            content_color=constants.LIGHT_TEXT,
            font=("Georgia", 12),
            frame_background_color=constants.SUNK_FRAME_BG,
            frame_border_width=2,
            justification="center",
            pad=((5, 15), (15, 15)),
            relief=sg.RELIEF_SUNKEN,
            size=(15, 1))

        header = CountryLayout.create_country_header_frame()

        country_info_frame = sg.Frame("", [
            [header],
            [development_label, development_info_frame,
                sg.Push(background_color=constants.LIGHT_FRAME_BG),
            area_km2_label, area_km2_value],
        ], background_color=constants.LIGHT_FRAME_BG,
        border_width=5,
        expand_x=True,
        expand_y=True,
        key="-COUNTRY_INFO_FRAME-",
        pad=(10, 10),
        relief=sg.RELIEF_GROOVE,
        size=(1010, 575))

        return sg.Column([
            [country_info_frame]
        ], background_color=constants.LIGHT_FRAME_BG,
        expand_x=True,
        expand_y=True,
        key="-COUNTRY_INFO_COLUMN-",
        pad=((5, 10), 10, 10),
        scrollable=True,
        sbar_arrow_color=constants.GOLD_FRAME_UPPER,
        sbar_background_color=constants.RED_BANNER_BG,
        sbar_trough_color=constants.GOLD_FRAME_LOWER,
        sbar_relief=sg.RELIEF_GROOVE,
        sbar_width=5,
        vertical_scroll_only=True,
        vertical_alignment="top",
        visible=False)
