"""
Layout builder for area-related UI components.

This module defines how area data is visually structured and rendered within 
the Europa Universalis UI. It organizes grouped province data under trade node labels.

Classes:
    - **TradeNodeLayout**: Builds and manages the layout for displaying trade nodes and 
        the provinces contained within them.
"""


import FreeSimpleGUI as sg
import matplotlib.pyplot as plt

from io import BytesIO
from . import constants
from . import LayoutHelper
from .elements import SortableTable
from ..utils import IconLoader


icon_loader = IconLoader()



class TradeNodeLayout:
    """Layout builder for displaying trade node information."""

    @staticmethod
    def create_trade_node_header():
        trade_node_name = LayoutHelper.create_text_with_frame(
            "",
            key="-INFO_TRADE_NODE_NAME-",
            content_color=constants.LIGHT_TEXT,
            font=("Georgia", 16),
            frame_background_color=constants.SECTION_BANNER_BG,
            justification="center",
            pad=((15, 15), (10, 5)),
            relief=sg.RELIEF_RIDGE,
            size=(50, 1),)

        trade_node_region_name = LayoutHelper.create_text_with_frame(
            "",
            key="-INFO_TRADE_NODE_REGION_NAME-",
            content_color=constants.LIGHT_TEXT,
            font=("Georgia", 12),
            frame_background_color=constants.DARK_FRAME_BG,
            justification="center",
            pad=(0, 0),
            relief=sg.RELIEF_RIDGE,
            size=(35, 1))

        region_header = LayoutHelper.add_border(
            layout=[[trade_node_region_name]],
            borders=[
                (constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE),
                (constants.GOLD_FRAME_UPPER, 1, sg.RELIEF_RIDGE)],
            pad=(5, 5))

        return sg.Column([
            [trade_node_name],
            [region_header]
        ], background_color=constants.LIGHT_FRAME_BG,
        element_justification="center",
        expand_x=True)

    @staticmethod
    def create_trade_node_ships_column():
        """Creates the column for the trade node's ship information.
        
        Returns:
            column (Column): The column containing the ship information.
        """
        privateer_icon = LayoutHelper.create_icon_with_border(
            icon_name="blockade",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))

        privateer_efficiency = sg.Text(
            "",
            key="-INFO_TRADE_NODE_PRIVATEER_EFFICIENCY-",
            background_color=constants.SUNK_FRAME_BG,
            font=("Georgia", 12),
            justification="right",
            text_color=constants.GREEN_TEXT,
            size=(10, 1))

        privateer_frame = sg.Frame("", [
            [privateer_icon, privateer_efficiency]
        ], background_color=constants.SUNK_FRAME_BG,
        border_width=0)

        light_ship_icon = LayoutHelper.create_icon_with_border(
            icon_name="light_ship",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))

        num_light_ships = sg.Text(
            "",
            key="-INFO_TRADE_NODE_NUM_LIGHT_SHIPS-",
            background_color=constants.SUNK_FRAME_BG,
            font=("Georgia", 12),
            justification="right",
            text_color=constants.LIGHT_TEXT,
            size=(10, 1))

        light_ships_frame = sg.Frame("", [
            [light_ship_icon, num_light_ships]
        ], background_color=constants.SUNK_FRAME_BG,
        border_width=0)

        spacer = sg.Frame("", [[]], 
        background_color=constants.DARK_FRAME_BG, 
        border_width=0, 
        expand_x=True, 
        expand_y=True)

        return sg.Column([
            [spacer],
            [privateer_frame, light_ships_frame]
        ], background_color=constants.DARK_FRAME_BG,
        expand_y=True,
        pad=((5, 5), (10, 10)))

    @staticmethod
    def create_trade_node_value_column():
        """Creates the column for the trade node's income values.
        
        Returns:
            column (Column): The column containing the income information.
        """
        incoming_label, incoming_value = LayoutHelper.create_text_with_inline_label(
            "Incoming:",
            text_key="-INFO_TRADE_NODE_INCOMING_VALUE-",
            label_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            text_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            text_field_size=(15, 1),
            expand_x=True,
            font=("Georgia", 12),
            justification="right")

        local_lable, local_value = LayoutHelper.create_text_with_inline_label(
            "Local:",
            text_key="-INFO_TRADE_NODE_LOCAL_VALUE-",
            label_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            text_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            text_field_size=(15, 1),
            expand_x=True,
            font=("Georgia", 12),
            justification="right")

        outgoing_label, outgoing_value = LayoutHelper.create_text_with_inline_label(
            "Outgoing:",
            text_key="-INFO_TRADE_NODE_OUTGOING_VALUE-",
            label_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            text_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            text_field_size=(15, 1),
            expand_x=True,
            font=("Georgia", 12),
            justification="right")

        total_label, total_value = LayoutHelper.create_text_with_inline_label(
            "Total:",
            text_key="-INFO_TRADE_NODE_TOTAL_REMAINING_VALUE-",
            label_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            text_colors=(constants.LIGHT_TEXT, constants.DARK_FRAME_BG),
            text_field_size=(15, 1),
            expand_x=True,
            font=("Georgia", 12),
            justification="right")

        # PySimpleGUI doesn't allow reusing any elements...
        value_sep_1 = sg.HorizontalSeparator(constants.GOLD_FRAME_UPPER, pad=(5, 5))
        value_sep_2 = sg.HorizontalSeparator(constants.GOLD_FRAME_UPPER, pad=(5, 5))
        value_sep_3 = sg.HorizontalSeparator(constants.GOLD_FRAME_UPPER, pad=(5, 5))
        value_sep_4 = sg.HorizontalSeparator(constants.GOLD_FRAME_UPPER, pad=(5, 5))
        value_sep_5 = sg.HorizontalSeparator(constants.GOLD_FRAME_UPPER, pad=(5, 5))
        node_values_frame = sg.Frame("", [
            [value_sep_1],
            [incoming_label, incoming_value],
            [value_sep_2],
            [local_lable, local_value],
            [value_sep_3],
            [outgoing_label, outgoing_value],
            [value_sep_4],
            [total_label, total_value],
            [value_sep_5]
        ], background_color=constants.DARK_FRAME_BG,
        border_width=0)

        return sg.Column([
            [node_values_frame]
        ], background_color=constants.DARK_FRAME_BG,
        pad=((5, 5), (10, 10)))

    @staticmethod
    def create_trade_node_chart_column():
        retained_value_label = sg.Text(
            "Retained Value",
            background_color=constants.DARK_FRAME_BG,
            font=("Georgia", 14),
            justification="center",
            expand_x=True,
            size=(15, 1),
            text_color=constants.LIGHT_TEXT)
        retained_value_graph_image = sg.Image(
            filename=icon_loader.get_icon(""), 
            key="-INFO_TRADE_NODE_RETAINED_PIE-",
            size=(100, 100))

        retained_value_frame = sg.Frame("", [
            [retained_value_label],
            [sg.Push(), retained_value_graph_image, sg.Push()]
        ], background_color=constants.DARK_FRAME_BG,
        border_width=0,
        element_justification="center",
        expand_x=True)

        trade_power_label = sg.Text(
            "Trade Power",
            background_color=constants.DARK_FRAME_BG,
            font=("Georgia", 14),
            justification="center",
            expand_x=True,
            size=(15, 1),
            text_color=constants.LIGHT_TEXT)
        trade_power_graph_image = sg.Image(
            filename=icon_loader.get_icon(""), 
            key="-INFO_TRADE_NODE_RETAINED_PIE-",
            size=(100, 100))

        trade_power_frame = sg.Frame("", [
            [trade_power_label],
            [sg.Push(), trade_power_graph_image, sg.Push()]
        ], background_color=constants.DARK_FRAME_BG,
        border_width=0,
        element_justification="center",
        expand_x=True)

        return sg.Column([
            [retained_value_frame, trade_power_frame]
        ], background_color=constants.DARK_FRAME_BG,
        expand_x=True,
        expand_y=True,
        pad=((5, 10), (10, 10)))

    @staticmethod
    def create_countries_table_header():
        """Creates the header for the trade node countries table.
        
        Returns:
            frame (Frame): The frame containing the header icons.
        """
        country_icon = LayoutHelper.create_icon_with_border(
            icon_name="protective_attitude",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        country_header = sg.Frame("", [
            [country_icon]
        ], background_color=constants.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(220, 40))

        merchant_icon = LayoutHelper.create_icon_with_border(
            icon_name="trade_merchant",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        merchant_header = sg.Frame("", [
            [merchant_icon]
        ], background_color=constants.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(110, 40))

        mission_icon = LayoutHelper.create_icon_with_border(
            icon_name="trade_steer",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        mission_header = sg.Frame("", [
            [mission_icon]
        ], background_color=constants.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(176, 40))

        income_icon = LayoutHelper.create_icon_with_border(
            icon_name="development",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        income_header = sg.Frame("", [
            [income_icon]
        ], background_color=constants.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(110, 40))

        ship_trade_power_icon = LayoutHelper.create_icon_with_border(
            icon_name="ship_trade_power",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        ship_trade_power_header = sg.Frame("", [
            [ship_trade_power_icon]
        ], background_color=constants.SECTION_BANNER_BG,
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(176, 40))

        trade_power_icon = LayoutHelper.create_icon_with_border(
            icon_name="province_trade_power",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_power_header = sg.Frame("", [
            [trade_power_icon]
        ], background_color=constants.SECTION_BANNER_BG, 
        border_width=0, 
        element_justification="center", 
        pad=(0, 0), 
        size=(176, 40))  

        icon_row = sg.Column([
            [country_header, 
            merchant_header, 
            mission_header,
            income_header, 
            ship_trade_power_header,
            trade_power_header]
        ], background_color=constants.SECTION_BANNER_BG, 
        pad=(0, 0))

        return sg.Frame("", 
            layout=[[icon_row]], 
            background_color=constants.SECTION_BANNER_BG,
            expand_x=True,
            pad=(0, 0), 
            relief=sg.RELIEF_SOLID)

    @staticmethod
    def create_trade_node_participants_table():
        """Creates the table that will be used to display the trade node's countries.
        
        Returns:
            column (Column): The table and its header packed into a column.
        """
        table_header = TradeNodeLayout.create_countries_table_header()

        table = SortableTable(
            values=[],
            key="-INFO_TRADE_NODE_PARTICIPANTS_TABLE-",
            alternating_row_color=constants.DARK_FRAME_BG,
            background_color=constants.MEDIUM_FRAME_BG,
            auto_size_columns=False,
            col_widths=[20, 10, 16, 10, 16, 16],
            enable_events=True,
            enable_click_events=True,
            font=("Georgia", 12),
            text_color=constants.LIGHT_TEXT,
            headings=["Country", "Merchant", "Merchant Mission", "Income", "Ship Trade Power", "Trade Power"],
            header_background_color=constants.SECTION_BANNER_BG,
            hide_vertical_scroll=False,
            header_relief=sg.RELIEF_SOLID,
            justification="left",            
            num_rows=6,
            pad=(0, 0),
            row_height=28,
            sbar_arrow_color=constants.GOLD_FRAME_UPPER,
            sbar_background_color=constants.RED_BANNER_BG,
            sbar_trough_color=constants.GOLD_FRAME_LOWER,
            sbar_relief=sg.RELIEF_GROOVE,
            sbar_width=5)

        participants_table = sg.Frame("", [
            [table_header],
            [table]
        ], expand_x=True, pad=(0, 0))

        participants_table = LayoutHelper.add_border(
            layout=[[participants_table]],
            borders=[
                (constants.GOLD_FRAME_LOWER, 2, sg.RELIEF_RIDGE),
                (constants.GOLD_FRAME_UPPER, 2, sg.RELIEF_RIDGE)],
            pad=(5, 5))

        return sg.Column([
            [participants_table]
        ], background_color=constants.LIGHT_FRAME_BG,
        pad=(5, 5))

    @staticmethod
    def create_trade_node_info_column():
        """Creates the trade node column section.

        Returns:
            column (Column): The column containing the trade node info.
        """
        trade_node_header_column = TradeNodeLayout.create_trade_node_header()

        trade_node_value_column = TradeNodeLayout.create_trade_node_value_column()
        trade_node_ships_column = TradeNodeLayout.create_trade_node_ships_column()
        trade_center_frame = sg.Frame("", [
            [trade_node_value_column, trade_node_ships_column]
        ], background_color=constants.DARK_FRAME_BG,
        border_width=0,
        pad=(10, 10))

        graphs_column = TradeNodeLayout.create_trade_node_chart_column()

        node_countries_table = TradeNodeLayout.create_trade_node_participants_table()
        trade_node_info_frame = sg.Frame("", [
            [trade_node_header_column],
            [trade_center_frame, graphs_column],
            [node_countries_table],
        ], background_color=constants.LIGHT_FRAME_BG,
        border_width=5,
        expand_x=True,
        expand_y=True,
        key="-TRADE_NODE_INFO_FRAME-",
        pad=(10, 10),
        relief=sg.RELIEF_GROOVE,
        size=(1010, 575))

        return sg.Column([
            [trade_node_info_frame]
        ], background_color=constants.LIGHT_FRAME_BG,
        expand_x=True,
        expand_y=True,
        key="-TRADE_NODE_INFO_COLUMN-",
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
