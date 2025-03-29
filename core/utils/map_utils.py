"""
Utility functions for map generation, formatting, and visualization.

This module provides various utility functions to assist with the generation, 
formatting, and display of map-related elements, including name formatting 
and color generation.

Methods:
    - format_name(name: str) -> str: Converts an internal name format (e.g., 'cosmopolitan_french') 
      into a properly capitalized display name (e.g., 'Cosmopolitan French').
    - seed_color(name: str) -> tuple[int, int, int]: Generates a consistent RGB color 
      based on the hash of a given name, ensuring unique and distinguishable colors.
"""


import colorsys
import hashlib
from random import Random



class MapUtils:
    """Utility class for map-related formatting and visualization.

    This class contains static methods that assist with map-related tasks, 
    such as formatting internal name identifiers into human-readable names 
    and generating colors based on names.

    Methods:
        format_name(name: str) -> str:
            Converts an internal identifier format into a properly capitalized 
            display name.
        
        seed_color(name: str) -> tuple[int, int, int]:
            Generates a unique color based on the given name by hashing 
            the input and mapping it to an RGB color.
    """
    
    @staticmethod
    def format_name(name: str):
        """Converts an internal name format (e.g., 'cosmopolitan_french') 
        into a properly capitalized display name (e.g., 'Cosmopolitan French').

        Args:
            name (str): The internal name to format.

        Returns:
            str: The formatted name.
        """
        if not name:
            return ""

        words = name.split("_")
        return " ".join(word.capitalize() for word in words)

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
