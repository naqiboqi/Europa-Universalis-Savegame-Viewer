import FreeSimpleGUI as fsg
import io

from PIL import Image
from . import MapPainter
from .models import MapMode



class MapDisplayer:
    def __init__(self, painter: MapPainter):
        self.painter = painter
        
    def image_to_bytes(self, image: Image.Image):
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            return output.getvalue()

    def display_map(self):
        fsg.theme("DarkBlue")

        map_image = self.painter.draw_map()
        max_width, max_height = 1200, 800
        
        scale = min(max_width / map_image.width, max_height / map_image.height)
        new_size = (int(map_image.width * scale), int(map_image.height * scale))
        map_image = map_image.resize(new_size, Image.Resampling.LANCZOS)
        
        map_bytes = self.image_to_bytes(map_image)

        layout = [
            [fsg.Image(data=map_bytes, key="-IMAGE-")],
            [fsg.Button(mode.value.capitalize(), key=mode.value.capitalize()) for mode in self.painter.map_modes]
        ]

        print("Loading map....")
        window = fsg.Window("EU Map Viewer", layout, finalize=True)
        window.move_to_center()

        while True:
            event, values = window.read(timeout=20)

            if event in (fsg.WIN_CLOSED, "Exit"):
                break

            if event in {mode.value.capitalize() for mode in self.map_modes}:
                self.painter.map_mode = MapMode[event.upper()]
                image = self.image_to_bytes(self.painter.draw_map().resize(new_size, Image.Resampling.LANCZOS))
                window["-IMAGE-"].update(data=image)

        window.close()