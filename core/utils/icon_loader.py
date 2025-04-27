"""
Utility functions for image loading and caching.

This module provides a singleton-based utility class for loading 
and caching image paths, used for UI or map assets.

Classes:
    - IconLoader: A singleton class responsible for retrieving and caching 
        icon file paths from a specified directory.

Methods:
    - get_icon(icon_name: str) -> str: Retrieves the absolute path of an 
        icon, caching it for future use. If the icon is not found, returns a 
        default placeholder image.
"""



import os



class IconLoader:
    """Singleton class for image loading and caching.

    This class manages the retrieval of icons from a specified folder, ensuring 
    that once an icon is located, its file path is cached to improve performance. 
    If an icon cannot be found, a default placeholder image is used instead.

    Attributes:
        icons_folder (str): The absolute path to the directory containing icons.
        cache (dict): A dictionary for caching loaded icon paths.
        default (str): The path to the default placeholder image.
    """
    _instance = None
    """The singleton instance for the loader."""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IconLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, icons_folder: str=None):
        if not self._initialized:
            if icons_folder is None:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                icons_folder = os.path.join(base_dir, "../../data/icons/trade_good_icons") 

            self.icons_folder = os.path.abspath(icons_folder)
            self.cache = {}
            self.default = os.path.join(self.icons_folder, "Unknown.png")
            self._initialized = True

    def get_icon(self, icon_name: str, extension: str=".png"):
        """Retrieves the absolute path of the requested icon, caching it for future use.

        If the icon is not found in the designated folder, the method returns 
        a default placeholder image.

        Args:
            icon_name (str): The name of the icon file (without the extension).
            extension (str): The extenison of the icon file (".png", ".jpeg", .etc). Is `.png` by default.

        Returns:
            str: The absolute path to the requested icon, or the default image 
                if the icon is not found.
        """
        if not icon_name.lower().endswith(extension):
            icon_name += extension

        if icon_name in self.cache:
            return self.cache[icon_name]

        if not os.path.exists(self.icons_folder):
            print(f"Warning: Icons folder '{self.icons_folder}' was not found.")
            return self.default

        for root, _, files in os.walk(self.icons_folder):
            if icon_name in files:
                icon_path = os.path.abspath(os.path.join(root, icon_name))
                self.cache[icon_name] = icon_path
                return icon_path
        else:
            self.cache[icon_name] = self.default
            return self.default
