

import FreeSimpleGUI as sg

from . import constants
from . import LayoutHelper
from ..utils import IconLoader


icon_loader = IconLoader()


class NativeLayout:
    """Builds UI layouts for displaying native province data, including name, type, 
    culture, religion, development, trade goods,
    """
    
    @staticmethod
    def create_geographic_native_info_frame():
        """Creates the geographical frame section for a native province.

        Returns:
            frame (Frame): The frame containing the province info.
        """
        province_name = sg.Text(
            "",
            key="-INFO_NATIVE_PROVINCE_NAME-",
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="left",
            text_color=constants.LIGHT_TEXT)

        spacer_left = sg.Text(
            "",
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="left",
            text_color=constants.LIGHT_TEXT)

        area_name = sg.Text(
            "",
            key="-INFO_NATIVE_PROVINCE_AREA_NAME-",
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="right",
            text_color=constants.LIGHT_TEXT)

        region_name = sg.Text(
            "",
            key="-INFO_NATIVE_PROVINCE_REGION_NAME-",
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="right",
            text_color=constants.LIGHT_TEXT)

        return sg.Frame("", [
            [sg.Column([
                [province_name],
                [spacer_left]
            ], background_color=constants.TOP_BANNER_BG,
            element_justification="left", 
            expand_x=True),

            sg.Column([
                [area_name],
                [region_name],
            ], background_color=constants.TOP_BANNER_BG, 
            element_justification="right", 
            expand_x=True)]
        ], background_color=constants.TOP_BANNER_BG, 
        border_width=4, 
        expand_x=True,
        pad=(5, 5),
        relief=sg.RELIEF_RAISED, 
        vertical_alignment="center")

    @staticmethod
    def create_demographic_info_column():
        """Creates the demographics column section for a native province.

        Returns:
            column (Column): The column containing the demographic info.
        """
        culture_info = LayoutHelper.create_text_with_frame(
            "",
            content_color=constants.GREEN_TEXT,
            expand_x=True,
            font=("Georgia", 12),
            frame_background_color=constants.SUNK_FRAME_BG,
            justification="left",
            key="-INFO_NATIVE_PROVINCE_CULTURE-",
            relief=sg.RELIEF_FLAT,
            size=(20, 1))

        religion_info = LayoutHelper.create_text_with_frame(
            "",
            content_color=constants.GREEN_TEXT,
            expand_x=True,
            font=("Georgia", 12),
            frame_background_color=constants.SUNK_FRAME_BG,
            justification="left",
            key="-INFO_PROVINCE_RELIGION-",
            relief=sg.RELIEF_FLAT,
            size=(20, 1))

        demographics_frame = sg.Frame("", [
            [sg.Text(
                "Culture", 
                background_color=constants.MEDIUM_FRAME_BG,
                font=("Georgia", 12), 
                text_color=constants.LIGHT_TEXT)],
            [culture_info],

            [sg.Text(
                "Religion", 
                background_color=constants.MEDIUM_FRAME_BG,
                font=("Georgia", 12), 
                text_color=constants.LIGHT_TEXT)],
            [religion_info]
        ], background_color=constants.DARK_FRAME_BG,
        expand_y=True,
        pad=(0, 0), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        return sg.Column([
            [demographics_frame]
        ], background_color=constants.MEDIUM_FRAME_BG, 
        expand_y=True, 
        pad=(10, 10),
        vertical_alignment="top")

    @staticmethod
    def create_native_statistics_info_column():
        """Creates the demographics column section for a province.

        Returns:
            column (Column): The column containing the demographic info.
        """
        native_size_info = LayoutHelper.create_text_with_frame(
            "",
            content_color=constants.LIGHT_TEXT,
            expand_x=True,
            font=("Georgia", 12),
            frame_background_color=constants.SUNK_FRAME_BG,
            justification="left",
            key="-INFO_NATIVE_PROVINCE_NATIVE_SIZE-",
            relief=sg.RELIEF_FLAT,
            size=(20, 1))

        hostile_info = LayoutHelper.create_text_with_frame(
            "",
            content_color=constants.LIGHT_TEXT,
            expand_x=True,
            font=("Georgia", 12),
            frame_background_color=constants.SUNK_FRAME_BG,
            justification="left",
            key="-INFO_NATIVE_PROVINCE_NATIVE_HOSTILENESS-",
            relief=sg.RELIEF_FLAT,
            size=(20, 1))

        native_stats_frame = sg.Frame("", [
            [sg.Text(
                "Native Size",
                background_color=constants.MEDIUM_FRAME_BG,
                font=("Georgia", 12), 
                text_color=constants.LIGHT_TEXT)],
            [native_size_info],

            [sg.Text(
                "Hostileness", 
                background_color=constants.MEDIUM_FRAME_BG,
                font=("Georgia", 12), 
                text_color=constants.LIGHT_TEXT)],
            [hostile_info],
        ], background_color=constants.DARK_FRAME_BG, 
        expand_y=True,
        pad=(0, 0), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        return sg.Column([
            [native_stats_frame]
        ], background_color=constants.LIGHT_FRAME_BG, 
        expand_y=True, 
        pad=(0, 10), 
        vertical_alignment="top")

    @staticmethod
    def create_colonial_region_column():
        """Creates the colonial region column for a native province."""
        uncolonized_text = sg.Text(
            "Uncolonized Land",
            text_color=constants.LIGHT_TEXT,
            background_color=constants.SUNK_FRAME_BG,
            font=("Georgia", 18, "bold"),
            justification="center",
            pad=((40, 40), (30, 20)),
            size=(100, 1))

        colonial_region_info = sg.Text(
            "Placeholder Region",
            key="-INFO_NATIVE_PROVINCE_COLONIAL_REGION-",
            background_color=constants.SUNK_FRAME_BG,
            text_color=constants.LIGHT_TEXT,
            font=("Georgia", 14),
            justification="center",
            pad=((40, 40), (20, 30)),
            size=(30, 1))

        colonial_region_frame = sg.Frame("", [
            [uncolonized_text],
            [colonial_region_info]
        ], background_color=constants.SUNK_FRAME_BG,
        border_width=2,
        element_justification="center")

        return sg.Column([
            [colonial_region_frame]
        ], background_color=constants.DARK_FRAME_BG,
        element_justification="center")

    @staticmethod
    def create_native_goods():
        trade_good_icon = LayoutHelper.create_icon_with_border(
            icon_name="",
            image_key="-INFO_NATIVE_PROVINCE_TRADE_GOOD-",
            borders=[
                (constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE),
                (constants.GOLD_FRAME_UPPER, 1, sg.RELIEF_RIDGE)],
            border_pad=(0, 5),
            image_size=(64, 64))

    @staticmethod
    def create_native_info_column():
        """Creates the native province column section.
        
        This section contains the province's trade, military, and demographic information.
        
        Returns:
            column (Column): The column containing the province info.
        """
        development_info_frame = LayoutHelper.create_development_info_frame(name="NATIVE")
        native_stat_column = NativeLayout.create_native_statistics_info_column()
        demographic_info_column = NativeLayout.create_demographic_info_column()

        development_label = LayoutHelper.create_text_with_frame(
            content="Development",
            content_color=constants.LIGHT_TEXT,
            frame_background_color=constants.SECTION_BANNER_BG,
            pad=(20, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")

        area_km2_label = LayoutHelper.create_text_with_frame(
            "Area in km^2",
            content_color=constants.LIGHT_TEXT,
            frame_background_color=constants.SECTION_BANNER_BG,
            pad=(15, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        area_km2_value = LayoutHelper.create_text_with_frame(
            "",
            key="-INFO_NATIVE_PROVINCE_SIZE_KM-",
            content_color=constants.LIGHT_TEXT,
            font=("Georgia", 12),
            frame_background_color=constants.SUNK_FRAME_BG,
            frame_border_width=2,
            justification="center",
            pad=((5, 15), (15, 15)),
            relief=sg.RELIEF_SUNKEN,
            size=(15, 1))

        colonial_region_column = NativeLayout.create_colonial_region_column()

        geographic_info_frame = NativeLayout.create_geographic_native_info_frame()
        native_info_frame = sg.Frame("", [
            [geographic_info_frame],
            [development_label, development_info_frame,
                sg.Push(background_color=constants.LIGHT_FRAME_BG),
            area_km2_label, area_km2_value],
            [colonial_region_column],
            [demographic_info_column, native_stat_column]
        ], background_color=constants.LIGHT_FRAME_BG, 
        border_width=5,
        expand_x=True,
        expand_y=True,
        key="-NATIVE_PROVINCE_INFO_FRAME-",
        pad=(10, 10),
        relief=sg.RELIEF_GROOVE,
        size=(1010, 575))

        return sg.Column([
            [native_info_frame]
        ], background_color=constants.LIGHT_FRAME_BG,
        expand_x=True,
        expand_y=True,
        key="-NATIVE_PROVINCE_INFO_COLUMN-",
        pad=((5, 10), (10, 10)),
        scrollable=True,
        sbar_arrow_color=constants.GOLD_FRAME_UPPER,
        sbar_background_color=constants.RED_BANNER_BG,
        sbar_trough_color=constants.GOLD_FRAME_LOWER,
        sbar_relief=sg.RELIEF_GROOVE,
        sbar_width=5,
        vertical_scroll_only=True,
        vertical_alignment="top",
        visible=False)