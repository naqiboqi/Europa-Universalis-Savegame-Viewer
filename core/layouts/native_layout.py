

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

        spacer_right = sg.Text(
            "",
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
                [spacer_right],
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
            key="-INFO_NATIVE_PROVINCE_RELIGION-",
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
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        return sg.Column([
            [demographics_frame]
        ], background_color=constants.MEDIUM_FRAME_BG, 
        expand_y=True,
        pad=(0, 10),
        vertical_alignment="top")

    @staticmethod
    def create_native_statistics_info_column():
        """Creates the statistics column section for a native/uncolonized province.

        Returns:
            column (Column): The column containing the native statistics.
        """
        native_size_label, native_size_value = LayoutHelper.create_text_with_inline_label(
            "Native size",
            text_key="-INFO_NATIVE_PROVINCE_NATIVE_SIZE-",
            expand_x=True,
            font=("Georgia", 12, "bold"),
            label_colors=(constants.LIGHT_TEXT, constants.SECTION_BANNER_BG),
            justification="right",
            text_colors=(constants.LIGHT_TEXT, constants.SECTION_BANNER_BG),
            text_field_size=(5, 1))

        native_size_icon = LayoutHelper.create_icon_with_border(
            icon_name="uprising_chance",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))

        native_size_frame = sg.Frame("", [
            [native_size_label, native_size_icon, sg.Push(constants.SECTION_BANNER_BG), native_size_value]
        ], background_color=constants.SECTION_BANNER_BG,
        border_width=2,
        pad=(10, 10),
        relief=sg.RELIEF_RIDGE,
        size=(300, 30))

        hostileness_label, hostileness_value = LayoutHelper.create_text_with_inline_label(
            "Hostileness",
            text_key="-INFO_NATIVE_PROVINCE_NATIVE_HOSTILENESS-",
            expand_x=True,
            font=("Georgia", 12, "bold"),
            label_colors=(constants.LIGHT_TEXT, constants.SECTION_BANNER_BG),
            justification="right",
            text_colors=(constants.LIGHT_TEXT, constants.SECTION_BANNER_BG),
            text_field_size=(5, 1))

        hostileness_icon = LayoutHelper.create_icon_with_border(
            icon_name="agressiveness",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))

        hostileness_frame = sg.Frame("", [
            [hostileness_label, hostileness_icon, sg.Push(constants.SECTION_BANNER_BG), hostileness_value]
        ], background_color=constants.SECTION_BANNER_BG,
        border_width=2,
        pad=(10, 10),
        relief=sg.RELIEF_RIDGE,
        size=(300, 30))

        ferocity_label, ferocity_value = LayoutHelper.create_text_with_inline_label(
            "Hostileness",
            text_key="-INFO_NATIVE_PROVINCE_NATIVE_FEROCITY-",
            expand_x=True,
            font=("Georgia", 12, "bold"),
            label_colors=(constants.LIGHT_TEXT, constants.SECTION_BANNER_BG),
            justification="right",
            text_colors=(constants.LIGHT_TEXT, constants.SECTION_BANNER_BG),
            text_field_size=(5, 1))

        ferocity_icon = LayoutHelper.create_icon_with_border(
            icon_name="ferocity",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))

        ferocity_frame = sg.Frame("", [
            [ferocity_label, ferocity_icon, sg.Push(constants.SECTION_BANNER_BG), ferocity_value]
        ], background_color=constants.SECTION_BANNER_BG,
        border_width=2,
        pad=(10, 10),
        relief=sg.RELIEF_RIDGE,
        size=(300, 30))

        native_stats_frame = sg.Frame("", [
            [native_size_frame],
            [hostileness_frame],
            [ferocity_frame]
        ], background_color=constants.MEDIUM_FRAME_BG,
        border_width=2,
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        return sg.Column([
            [native_stats_frame],
        ], background_color=constants.MEDIUM_FRAME_BG,
        expand_y=True,
        pad=((0, 0), (10, 10)), 
        vertical_alignment="top")

    @staticmethod
    def create_colonial_region_column():
        """Creates the colonial region column for a native province.
        
        Returns:
            column (Column): The column containing the colonial region information.
        """
        uncolonized_text = sg.Text(
            "Uncolonized Land.",
            text_color=constants.LIGHT_TEXT,
            background_color=constants.SUNK_FRAME_BG,
            font=("Georgia", 18, "bold"),
            justification="center",
            pad=((40, 40), (30, 30)),
            size=(100, 1))

        colonial_region_info = sg.Text(
            "Placeholder Region",
            key="-INFO_NATIVE_PROVINCE_COLONIAL_REGION-",
            background_color=constants.SUNK_FRAME_BG,
            text_color=constants.LIGHT_TEXT,
            font=("Georgia", 14),
            justification="center",
            pad=((40, 40), (40, 30)),
            size=(30, 1))

        colonial_region_frame = sg.Frame("", [
            [uncolonized_text],
            [colonial_region_info]
        ], background_color=constants.SUNK_FRAME_BG,
        border_width=3,
        element_justification="center",
        expand_y=True)

        return sg.Column([
            [colonial_region_frame]
        ], background_color=constants.DARK_FRAME_BG,
        element_justification="center",
        expand_y=True)

    @staticmethod
    def create_native_trade_goods_column():
        """Creates the trade goods column for a native province.
        
        Returns:
            column (Column): The column containing the trade good information.
        """
        trade_good_icon = LayoutHelper.create_icon_with_border(
            icon_name="",
            image_key="-INFO_NATIVE_PROVINCE_TRADE_GOOD-",
            borders=[
                (constants.GOLD_FRAME_LOWER, 2, sg.RELIEF_RIDGE),
                (constants.GOLD_FRAME_UPPER, 2, sg.RELIEF_RIDGE)],
            border_pad=(0, 5),
            image_size=(64, 64))

        trade_good_frame = sg.Frame("", [
            [sg.Push(constants.MEDIUM_FRAME_BG), trade_good_icon, sg.Push(constants.MEDIUM_FRAME_BG)],
        ], background_color=constants.MEDIUM_FRAME_BG,
        pad=(0, 0),
        relief=sg.RELIEF_FLAT)

        trade_good_column = sg.Column([
            [sg.Push(constants.MEDIUM_FRAME_BG), trade_good_frame, sg.Push(constants.MEDIUM_FRAME_BG)]
        ], background_color=constants.MEDIUM_FRAME_BG,
        pad=(15, 15),
        vertical_alignment="top")

        trade_good_name = LayoutHelper.create_text_with_frame(
            "",
            key="-INFO_NATIVE_PROVINCE_TRADE_GOOD_NAME-",
            content_color=constants.LIGHT_TEXT,
            expand_x=True,
            frame_background_color=constants.BUTTON_BG,
            justification="center",
            pad=((0, 20), (5, 5)),
            size=(15, 1),
            relief=sg.RELIEF_RIDGE)

        trade_info_frame = sg.Frame("", [
            [trade_good_column, trade_good_name]
        ], background_color=constants.MEDIUM_FRAME_BG,
        border_width=2,
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        return sg.Column([
            [trade_info_frame],
        ], background_color=constants.MEDIUM_FRAME_BG,
        pad=(10, 10),
        vertical_alignment="center")

    @staticmethod
    def create_native_info_column():
        """Creates the native province column section.
        
        This section contains the province's trade, military, and demographic information.
        
        Returns:
            column (Column): The column containing the province info.
        """
        native_stat_column = NativeLayout.create_native_statistics_info_column()
        demographic_info_column = NativeLayout.create_demographic_info_column()

        development_label = LayoutHelper.create_text_with_frame(
            content="Development",
            content_color=constants.LIGHT_TEXT,
            frame_background_color=constants.SECTION_BANNER_BG,
            pad=(20, 15),
            relief=sg.RELIEF_SOLID,
            justification="center")
        development_info_frame = LayoutHelper.create_development_info_frame(name="NATIVE_PROVINCE")

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

        trade_header_label = sg.Text(
            "Trade", 
            background_color=constants.SECTION_BANNER_BG,
            font=("Georgia", 12, "bold"),
            text_color=constants.LIGHT_TEXT)
        trade_icon = LayoutHelper.create_icon_with_border(
            icon_name="trade",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_header_frame = sg.Frame("", [
            [trade_header_label, trade_icon, sg.Push(background_color=constants.SECTION_BANNER_BG)]
        ], background_color=constants.SECTION_BANNER_BG,
        expand_x=True,
        pad=(0, 0),
        relief=sg.RELIEF_SOLID,
        vertical_alignment="top")

        trade_good_column = NativeLayout.create_native_trade_goods_column()

        trade_column = sg.Column([
            [trade_header_frame],
            [trade_good_column]
        ], background_color=constants.LIGHT_FRAME_BG,
        expand_x=True,
        pad=(10, 10),
        vertical_alignment="top")

        native_info_frame = sg.Frame("", [
            [geographic_info_frame],
            [development_label, development_info_frame,
                sg.Push(background_color=constants.LIGHT_FRAME_BG),
            area_km2_label, area_km2_value],
            [colonial_region_column],
            [native_stat_column, demographic_info_column, trade_column]
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
