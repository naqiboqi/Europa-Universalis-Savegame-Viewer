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

        country_info_frame = sg.Frame("", [
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
