"""
World Map interaction handler for Europa Universalis IV (EU4) savegame viewing.

This module implements the handling of user interactions with the world map, including 
zooming, panning, and displaying tooltips. It processes user input events such as mouse 
clicks, drags, and scrolls to adjust the map view accordingly.

Key Features:
    - **Panning**: Allows users to drag the map to view different areas.
    - **Zooming**: Enables users to zoom in and out of the map using mouse scroll or buttons.
    - **Hover Information**: Displays contextual information about provinces, areas, and regions 
        when hovering over the map.

The **MapHandler** class works in conjunction with the `MapDisplayer` and canvas to manage 
user interactions and ensure smooth map navigation.
"""



from __future__ import annotations

import tkinter as tk

from PIL import Image
from typing import TYPE_CHECKING
from .models import MapMode
from .models import EUProvince, ProvinceType, EUArea, EURegion
from .utils import MapUtils


if TYPE_CHECKING:
    from . import MapDisplayer



class MapHandler:
    """Handles user interactions for panning and zooming on the map displayed in the 
    `MapDisplayer` instance. Manages the internal state for drag events, zoom operations, 
    and panning animations.

    Attributes:
        displayer (MapDisplayer): The instance of the MapDisplayer responsible for displaying the map.
        tk_canvas (tk.Canvas): The Tkinter canvas on which the map is rendered.
        world_data (EUWorldData): The world data associated with the map.

        disabled (bool): If the handler is disabled, should respond to events or not.

        pan_animation_id (int or None): The identifier for the pan animation, if active.
        cursor_movement (float): The total distance moved by the cursor while dragging.
        dragging (bool): Flag indicating whether the user is currently dragging the map.
        prev_x (int): The previous x-coordinate of the cursor during dragging.
        prev_y (int): The previous y-coordinate of the cursor during dragging.
        start_x (int): The starting x-coordinate of the cursor during dragging.
        start_y (int): The starting y-coordinate of the cursor during dragging.

        scale_factor (float): The factor by which the map scales during zooming operations.
        zooming (bool): Flag indicating whether a zoom operation is currently in progress.
    """
    def __init__(self, displayer: MapDisplayer, tk_canvas: tk.Canvas, disabled: bool=False):
        self.displayer = displayer
        self.world_data = self.displayer.world_data
        self.tk_canvas = tk_canvas

        self.disabled = disabled

        self.pan_animation_id = None
        self.cursor_movement = 0
        self.dragging = False
        self.prev_x = 0
        self.prev_y = 0
        self.start_x = 0
        self.start_y = 0

        self.scale_factor = 1.1
        self.zooming = False

    def bind_events(self):
        """Binds events to `self.tk_canvas` for event handling."""
        self.tk_canvas.bind("<Motion>", self._on_hover)
        self.tk_canvas.bind("<ButtonPress-1>", self._on_press)
        self.tk_canvas.bind("<B1-Motion>", self._on_drag)
        self.tk_canvas.bind("<ButtonRelease-1>", self._on_release)

        self.tk_canvas.bind("<MouseWheel>", self._on_zoom)
        self.tk_canvas.bind("<Button-4>", self._on_zoom)
        self.tk_canvas.bind("<Button-5>", self._on_zoom)

    def clamp_offsets(self, target_offset_x: int=None, target_offset_y: int=None):
        """Restricts the map's position within valid bounds to prevent it from moving out of view.

        This function ensures that the map remains within the visible canvas area 
        by clamping the offsets within the allowed range. If target offsets are provided, 
        it returns the clamped values without modifying the current offsets.

        Args:
            target_offset_x (int, optional): The target x-offset for the map. If None, modifies `displayer.offset_x`.
            target_offset_y (int, optional): The target y-offset for the map. If None, modifies `displayer.offset_y`.

        Returns:
            offsets|None (tuple[int, int]|None): If target offsets are provided, returns the clamped (x, y) offsets. 
                Otherwise, updates `displayer.offset_x` and `displayer.offset_y` directly.
        """
        displayer = self.displayer
        map_width, map_height = displayer.map_image.size
        canvas_width, canvas_height = displayer.canvas_size

        max_x = 0
        min_x = -(map_width - canvas_width)

        max_y = 0
        min_y = -(map_height - canvas_height)

        if target_offset_x is not None and target_offset_y is not None:
            target_offset_x = max(min_x, min(target_offset_x, max_x))
            target_offset_y = max(min_y, min(target_offset_y, max_y))
            return target_offset_x, target_offset_y
        else:
            displayer.offset_x = max(min_x, min(displayer.offset_x, max_x))
            displayer.offset_y = max(min_y, min(displayer.offset_y, max_y))

    def canvas_to_image_coords(self, canvas_x: int|float, canvas_y: int|float):
        """Converts canvas coordinates to image coordinates using the current map scale.
        
        Args:
            canvas_x (int|float): x location on the canvas.
            canvas_y (int|float): y location on the canvas.
        
        Returns:
            coords (tuple[int, int]): The (x, y) image coordinates.
        """
        displayer = self.displayer
        image_x = int((canvas_x - displayer.offset_x) / displayer.map_scale)
        image_y = int((canvas_y - displayer.offset_y) / displayer.map_scale)

        return (image_x, image_y)

    def get_province_at(self, image_x: int, image_y: int):
        """Gets the province at the given `(x, y)` location on the map.
        
        Args:
            image_x (int): x location on the map image.
            image_y (int): y location on the map image.
        
        Returns:
            province (EUProvince|None): The located province.
        """
        for province in self.world_data.provinces.values():
            if (image_x, image_y) in province.pixel_locations:
                return province

        return None

    def go_to_entity_location(self, destination: EUProvince|EUArea|EURegion=None):
        if self.pan_animation_id:
            self.tk_canvas.after_cancel(self.pan_animation_id)

        displayer = self.displayer
        bbox = destination.bounding_box
        if not bbox:
            return

        min_x, max_x, min_y, max_y = bbox
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2

        canvas_width, canvas_height = self.displayer.canvas_size

        target_offset_x = (canvas_width // 2) - (center_x * displayer.map_scale)
        target_offset_y = (canvas_height // 2) - (center_y * displayer.map_scale)
        target_offset_x, target_offset_y = self.clamp_offsets(target_offset_x, target_offset_y)

        def animate_pan(step: int=0, pan_speed: int=10):
            """Smoothly animates the camera to pan toward the target offset.

            Used to navigate towards the selected province, area, or region the user clicked on.

            Args:
                step (int): The current animation step (unused but can be for progressive movement).
                pan_speed (int): The delay in milliseconds between animation frames.
            """
            dx = target_offset_x - displayer.offset_x
            dy = target_offset_y - displayer.offset_y

            if abs(dx) < 1 and abs(dy) < 1:
                displayer.offset_x = target_offset_x
                displayer.offset_y = target_offset_y
                self.clamp_offsets()

                return self.tk_canvas.coords(displayer.image_id, target_offset_x, target_offset_y)

            displayer.offset_x += dx * 0.1
            displayer.offset_y += dy * 0.1

            self.tk_canvas.coords(displayer.image_id, displayer.offset_x, displayer.offset_y)

            self.pan_animation_id = self.tk_canvas.after(pan_speed, animate_pan)

        animate_pan()

    def _on_hover(self, event: tk.Event):
        """Handles mouse hover events and updates the UI with province/area/region information."""
        if self.disabled:
            return

        displayer = self.displayer
        canvas_x = event.x
        canvas_y = event.y

        image_x, image_y = self.canvas_to_image_coords(canvas_x, canvas_y)
        if not (0 <= image_x < displayer.original_map.width or
                0 <= image_y < displayer.original_map.height):
            return

        province = self.get_province_at(image_x, image_y)
        if not province:
            return

        area = displayer.world_data.province_to_area.get(province.province_id)
        if not area:
            return

        map_mode = displayer.painter.map_mode
        if province.province_type == ProvinceType.WASTELAND:
            info = f"The wasteland of {province.name}"
        elif area.area_id == "lake_area":
            info = f"The waters of {province.name}"
        else:
            match(map_mode):
                case MapMode.POLITICAL:
                    if province.province_type == ProvinceType.SEA:
                        info = f"The waters of {province.name}"
                    else:
                        if province.province_type == ProvinceType.NATIVE:
                            info = f"The native lands of {province.name}"
                        else:
                            province_owner = province.owner_name
                            info = f"The province of {province.name} ({province_owner})"

                case MapMode.AREA:
                    if area.is_sea_area:
                        info = f"The waters of {area.name}"
                    else:
                        info = f"The province of {province.name} ({area.name})"

                case MapMode.REGION:
                    region = displayer.world_data.province_to_region.get(province.province_id)
                    if not region:
                        return

                    if region.is_sea_region:
                        info = f"The waters of {region.name}"
                    else:
                        info = f"The province of {province.name} ({region.name})"

                case MapMode.DEVELOPMENT:
                    if province.province_type == ProvinceType.SEA:
                        info = f"The waters of {province.name}"
                    else:
                        info = f"The province of {province.name} (Total Development: {province.development})"

                case MapMode.TRADE:
                    if province.province_type == ProvinceType.SEA:
                        info = f"The waters of {province.name}"
                    else:
                        trade_node = displayer.world_data.province_to_trade_node.get(province.province_id)
                        if not trade_node:
                            return

                        info = f"The province of {province.name} belogns to {trade_node.name}. It provides {province.trade_power} trade power to the node."

                case MapMode.CULTURE:
                    if province.province_type == ProvinceType.SEA:
                        info = f"The waters of {province.name}"
                    else:
                        province_culture = province.culture
                        info = (
                            f"The province of {province.name} " 
                            f"(Culture: {MapUtils.format_name(province_culture) if province_culture else 'No Culture'})")

                case MapMode.RELIGION:
                    if province.province_type == ProvinceType.SEA:
                        info = f"The waters of {province.name}"
                    else:
                        province_religion = province.religion
                        info = (
                            f"The province of {province.name} " 
                            f"(Religion: {MapUtils.format_name(province_religion) if province_religion else 'No Religion'})")

        if not info:
            return

        displayer.window["-MULTILINE-"].update(info)

    def _on_press(self, event: tk.Event):
        """Updates the handler attribtues and is triggered the left-mouse button is pressed."""
        if self.disabled:
            return

        self.dragging = True
        self.prev_x = event.x
        self.prev_y = event.y
        self.start_x = event.x
        self.start_y = event.y
        self.cursor_movement = 0

    def _on_drag(self, event: tk.Event):
        """Pans the image while the left mouse button is held down.
        
        Triggered whenever the cursor moves while the left mouse button is pressed.
        Continuously updates the canvas offsets to move the image accordingly, ensuring 
        that panning remains within the allowed bounds.
        """
        if self.disabled:
            return

        displayer = self.displayer

        if self.dragging:
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y

            self.cursor_movement += (dx ** 2 + dy ** 2) ** 0.5
            self.displayer.offset_x += dx
            self.displayer.offset_y += dy
            self.clamp_offsets()

            self.tk_canvas.coords(displayer.image_id, displayer.offset_x, displayer.offset_y)

            self.prev_x = event.x
            self.prev_y = event.y

    def _on_release(self, event: tk.Event):
        """Handles mouse release events.

        Updates handler attributes when the left mouse button is released.
        If the cursor did not move significantly, the release is registered as a click event, 
        triggering the `on_click` method.
        """
        if self.disabled:
            return

        self.dragging = False

        cursor_move_threshold = 1
        if self.cursor_movement < cursor_move_threshold:
            self._on_click(event)

    def _on_click(self, event: tk.Event):
        """Handles click events on the map canvas.
        
        - Determines the clicked location on the canvas and converts it to map coordinates.
        - Identifies the province at the clicked location."""
        if self.disabled:
            return

        displayer = self.displayer
        canvas_x = event.x
        canvas_y = event.y

        image_x, image_y = self.canvas_to_image_coords(canvas_x, canvas_y)
        if not (0 <= image_x < displayer.original_map.width or
                0 <= image_y < displayer.original_map.height):
            return

        province = self.get_province_at(image_x, image_y)
        if not province:
            return

        if (province.province_type == ProvinceType.WASTELAND or
            province.province_type == ProvinceType.SEA):
            return

        map_mode = self.displayer.painter.map_mode
        match(map_mode):
            case MapMode.POLITICAL:
                selected_item = province

            case MapMode.AREA:
                selected_item = self.world_data.province_to_area.get(province.province_id)
                if not selected_item:
                    return

            case MapMode.REGION:
                selected_item = self.world_data.province_to_region.get(province.province_id)
                if not selected_item:
                    return

            case MapMode.DEVELOPMENT:
                selected_item = province

            case MapMode.TRADE:
                selected_item = self.world_data.province_to_trade_node.get(province.province_id)
                if not selected_item:
                    return

            case MapMode.CULTURE:
                selected_item = province

            case MapMode.RELIGION:
                selected_item = province

        self.displayer.window = self.displayer.update_details_from_selected_item(selected_item)

    def _on_zoom(self, event: tk.Event):
        """Handles zoom events triggered by the mouse scroll or trackpad gestures.

        Determines the zoom direction based on the event data and calls `zoom_map` 
        with the appropriate zoom direction.
        """
        if self.disabled:
            return

        cursor_x, cursor_y = event.x, event.y

        if event.delta > 0 or event.num == 4:
            self._zoom_map(cursor_x, cursor_y, zoom_in=True)
        elif event.delta < 0 or event.num == 5:
            self._zoom_map(cursor_x, cursor_y, zoom_in=False)

    def _zoom_map(self, cursor_x: float, cursor_y: float, zoom_in: bool=True):
        """Zooms in or out on the map while keeping the cursor position as the focal point.

        This function scales the map image based on the zoom factor, updates offsets 
        to maintain the cursor position in place, and ensures the new scale remains 
        within allowed limits.

        Args:
            cursor_x (float): The x-coordinate of the cursor on the canvas.
            cursor_y (float): The y-coordinate of the cursor on the canvas.
            zoom_in (bool, optional): Determines whether to zoom in (True) or out (False). 
                Defaults to True.
        """
        if self.zooming or self.disabled:
            return

        displayer = self.displayer
        canvas_width, canvas_height = displayer.canvas_size

        if zoom_in and displayer.map_scale >= displayer.max_scale:
            self.zooming = False
            return

        if not zoom_in and displayer.map_scale <= displayer.min_scale:
            self.zooming = False
            return

        self.zooming = True
        new_scale = displayer.map_scale * self.scale_factor if zoom_in else displayer.map_scale / self.scale_factor
        new_scale = min(displayer.max_scale, max(displayer.min_scale, new_scale))

        scaled_width = int(displayer.original_map.width * new_scale)
        scaled_height = int(displayer.original_map.height * new_scale)

        map_cursor_x = (cursor_x - displayer.offset_x) / displayer.map_scale
        map_cursor_y = (cursor_y - displayer.offset_y) / displayer.map_scale

        new_offset_x = cursor_x - map_cursor_x * new_scale
        new_offset_y = cursor_y - map_cursor_y * new_scale

        new_offset_x = min(0, max(canvas_width - scaled_width, new_offset_x))
        new_offset_y = min(0, max(canvas_height - scaled_height, new_offset_y))

        displayer.offset_x = new_offset_x
        displayer.offset_y = new_offset_y
        displayer.map_scale = new_scale
        self.clamp_offsets()

        self.displayer.map_image = self.displayer.original_map.resize(
            (scaled_width, scaled_height), Image.Resampling.LANCZOS)
        self.displayer.update_canvas()

        self.tk_canvas.after(50, lambda: setattr(self, 'zooming', False))
