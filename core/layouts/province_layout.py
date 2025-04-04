"""
Layout builder for province-related UI components.

This module defines the visual layout and organization of province data 
in the user interface. It uses helpers and standardized styling to ensure 
consistency across province displays.

Classes:
    - **ProvinceLayout**: Responsible for constructing layouts that represent 
        individual provinces and province-related data.
"""


import FreeSimpleGUI as sg

from . import constants
from . import LayoutHelper
from ..utils import IconLoader


icon_loader = IconLoader()


class ProvinceLayout:
    """Builds UI layouts for displaying province data, including name, type, 
    ownership, development, trade goods, and other relevant attributes.
    """

    @staticmethod
    def create_geographic_province_info_frame():
        """Creates the geographical frame section for a province.

        Returns:
            frame (Frame): The frame containing the province info.
        """
        province_name = sg.Text(
            "",
            key="-INFO_PROVINCE_NAME-",
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="left",
            text_color=constants.LIGHT_TEXT)

        capital_name = sg.Text(
            "",
            key="-INFO_PROVINCE_CAPITAL-",
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="left",
            text_color=constants.LIGHT_TEXT)

        area_name = sg.Text(
            "",
            key="-INFO_PROVINCE_AREA_NAME-",
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 14),
            justification="right",
            text_color=constants.LIGHT_TEXT)

        region_name = sg.Text(
            "",
            key="-INFO_PROVINCE_REGION_NAME-",
            background_color=constants.TOP_BANNER_BG,
            font=("Georgia", 12),
            justification="right",
            text_color=constants.LIGHT_TEXT)

        return sg.Frame("", [
            [sg.Column([
                [province_name],
                [capital_name]
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
        """Creates the demographics column section for a province.

        Returns:
            column (Column): The column containing the demographic info.
        """
        cored_by_info = LayoutHelper.create_text_with_frame(
            "",
            content_color=constants.GREEN_TEXT,
            expand_x=True,
            font=("Georgia", 12),
            frame_background_color=constants.SUNK_FRAME_BG,
            justification="left",
            key="-INFO_PROVINCE_OWNER-",
            relief=sg.RELIEF_FLAT,
            size=(20, 1))

        culture_info = LayoutHelper.create_text_with_frame(
            "",
            content_color=constants.GREEN_TEXT,
            expand_x=True,
            font=("Georgia", 12),
            frame_background_color=constants.SUNK_FRAME_BG,
            justification="left",
            key="-INFO_PROVINCE_CULTURE-",
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
                "Cored By",
                background_color=constants.MEDIUM_FRAME_BG,
                font=("Georgia", 12), 
                text_color=constants.LIGHT_TEXT)],
            [cored_by_info],

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

        demographics_header_label = sg.Text(
            "Demographics", 
            background_color=constants.SECTION_BANNER_BG,
            font=("Georgia", 12, "bold"),
            text_color=constants.LIGHT_TEXT)
        demographics_icon = LayoutHelper.create_icon_with_border(
            icon_name="demographics",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        demographics_header_frame = sg.Frame("", [
            [demographics_header_label, demographics_icon, sg.Push(background_color=constants.SECTION_BANNER_BG)]
        ], background_color=constants.SECTION_BANNER_BG, 
        expand_x=True, 
        pad=((0, 0), (0, 15)),
        relief=sg.RELIEF_SOLID, 
        vertical_alignment="top")

        return sg.Column([
            [demographics_header_frame],
            [demographics_frame]
        ], background_color=constants.LIGHT_FRAME_BG, 
        expand_y=True, 
        pad=(0, 10), 
        vertical_alignment="top")

    @staticmethod
    def create_trade_info_column():
        """Creates the trade column section for a province.

        Returns:
            column (Column): The column containing the trade info.
        """
        trade_value_icon = LayoutHelper.create_icon_with_border(
            icon_name="trade_value_income",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_value_label, trade_value = LayoutHelper.create_text_with_inline_label(
            "Trade Value",
            text_key="-INFO_PROVINCE_TRADE_VALUE-",
            label_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(6, 1),
            expand_x=True)

        trade_power_icon = LayoutHelper.create_icon_with_border(
            icon_name="trade_power",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_power_label, trade_power_field = LayoutHelper.create_text_with_inline_label(
            "Trade Power",
            text_key="-INFO_PROVINCE_TRADE_POWER-", 
            label_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(6, 1),
            expand_x=True)

        goods_produced_icon = LayoutHelper.create_icon_with_border(
            icon_name="goods_produced",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        goods_produced_label, goods_produced_field = LayoutHelper.create_text_with_inline_label(
            "Goods Produced",
            text_key="-INFO_PROVINCE_GOODS_PRODUCED-",
            label_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(6, 1),
            expand_x=True)

        trade_info_frame = sg.Frame("", [
            [trade_value_label, trade_value_icon, trade_value],
            [trade_power_label, trade_power_icon, trade_power_field],
            [goods_produced_label, goods_produced_icon, goods_produced_field],
        ], background_color=constants.DARK_FRAME_BG,
        border_width=3,
        expand_x=True,  
        pad=(10, 5), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        trade_info_column = sg.Column([
            [trade_info_frame]
        ], background_color=constants.LIGHT_FRAME_BG, pad=(5, 5), vertical_alignment="center")

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
        relief=sg.RELIEF_SOLID)

        home_trade_node = LayoutHelper.create_text_with_frame(
            "",
            key="-INFO_PROVINCE_HOME_NODE-",
            content_color=constants.LIGHT_TEXT,
            frame_background_color=constants.BUTTON_BG,
            justification="center",
            pad=(10, 10),
            size=(15, 1),
            relief=sg.RELIEF_FLAT)

        estuary_icon = LayoutHelper.create_icon_with_border(
            icon_name="",
            image_key="-INFO_PROVINCE_HOME_NODE-",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(10, 5),
            image_size=(28, 28))

        goods_modifier_icon = LayoutHelper.create_icon_with_border(
            icon_name="",
            image_key="-INFO_PROVINCE_GOODS_PRODUCED_MODIFIER-",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))

        inland_trade_icon = LayoutHelper.create_icon_with_border(
            icon_name="",
            image_key="-INFO_PROVINCE_INLAND_TRADE_CENTER-",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))

        center_of_trade_icon = LayoutHelper.create_icon_with_border(
            icon_name="",
            image_key="-INFO_PROVINCE_CENTER_OF_TRADE-",
            borders=[
                (constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE),
                (constants.GOLD_FRAME_UPPER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(84, 40))

        goods_and_trade_modifiers = sg.Frame("", [
            [estuary_icon, inland_trade_icon, goods_modifier_icon, center_of_trade_icon]  
        ], background_color=constants.SUNK_FRAME_BG, 
        border_width=0,
        element_justification="center", 
        expand_x=True,
        pad=(5, 5))

        home_trade_icon = LayoutHelper.create_icon_with_border(
            icon_name="trade_office",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(10, 10),
            image_size=(40, 40))

        trade_influences_frame = sg.Frame("", [
            [home_trade_icon, home_trade_node],
            [goods_and_trade_modifiers]
        ], background_color=constants.DARK_FRAME_BG,
        pad=(5, 5),
        relief=sg.RELIEF_SUNKEN)

        trade_influences_column = sg.Column([
            [trade_influences_frame]
        ], background_color=constants.LIGHT_FRAME_BG, pad=(5, 5), vertical_alignment="center")

        trade_good_icon = LayoutHelper.create_icon_with_border(
            icon_name="",
            image_key="-INFO_PROVINCE_TRADE_GOOD-",
            borders=[
                (constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE),
                (constants.GOLD_FRAME_UPPER, 1, sg.RELIEF_RIDGE)],
            border_pad=(0, 5),
            image_size=(64, 64))
        trade_good_value = sg.Text(
            "",
            key="-INFO_PROVINCE_TRADE_GOOD_PRICE-",
            background_color=constants.DARK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            justification="center",
            pad=(0, 0),
            size=(4, 1),
            text_color=constants.LIGHT_TEXT)

        ducat_income_icon = LayoutHelper.create_icon_with_border(
            "income",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(0, 0),
            image_size=(24, 24))

        value_frame = sg.Frame("", [
            [trade_good_value, ducat_income_icon]
        ], background_color=constants.DARK_FRAME_BG, 
        relief=sg.RELIEF_FLAT,
        vertical_alignment="center")

        trade_good_frame = sg.Frame("", [
            [sg.Push(constants.DARK_FRAME_BG), trade_good_icon, sg.Push(constants.DARK_FRAME_BG)],
            [sg.Push(constants.DARK_FRAME_BG), value_frame, sg.Push(constants.DARK_FRAME_BG)]
        ], background_color=constants.DARK_FRAME_BG,
        pad=(5, 5),
        relief=sg.RELIEF_FLAT)

        trade_good_column = sg.Column([
            [trade_good_frame]
        ], background_color=constants.LIGHT_FRAME_BG, pad=(0, 0), vertical_alignment="center")

        return sg.Column([
            [trade_header_frame],
            [trade_info_column, trade_influences_column, trade_good_column],
        ], background_color=constants.LIGHT_FRAME_BG, 
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
        manpower_icon = LayoutHelper.create_icon_with_border(
            icon_name="base_manpower",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        manpower_label, manpower_value = LayoutHelper.create_text_with_inline_label(
            "Manpower",
            text_key="-INFO_PROVINCE_LOCAL_MANPOWER-",
            expand_x=True,
            label_colors=(constants.LIGHT_TEXT, constants.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(5, 1))

        sailors_icon = LayoutHelper.create_icon_with_border(
            icon_name="sailors",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        sailors_label, sailors_value = LayoutHelper.create_text_with_inline_label(
            "Sailors",
            text_key="-INFO_PROVINCE_LOCAL_SAILORS-",
            expand_x=True,
            label_colors=(constants.LIGHT_TEXT, constants.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(5, 1))

        troops_info_column = sg.Column([
            [manpower_label, manpower_icon, manpower_value, 
            sailors_icon, sailors_label, sailors_value]
        ], background_color=constants.MEDIUM_FRAME_BG)

        garrison_icon = LayoutHelper.create_icon_with_border(
            icon_name="fort_defense",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        garrison_label, garrison_value = LayoutHelper.create_text_with_inline_label(
            "Garrison",
            text_key="-INFO_PROVINCE_GARRISON_SIZE-",
            label_colors=(constants.LIGHT_TEXT, constants.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(5, 1))

        defense_info_column = sg.Column([
            [garrison_label, garrison_icon, garrison_value],
        ], background_color=constants.MEDIUM_FRAME_BG, pad=(5, 5))

        military_info_frame = sg.Frame("", [
            [troops_info_column, defense_info_column]
        ], background_color=constants.MEDIUM_FRAME_BG,
        element_justification="center",
        expand_x=True,
        relief=sg.RELIEF_SUNKEN)

        military_label = sg.Text(
            "Military", 
            background_color=constants.SECTION_BANNER_BG,
            font=("Georgia", 12, "bold"),
            text_color=constants.LIGHT_TEXT)
        military_icon = LayoutHelper.create_icon_with_border(
            icon_name="military",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        military_header_frame = sg.Frame("", [
            [military_label, military_icon, sg.Push(background_color=constants.SECTION_BANNER_BG)]
        ], background_color=constants.SECTION_BANNER_BG, 
        expand_x=True, 
        pad=((10, 10), (0, 10)),
        relief=sg.RELIEF_SOLID)

        fort_level = sg.Image("", key="-INFO_PROVINCE_FORT_LEVEL-", )
        fort_level = LayoutHelper.create_icon_with_border(
            "",
            image_key="-INFO_PROVINCE_FORT_LEVEL-",
            borders=[(constants.GOLD_FRAME_UPPER, 1, sg.RELIEF_RIDGE)],
            border_pad=(10, 10),
            image_size=(48, 48))

        return sg.Column([
            [military_header_frame],
            [military_info_frame, fort_level]
        ], background_color=constants.LIGHT_FRAME_BG, 
        expand_x=True, 
        pad=(0, 0), 
        vertical_alignment="top")

    @staticmethod
    def create_province_info_column():
        """Creates the province column section.
        
        This section contains the province's trade, military, and demographic information.
        
        Returns:
            column (Column): The column containing the province info.
        """
        development_info_frame = LayoutHelper.create_development_info_frame(name="PROVINCE")
        demographic_info_column = ProvinceLayout.create_demographic_info_column()

        trade_and_mil_column = sg.Column([
            [ProvinceLayout.create_trade_info_column()],
            [ProvinceLayout.create_military_info_column()]
        ], background_color=constants.LIGHT_FRAME_BG, expand_x=True, pad=(5, 5))

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
            key="-INFO_PROVINCE_SIZE_KM-",
            content_color=constants.LIGHT_TEXT,
            font=("Georgia", 12),
            frame_background_color=constants.SUNK_FRAME_BG,
            frame_border_width=2,
            justification="center",
            pad=((5, 15), (15, 15)),
            relief=sg.RELIEF_SUNKEN,
            size=(15, 1))

        geographic_info_frame = ProvinceLayout.create_geographic_province_info_frame()
        province_info_frame = sg.Frame("", [
            [geographic_info_frame],
            [development_label, development_info_frame,
                sg.Push(background_color=constants.LIGHT_FRAME_BG),
            area_km2_label, area_km2_value],
            [demographic_info_column, trade_and_mil_column]
        ], background_color=constants.LIGHT_FRAME_BG, 
        border_width=5,
        expand_x=True,
        expand_y=True,
        key="-PROVINCE_INFO_FRAME-",
        pad=(10, 10),
        size=(985, 510),
        relief=sg.RELIEF_GROOVE)

        return sg.Column([
            [province_info_frame]
        ], background_color=constants.LIGHT_FRAME_BG,
        expand_x=True,
        expand_y=True,
        key="-PROVINCE_INFO_COLUMN-",
        pad=((5, 10), (10, 10)),
        vertical_alignment="top")
