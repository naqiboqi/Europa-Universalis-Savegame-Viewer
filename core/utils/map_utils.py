import colorsys
import hashlib
from random import Random



class MapUtils:
    @staticmethod
    def canvas_to_image_coords(
        canvas_x: int|float, 
        canvas_y: int|float,
        offset_x: int|float, 
        offset_y: int|float, 
        scale_x: int|float, 
        scale_y: int|float):

        image_x = (canvas_x - offset_x) / scale_x
        image_y = (canvas_y - offset_y) / scale_y
        return image_x, image_y

    @staticmethod
    def clamp(value: int|float, min_value: int, max_value: int):
        return max(min(value, max_value), min_value)

    @staticmethod
    def get_bounded_offset(offset: int, image_dim: int, canvas_dim: int):
        if image_dim < canvas_dim:
            return (canvas_dim - image_dim) // 2
        return MapUtils.clamp(offset, canvas_dim - image_dim, 0)

    @staticmethod
    def seed_color(name: str):
        hash_value = int(hashlib.sha256(name.encode("utf-8")).hexdigest(), 16)

        random = Random(hash_value)

        hue = random.uniform(0, 1)
        saturation = random.uniform(0.4, 0.7)
        brightness = random.uniform(0.75, 0.85)

        r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
        return (int(r * 255), int(g * 255), int(b * 255))
