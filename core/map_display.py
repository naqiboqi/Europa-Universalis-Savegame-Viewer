import FreeSimpleGUI as fsg
import io

from PIL import Image, ImageTk
from . import MapPainter
from .models import MapMode



class MapDisplayer:
    def __init__(self, painter: MapPainter):
        self.painter = painter

        self.pan_x = 0
        self.pan_y = 0
        self.dragging = False
        self.start_x = 0
        self.start_y = 0

    def image_to_bytes(self, image: Image.Image):
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            return output.getvalue()

    def display_map(self):
        fsg.theme("DarkBlue")

        map_image = self.painter.draw_map()
        max_width, max_height = 1200, 800