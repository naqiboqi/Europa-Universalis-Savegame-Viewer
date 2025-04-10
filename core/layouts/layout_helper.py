"""
Helper utilities for building consistent UI layouts in the Europa Universalis UI.

This module contains reusable layout-building functions and utilities shared across 
province, area, and region layouts. It provides common components such as headers, 
spacers, colored boxes, and text formatting.

Classes:
    - **LayoutHelper**: A static utility class with helper methods for constructing UI elements.
"""


import FreeSimpleGUI as sg

from . import constants
from ..utils import IconLoader


icon_loader = IconLoader()


class LayoutHelper:
    """Provides static methods to assist in constructing standardized UI components 
    such as framed images, text, and formatted rows for the PySimpleGUI interface.
    """

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
        return LayoutHelper.add_border(layout=[[image]], borders=borders, pad=border_pad)

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
        pad: tuple[int, int]|tuple[tuple[int, int], tuple[int, int]]=None):
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
            pad: (tuple[int, int]|tuple[tuple[int, int], tuple[int, int]]): The amount of `(x, y)` or `((left/right), (top/bottom))` padding in pixels. 
        
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
    def create_development_info_frame(name: str):
        """Creates the development frame section for a given entity.

        Returns:
            frame (Frame): The frame containing the development info.
        """
        development_icon= LayoutHelper.create_icon_with_border(
            icon_name="development",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        total_dev_value = sg.Text(
            "",
            key=f"-INFO_{name}_TOTAL_DEV-",
            background_color=constants.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),   
            size=(5, 1),
            text_color=constants.GREEN_TEXT)

        total_dev_frame = sg.Frame("", [
            [development_icon, total_dev_value]
        ], background_color=constants.SUNK_FRAME_BG, 
        border_width=3, 
        pad=(10, 0),
        relief=sg.RELIEF_FLAT)

        tax_icon = LayoutHelper.create_icon_with_border(
            icon_name="base_tax",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        tax_value = sg.Text(
            "",
            key=f"-INFO_{name}_BASE_TAX-",
            background_color=constants.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),   
            size=(4, 1),
            text_color=constants.GREEN_TEXT)
        tax_frame = sg.Frame("", [
            [tax_icon, tax_value]
        ], background_color=constants.SUNK_FRAME_BG, 
        border_width=2, 
        pad=(5, 0),
        relief=sg.RELIEF_FLAT)

        production_icon = LayoutHelper.create_icon_with_border(
            icon_name="base_production",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        production_value = sg.Text(
            "",
            key=f"-INFO_{name}_BASE_PRODUCTION-",
            background_color=constants.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            size=(4, 1),
            text_color=constants.GREEN_TEXT)
        production_frame = sg.Frame("", [
            [production_icon, production_value]
        ], background_color=constants.SUNK_FRAME_BG, 
        border_width=2,
        pad=(5, 0),
        relief=sg.RELIEF_FLAT)

        manpower_icon = LayoutHelper.create_icon_with_border(
            icon_name="base_manpower",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        manpower_value = sg.Text(
            "",
            key=f"-INFO_{name}_BASE_MANPOWER-",
            background_color=constants.SUNK_FRAME_BG,
            font=("Georgia", 12, "bold"),
            size=(4, 1),
            text_color=constants.GREEN_TEXT)
        manpower_frame = sg.Frame("", [
            [manpower_icon, manpower_value]
        ], background_color=constants.SUNK_FRAME_BG, 
        border_width=2, 
        pad=(5, 0),
        relief=sg.RELIEF_FLAT)

        return sg.Frame("", [
            [total_dev_frame, tax_frame, production_frame, manpower_frame]
        ], background_color=constants.DARK_FRAME_BG, 
        border_width=3, 
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN, 
        title_color=constants.LIGHT_TEXT)

    @staticmethod
    def create_trade_column(name: str):
        trade_power_icon = LayoutHelper.create_icon_with_border(
            icon_name="trade_power",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        trade_power_label, trade_power_value = LayoutHelper.create_text_with_inline_label(
            "Trade Power",
            text_key=f"-INFO_{name}_TRADE_POWER-",
            label_colors=(constants.LIGHT_TEXT, constants.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(10, 1),
            expand_x=True)

        trade_power_column = sg.Column([
            [trade_power_label, trade_power_icon, trade_power_value]
        ], background_color=constants.MEDIUM_FRAME_BG,
        pad=(0, 0))

        goods_produced_icon = LayoutHelper.create_icon_with_border(
            icon_name="goods_produced",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        goods_produced_label, goods_produced_value = LayoutHelper.create_text_with_inline_label(
            "Goods Produced",
            text_key=f"-INFO_{name}_GOODS_PRODUCED-", 
            label_colors=(constants.LIGHT_TEXT, constants.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(10, 1),
            expand_x=True)

        goods_produced_column = sg.Column([
            [goods_produced_label, goods_produced_icon, goods_produced_value]
        ], background_color=constants.MEDIUM_FRAME_BG,
        pad=(0, 0))

        dominant_good_icon = LayoutHelper.create_icon_with_border (
            icon_name="warehouse",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        dominant_good_label, dominant_good_value = LayoutHelper.create_text_with_inline_label(
            "Dominant Trade Good",
            text_key=f"-INFO_{name}_DOMINANT_TRADE_GOOD-",
            label_colors=(constants.LIGHT_TEXT, constants.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(15, 1),
            expand_x=True)  

        dominant_good_column = sg.Column([
            [dominant_good_label, dominant_good_icon, dominant_good_value]
        ], background_color=constants.MEDIUM_FRAME_BG,
        pad=(0, 0))

        income_info_frame = sg.Frame("", [
            [trade_power_column, goods_produced_column, dominant_good_column]
        ], background_color=constants.DARK_FRAME_BG,
        border_width=3,
        expand_x=True,
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        return sg.Column([
            [income_info_frame]
        ], background_color=constants.LIGHT_FRAME_BG,
        pad=((10, 10), (0, 10)),
        vertical_alignment="top")

    @staticmethod
    def create_income_column(name: str):
        total_income_icon = LayoutHelper.create_icon_with_border(
            icon_name="total_income",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        total_income_label, total_income_value = LayoutHelper.create_text_with_inline_label(
            "Total Income",
            text_key=f"-INFO_{name}_INCOME-",
            label_colors=(constants.LIGHT_TEXT, constants.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(10, 1),
            expand_x=True)

        total_income_column = sg.Column([
            [total_income_label, total_income_icon, total_income_value]
        ], background_color=constants.MEDIUM_FRAME_BG,
        pad=(0, 0))

        tax_income_icon = LayoutHelper.create_icon_with_border(
            icon_name="income",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        tax_income_label, tax_income_value = LayoutHelper.create_text_with_inline_label(
            "Tax",
            text_key=f"-INFO_{name}_TAX_INCOME-", 
            label_colors=(constants.LIGHT_TEXT, constants.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(10, 1),
            expand_x=True)

        tax_income_column = sg.Column([
            [tax_income_label, tax_income_icon, tax_income_value]
        ], background_color=constants.MEDIUM_FRAME_BG,
        pad=(0, 0))

        goods_income_icon = LayoutHelper.create_icon_with_border(
            icon_name="trade_value_income",
            borders=[(constants.GOLD_FRAME_LOWER, 1, sg.RELIEF_RIDGE)],
            border_pad=(5, 5),
            image_size=(28, 28))
        goods_income_label, goods_income_value = LayoutHelper.create_text_with_inline_label(
            "Production",
            text_key=f"-INFO_{name}_PRODUCTION_INCOME-",
            label_colors=(constants.LIGHT_TEXT, constants.MEDIUM_FRAME_BG),
            justification="center",
            text_colors=(constants.LIGHT_TEXT, constants.SUNK_FRAME_BG),
            text_field_size=(15, 1),
            expand_x=True)  

        goods_income_column = sg.Column([
            [goods_income_label, goods_income_icon, goods_income_value]
        ], background_color=constants.MEDIUM_FRAME_BG,
        pad=(0, 0))

        income_info_frame = sg.Frame("", [
            [total_income_column, tax_income_column, goods_income_column]
        ], background_color=constants.DARK_FRAME_BG,
        border_width=3,
        expand_x=True,
        pad=(5, 5), 
        relief=sg.RELIEF_SUNKEN,
        vertical_alignment="top")

        return sg.Column([
            [income_info_frame]
        ], background_color=constants.LIGHT_FRAME_BG,
        pad=((10, 10), (15, 10)),
        vertical_alignment="top")
