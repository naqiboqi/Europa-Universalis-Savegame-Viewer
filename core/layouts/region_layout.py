"""
Layout builder for region-related UI components.

This module defines the visual layout for regions, which are composed of multiple 
areas. It handles how these higher-level geographical groupings are displayed 
in the user interface.

Classes:
    - **RegionLayout**: Builds the layout for displaying regions and their 
        constituent areas and provinces.
"""


import FreeSimpleGUI as sg

from . import constants
from . import LayoutHelper
from ..utils import IconLoader


icon_loader = IconLoader()



class RegionLayout:
    """Constructs layouts for regions by organizing their areas and the provinces 
    within them into structured UI panels.
    """

    @staticmethod
    def create_geographic_region_info_frame():
        """Creates the geographical frame section for an area.

        Returns:
            frame (Frame): The frame containing the area info.
        """
        region_name = sg.Text(
            "",
            key="-INFO_REGION_NAME-",
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="right",
            text_color=constants.LIGHT_TEXT)

        spacer_left = sg.Text(
            "", 
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="left")

        region_column = sg.Column([
            [region_name],
            [spacer_left]
        ], background_color=constants.TOP_BANNER_BG,
        element_justification="left",
        expand_x=True)

        spacer_right = sg.Text(
            "",
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="right")

        spacer_column = sg.Column([
            [spacer_right],
        ], background_color=constants.TOP_BANNER_BG,
        element_justification="left",
        expand_x=True)

        return sg.Frame("", [
            [region_column, sg.Push(background_color=constants.TOP_BANNER_BG), spacer_column]
        ], background_color=constants.TOP_BANNER_BG,
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
        area_icon = LayoutHelper.create_icon_with_border(
            icon_name="map_area",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        area_header = sg.Frame("", [
            [area_icon]
        ], background_color=constants.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(220, 40))

        development_icon = LayoutHelper.create_icon_with_border(
            icon_name="development",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        development_header = sg.Frame("", [
            [development_icon]
        ], background_color=constants.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(44, 40))

        trade_power_icon = LayoutHelper.create_icon_with_border(
            icon_name="trade_power",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_power_header = sg.Frame("", [
            [trade_power_icon]
        ], background_color=constants.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(111, 40))

        religion_icon = LayoutHelper.create_icon_with_border(
            icon_name="religion",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        religion_header = sg.Frame("", [
            [religion_icon]
        ], background_color=constants.SECTION_BANNER_BG,
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(198, 40))

        culture_icon = LayoutHelper.create_icon_with_border(
            icon_name="culture",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        culture_header = sg.Frame("", [
            [culture_icon]
        ], background_color=constants.SECTION_BANNER_BG,
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
        ], background_color=constants.SECTION_BANNER_BG, 
        pad=(0, 0))

        return sg.Frame("", 
            layout=[[icon_row]], 
            background_color=constants.SECTION_BANNER_BG,
            expand_x=True,
            pad=(0, 0), 
            relief=sg.RELIEF_SOLID)

    @staticmethod
    def create_region_areas_table():
        """Creates the table that will be used to display the an regions's provinces.
        
        Includes fields for area name, development, religion and culture.
        
        Returns:
            column (Column): The table and its header packed into a column.
        """
        table_header = RegionLayout.create_areas_table_header()

        table = sg.Table(
            values=[],
            key="-INFO_REGION_AREAS_TABLE-",
            alternating_row_color=constants.DARK_FRAME_BG,
            background_color=constants.MEDIUM_FRAME_BG,
            auto_size_columns=False,
            col_widths=[20, 4, 10, 18, 18],
            headings=["Name", "Dev.", "Trade Power", "Dominant Religion", "Dominant Culture"],
            header_background_color=constants.SECTION_BANNER_BG,
            header_relief=sg.RELIEF_SOLID,
            font=("Georgia", 12),
            text_color=constants.LIGHT_TEXT,
            hide_vertical_scroll=False,
            justification="left",
            num_rows=5,
            pad=(0, 0),
            row_height=28,
            sbar_arrow_color=constants.GOLD_FRAME_UPPER,
            sbar_background_color=constants.RED_BANNER_BG,
            sbar_trough_color=constants.GOLD_FRAME_LOWER,
            sbar_relief=sg.RELIEF_GROOVE,
            sbar_width=5)

        areas_info = sg.Frame("", [
            [table_header],
            [table]
        ], expand_x=True, pad=(0, 0))

        return sg.Column([
            [areas_info]
        ], background_color=constants.LIGHT_FRAME_BG,
        pad=(10, 0))

    @staticmethod
    def create_region_info_column():
        """Creates the region column section.
        
        This section contains the region's areas table and the regions's overall income and trade information.
        
        Returns:
            column (Column): The column containing the region info.
        """
        geographic_info_frame = RegionLayout.create_geographic_region_info_frame()

        development_label = LayoutHelper.create_text_with_frame(
            content="Development",
            content_color=constants.LIGHT_TEXT,
            frame_background_color=constants.SECTION_BANNER_BG,
            pad=(15, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        development_info_frame = LayoutHelper.create_development_info_frame(name="REGION")

        region_areas_table = RegionLayout.create_region_areas_table()

        income_info_column = LayoutHelper.create_income_column(name="REGION")
        trade_info_column = LayoutHelper.create_trade_column(name="REGION")

        area_km2_label = LayoutHelper.create_text_with_frame(
            "Area in km^2",
            content_color=constants.LIGHT_TEXT,
            frame_background_color=constants.SECTION_BANNER_BG,
            pad=(15, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        area_km2_value = LayoutHelper.create_text_with_frame(
            "",
            key="-INFO_REGION_SIZE_KM-",
            content_color=constants.LIGHT_TEXT,
            font=("Georgia", 12),
            frame_background_color=constants.SUNK_FRAME_BG,
            frame_border_width=2,
            justification="center",
            pad=((5, 15), (15, 15)),
            relief=sg.RELIEF_SUNKEN,
            size=(15, 1))

        region_info_frame = sg.Frame("", [
            [geographic_info_frame],
            [development_label, development_info_frame,
                sg.Push(background_color=constants.LIGHT_FRAME_BG),
            area_km2_label, area_km2_value],
            [region_areas_table],
            [income_info_column],
            [trade_info_column]
        ], background_color=constants.LIGHT_FRAME_BG,
        border_width=5,
        expand_x=True,
        expand_y=True,
        key="REGION_INFO_FRAME-",
        pad=(10, 10),
        relief=sg.RELIEF_GROOVE,
        size=(985, 510))

        return sg.Column([
            [region_info_frame]
        ], background_color=constants.LIGHT_FRAME_BG,
        expand_x=True,
        expand_y=True,
        key="-REGION_INFO_COLUMN-",
        pad=((5, 10), 10, 10),
        vertical_alignment="top",
        visible=False)