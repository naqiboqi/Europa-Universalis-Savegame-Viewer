"""
Utility functions for map generation and drawing.
"""



import colorsys
import hashlib
from random import Random



class MapUtils:
    """Utility class for map drawing and generation.

    This class contains static methods that assist with map-related tasks, such as generating 
    colors based on names. It is primarily used for map creation and customizing visuals 
    for map-related entities.

    Methods:
        - **seed_color(name: str)**: Generates a color based on the provided name by hashing 
            the name and using the resulting hash to generate a unique hue, saturation, and brightness.
            Returns an RGB color tuple.
    """

    @staticmethod
    def seed_color(name: str):
        """Generates a color based on the provided name.

        Hashes the input `name` string and uses the resulting hash 
        to produce a unique color, with a random hue, saturation, and brightness.

        Args:
            name (str): The name used for generating the color.

        Returns:
            color (tuple[int, int, int]): An RGB color represented as a tuple of integers (r, g, b).
        """
        hash_value = int(hashlib.sha256(name.encode("utf-8")).hexdigest(), 16)

        random = Random(hash_value)

        hue = random.uniform(0, 1)
        saturation = random.uniform(0.4, 0.7)
        brightness = random.uniform(0.75, 0.85)

        r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
        return (int(r * 255), int(g * 255), int(b * 255))
