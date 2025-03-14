import colorsys
import hashlib
from random import Random



class MapUtils:

    @staticmethod
    def seed_color(name: str):
        hash_value = int(hashlib.sha256(name.encode("utf-8")).hexdigest(), 16)

        random = Random(hash_value)

        hue = random.uniform(0, 1)
        saturation = random.uniform(0.4, 0.7)
        brightness = random.uniform(0.75, 0.85)

        r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
        return (int(r * 255), int(g * 255), int(b * 255))
