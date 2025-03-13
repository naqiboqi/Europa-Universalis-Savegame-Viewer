import FreeSimpleGUI as sg
import io
import tkinter as tk

from PIL import Image, ImageTk
from . import MapPainter
from .models import MapMode



class MapDisplayer:
    def __init__(self, painter: MapPainter):
        self.painter = painter

        self.canvas_size = ()
        self.image_id = None
        self.map_image = None
        self.tk_image = None

        self.dragging = False
        self.max_scale = 5.0
        self.map_scale = 1.0
        self.min_scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.prev_x = 0
        self.prev_y = 0
        self.scale_factor = 1.1

    def image_to_bytes(self, image: Image.Image):
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            return output.getvalue()

    def image_to_tkimage(self, image: Image.Image):
        return ImageTk.PhotoImage(image)

    def scale_image_to_fit(self, map_image: Image.Image):
        width, height = map_image.size
        canvas_width, canvas_height = self.canvas_size
        self.map_scale = min(canvas_width / width, canvas_height / height)
        self.min_scale = self.map_scale

        return map_image.resize((self.canvas_size), Image.Resampling.LANCZOS)

    def clamp_offsets(self):
        map_width, map_height = self.map_image.size
        
        max_x = 0
        min_x = -(map_width - self.canvas_size[0])
        
        max_y = 0
        min_y = -(map_height - self.canvas_size[1])
        
        self.offset_x = max(min_x, min(self.offset_x, max_x))
        self.offset_y = max(min_y, min(self.offset_y, max_y))

    def on_press(self, event: tk.Event):
        self.dragging = True
        self.prev_x = event.x
        self.prev_y = event.y

    def on_drag(self, event: tk.Event):
        if self.dragging:
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y

            self.offset_x += dx
            self.offset_y += dy
            self.clamp_offsets()

            event.widget.coords(self.image_id, self.offset_x, self.offset_y)
            self.prev_x = event.x
            self.prev_y = event.y

    def on_release(self, event: tk.Event):
        self.dragging = False

    def zoom_map(self, cursor_loc: tuple[int, int], zoom_in: bool=True):
        cursor_x, cursor_y = cursor_loc 
        canvas_width, canvas_height = self.canvas_size

        if zoom_in and self.map_scale >= self.max_scale:
            return self.map_image

        if not zoom_in and self.map_scale <= self.min_scale:
            return self.map_image

        new_scale = self.map_scale * self.scale_factor if zoom_in else self.map_scale / self.scale_factor
        new_scale = min(self.max_scale, max(self.min_scale, new_scale))

        scaled_width = int(self.original_map.width * new_scale)
        scaled_height = int(self.original_map.height * new_scale)

        map_cursor_x = (cursor_x - self.offset_x) / self.map_scale
        map_cursor_y = (cursor_y - self.offset_y) / self.map_scale

        new_offset_x = cursor_x - map_cursor_x * new_scale
        new_offset_y = cursor_y - map_cursor_y * new_scale

        new_offset_x = min(0, max(canvas_width - scaled_width, new_offset_x))
        new_offset_y = min(0, max(canvas_height - scaled_height, new_offset_y))

        self.offset_x = new_offset_x
        self.offset_y = new_offset_y
        self.map_scale = new_scale

        return self.original_map.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

    def on_zoom(self, event: tk.Event):
        cursor_x, cursor_y = event.x, event.y

        if event.delta > 0 or event.num == 4:
            self.map_image = self.zoom_map((cursor_x, cursor_y), zoom_in=True)
        elif event.delta < 0 or event.num == 5:
            self.map_image = self.zoom_map((cursor_x, cursor_y), zoom_in=False)

        self.tk_image = self.image_to_tkimage(self.map_image)
        event.widget.itemconfig(self.image_id, image=self.tk_image)
        self.clamp_offsets()

        event.widget.coords(self.image_id, self.offset_x, self.offset_y)

    def display_map(self):
        sg.theme("DarkBlue")

        self.original_map = self.painter.draw_map()
        map_width, map_height = self.original_map.size

        canvas_width = 800
        canvas_height = int(canvas_width * (map_height / map_width))
        self.canvas_size = (canvas_width, canvas_height)

        self.map_image = self.scale_image_to_fit(self.original_map)

        layout = [[sg.Canvas(background_color="black", size=self.canvas_size, key="-CANVAS-"), sg.Button("Exit")]]

        window = sg.Window("EU4 Map Viewer", layout, finalize=True, return_keyboard_events=True)
        window.move_to_center()

        canvas = window["-CANVAS-"]
        tk_canvas: tk.Canvas = canvas.TKCanvas

        self.tk_image = self.image_to_tkimage(self.map_image)
        self.image_id = tk_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        tk_canvas.bind("<ButtonPress-1>", self.on_press)
        tk_canvas.bind("<B1-Motion>", self.on_drag)
        tk_canvas.bind("<ButtonRelease-1>", self.on_release)

        tk_canvas.bind("<MouseWheel>", self.on_zoom)
        tk_canvas.bind("<Button-4>", self.on_zoom)
        tk_canvas.bind("<Button-5>", self.on_zoom)

        window.finalize()

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "Exit"):
                break

        window.close()